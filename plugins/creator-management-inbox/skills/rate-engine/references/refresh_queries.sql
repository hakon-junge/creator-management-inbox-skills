-- ================================================================
-- RATE-ENGINE - REFRESH QUERIES
--
-- Five queries that rebuild the entire rate engine from the warehouse. No
-- manual exports, no spreadsheets, no "I remember what we paid".
--
-- Dialect: written for a BigQuery-style warehouse (APPROX_QUANTILES, QUALIFY,
-- MAX_BY, SAFE_DIVIDE, TO_JSON_STRING). On Snowflake/Redshift the shape holds
-- but you will swap those for the local equivalents. Keep the comments when
-- you port the dialect - they are the part that took the longest to learn.
--
-- ---------------------------------------------------------------- TOKENS
-- Fill these from your profile (data-sources.md) before running. Every one of them is a
-- company fact, which is exactly why none of them is hardcoded here.
--
--   {{WAREHOUSE_PROJECT}}          project / database qualifier
--   {{TBL_POSTS}}                  one row per creator post, with creator attributes
--   {{TBL_CAMPAIGN_DAILY}}         one row per campaign per day - the outcome table
--   {{TBL_BOOST_DAILY}}            one row per boosted post per day
--   {{TBL_CRM_POST_REPLICA}}       raw CRM post-object replica (deliverable type lives here)
--
--   {{COL_POST_ID}}                post primary key, shared by posts and the CRM replica
--   {{COL_HANDLE}}                 social handle
--   {{COL_CREATOR_NAME}}           creator display name - the ONLY key promo data joins on
--   {{COL_NICHE}}                  creator category/niche
--   {{COL_COUNTRY}}                AUDIENCE country (not creator residence - see below)
--   {{COL_PLATFORM}}               social channel
--   {{COL_FEE}}                    fee paid for the post
--   {{COL_VIEWS}}                  actual organic views
--   {{COL_GOLIVE}}                 publish date
--   {{COL_LEAD_STATUS}}            CRM lead status
--   {{COL_OWNER}}                  record owner
--   {{COL_DEAL_STAGE}}             deal stage label
--   {{COL_AFFILIATE_RATE}}         affiliate commission rate, if any
--   {{COL_POST_UTM}}               the post's tracking campaign string
--   {{COL_DELIVERABLE_TYPE}}       CRM dropdown: what was actually delivered
--   {{COL_CAMPAIGN}}               the CLEANED campaign string on the outcome table
--   {{COL_REPORT_DATE}}            outcome row date
--   {{COL_NEW_CONVERSIONS}}        new conversions that day
--   {{COL_VALUE_ADDED}}            value added that day - define this precisely, see below
--   {{COL_DAILY_REVENUE}}          cash revenue that day
--   {{COL_BOOST_SPEND}}            paid amplification spend
--
--   {{CAMPAIGN_PREFIX_PROMO}}      prefix marking promo-code campaigns, e.g. 'promo_'
--   {{CAMPAIGN_PREFIX_AFFILIATE}}  prefix marking affiliate-network campaigns
--   {{PAYBACK_WINDOW}}             attribution window in days
--   {{REGIME_START_DATE}}          first day of the "current regime" period
--   {{GEO_TIER_1}} / _2 / _3       country lists for the tier CASE
--
-- ---------------------------------------------------------- BEFORE YOU RUN
--   * Whatever access path you use ({{WAREHOUSE_QUERY_TOOL}}, a notebook, the
--     console), follow your company's audit convention first. If there is a
--     "record the request" step, do it - a read-only query still shows up in
--     somebody's cost report and you want your name attached to a reason.
--   * Dry-run gate: check the bytes scanned before you execute. The posts x
--     campaign-daily join is the expensive one.
--   * Some SQL gateways block `SELECT *` (even inside CTEs) and literal
--     semicolons inside string literals. If yours does, name every column and
--     use CHR(59) where you need a semicolon - the SPLIT in the base block
--     below does exactly that, because multi-valued CRM fields are often
--     semicolon-delimited.
--   * Row caps: if your gateway caps results (500 rows is common), Q5 will not
--     fit in one pass. Run it in halves on the handle range and merge. Split
--     further if a half comes back at exactly the cap - that means truncation,
--     not a coincidence.
--
-- ----------------------------------------------------- THE TRAPS THAT COST
-- Read these before trusting a single number out of this file.
--
--  1. JOIN KEY posts -> outcomes. Join on the RAW
--     LOWER(TRIM({{COL_POST_UTM}})) on BOTH sides. The outcome table usually
--     also carries a cleaned/normalised campaign string; it does NOT match the
--     raw value and joining on it silently drops a large share of posts. Check
--     the join rate every refresh and record it in meta.corpus.utm_join_rate.
--     A join rate that drops between refreshes means the tracking convention
--     changed, and every value rate is wrong until you fix it.
--  2. PROMO CODES DON'T HAVE A POST. Promo-code conversions arrive attributed
--     to a creator, not a post. Allocating them to posts is a modelling choice:
--     here they are spread evenly across whatever posts of that creator are
--     inside the window on that day (promo_cover / promo_alloc below). Without
--     the divide-by-n_posts step you count the same conversion once per post
--     and a creator with four posts in-window looks four times as good.
--  3. DOUBLE COUNTING affiliate. Affiliate campaigns must be excluded from the
--     link-attributed outcome CTE or the same revenue is paid for twice - once
--     in the flat fee's EV and once as commission.
--  4. BOOSTED POSTS ARE NOT ORGANIC. Any post whose window overlaps paid
--     amplification of the same creator is excluded from value rates. Leave it
--     in and you learn that buying reach makes creators convert better, which
--     is true and useless.
--  5. MATURITY. A post inside the payback window has not finished earning.
--     Including immature posts drags every rate down and does it worst on the
--     most recent period, which is the period you most need to read correctly.
--  6. VIEWS FLOOR. Posts under ~300 views produce absurd CPMs and absurd
--     value-per-1k rates. They are noise in both directions; floor them out.
--  7. AUDIENCE GEO, NOT CREATOR GEO. The tier CASE must run on where the
--     audience is, not where the creator lives. A creator in a T1 country with
--     a T3 audience converts like T3, every time.
--  8. {{COL_VALUE_ADDED}} IS AMBIGUOUS. "Predicted lifetime value", "realized
--     value to date" and "cash collected" are three different columns at most
--     companies and the walk-away ceiling changes by a multiple depending on
--     which you sum. Pin the definition in data-sources.md before you
--     quote anything derived from it.
--  9. LEAK EXCLUSIONS. The known-leak list is an operational judgement, not a
--     schema fact - it lives in benchmarks.json meta.exclusions.known_leaks and
--     is substituted into the corpus block below. Keep the two in sync. A
--     single leaked promo code can move a whole cohort's value rate.
-- ================================================================


-- #################### SHARED CORPUS BLOCK ####################
-- Every query below starts with this WITH block. Each query states which extra
-- corpus columns it needs; the full version here carries all of them.
WITH dt_map AS (
  -- Deliverable type usually only exists on the raw CRM replica - it is rarely
  -- modelled into the analytics layer. Dedupe to the latest extract per record.
  SELECT {{COL_POST_ID}} AS post_id,
         JSON_VALUE(properties, '$.{{COL_DELIVERABLE_TYPE}}') AS dt_raw
  FROM `{{WAREHOUSE_PROJECT}}.{{TBL_CRM_POST_REPLICA}}`
  QUALIFY ROW_NUMBER() OVER (PARTITION BY {{COL_POST_ID}} ORDER BY _extracted_at DESC) = 1
),
creator_flags AS (
  -- Lifetime promo vs link split per creator. Used only for the leak heuristic,
  -- so it is deliberately unwindowed - a code that leaked two years ago still
  -- tells you the creator's history is untrustworthy.
  SELECT {{COL_CREATOR_NAME}},
         SUM(IF({{COL_CAMPAIGN}} LIKE '{{CAMPAIGN_PREFIX_PROMO}}%', {{COL_NEW_CONVERSIONS}}, 0)) AS promo_s,
         SUM(IF({{COL_CAMPAIGN}} NOT LIKE '{{CAMPAIGN_PREFIX_PROMO}}%'
            AND {{COL_CAMPAIGN}} NOT LIKE '{{CAMPAIGN_PREFIX_AFFILIATE}}%',
                {{COL_NEW_CONVERSIONS}}, 0)) AS link_s
  FROM `{{WAREHOUSE_PROJECT}}.{{TBL_CAMPAIGN_DAILY}}`
  GROUP BY 1
),
base AS (
  SELECT p.{{COL_POST_ID}} AS post_id,
         LOWER(TRIM(p.{{COL_HANDLE}})) AS handle,
         p.{{COL_CREATOR_NAME}} AS creator_name,
         -- multi-valued CRM category fields are usually delimited; take the first
         SPLIT(COALESCE(p.{{COL_NICHE}}, 'Uncategorized'), CHR(59))[OFFSET(0)] AS niche,
         -- AUDIENCE geo. Fill the three lists from rates.md (geo tiers).
         CASE
           WHEN p.{{COL_COUNTRY}} IN ({{GEO_TIER_1}}) THEN 'T1'
           WHEN p.{{COL_COUNTRY}} IN ({{GEO_TIER_2}}) THEN 'T2'
           WHEN p.{{COL_COUNTRY}} IS NULL THEN NULL   -- unknown geo is NOT T3
           ELSE 'T3' END AS tier,
         p.{{COL_COUNTRY}} AS country,
         LOWER(COALESCE(p.{{COL_PLATFORM}}, 'other')) AS platform,
         -- Normalise the CRM's deliverable dropdown into the engine's codes.
         -- These LIKE patterns are examples: replace them with your own option
         -- labels. Keep the fallbacks - historical posts are mostly unlabeled,
         -- and the YouTube fallback deliberately does NOT guess, because the
         -- dedicated-vs-integration price gap is far too large to assume.
         CASE
           WHEN m.dt_raw LIKE '%dedicated%'          THEN 'yt_dedicated'
           WHEN m.dt_raw LIKE '%mid-roll%'           THEN 'yt_integration'
           WHEN m.dt_raw LIKE '%integration%'        THEN 'yt_integration'
           WHEN m.dt_raw LIKE '%Short%'              THEN 'yt_short'
           WHEN m.dt_raw LIKE '%Reel%'               THEN 'ig_reel'
           WHEN m.dt_raw LIKE '%IG Carousel%'        THEN 'ig_carousel'
           WHEN m.dt_raw LIKE '%Static%'             THEN 'ig_static'
           WHEN m.dt_raw LIKE '%Stories%'            THEN 'ig_stories'
           WHEN m.dt_raw LIKE '%TT video%'           THEN 'tt_video'
           WHEN m.dt_raw LIKE '%TT Carousel%'        THEN 'tt_carousel'
           WHEN m.dt_raw LIKE '%Main Banner%'        THEN 'nl_main'
           WHEN m.dt_raw LIKE '%Secondary Banner%'   THEN 'nl_secondary'
           WHEN m.dt_raw LIKE '%Dedicated feature%'  THEN 'nl_feature'
           WHEN m.dt_raw LIKE '%Highlight%'          THEN 'nl_shoutout'
           WHEN m.dt_raw LIKE '%Community%'          THEN 'community'
           WHEN m.dt_raw IS NULL AND LOWER(p.{{COL_PLATFORM}}) = 'youtube'    THEN 'yt_unspecified'
           WHEN m.dt_raw IS NULL AND LOWER(p.{{COL_PLATFORM}}) = 'instagram'  THEN 'ig_reel'
           WHEN m.dt_raw IS NULL AND LOWER(p.{{COL_PLATFORM}}) = 'tiktok'     THEN 'tt_video'
           WHEN m.dt_raw IS NULL AND LOWER(p.{{COL_PLATFORM}}) = 'newsletter' THEN 'nl_main'
           ELSE LOWER(COALESCE(p.{{COL_PLATFORM}}, 'other')) END AS dt,
         (m.dt_raw IS NULL) AS dt_inferred,
         p.{{COL_FEE}} AS pay,
         p.{{COL_VIEWS}} AS views,
         p.{{COL_GOLIVE}} AS go_live,
         DATE_DIFF(CURRENT_DATE(), p.{{COL_GOLIVE}}, DAY) AS age_days,
         p.{{COL_LEAD_STATUS}} AS lead_status,
         p.{{COL_OWNER}} AS owner,
         p.{{COL_DEAL_STAGE}} AS deal_stage_label,
         p.{{COL_AFFILIATE_RATE}} AS aff_rate,
         -- RAW utm on both sides of the join. See trap 1.
         NULLIF(LOWER(TRIM(p.{{COL_POST_UTM}})), '') AS utm
  FROM `{{WAREHOUSE_PROJECT}}.{{TBL_POSTS}}` p
  LEFT JOIN dt_map m USING (post_id)
  WHERE p.{{COL_GOLIVE}} IS NOT NULL
),
outcomes AS (
  -- Link-attributed outcomes only. Promo and affiliate are excluded here and
  -- handled separately (traps 2 and 3).
  SELECT NULLIF(LOWER(TRIM({{COL_POST_UTM}})), '') AS utm,
         SUM(IF({{COL_REPORT_DATE}} <= DATE_ADD({{COL_GOLIVE}}, INTERVAL {{PAYBACK_WINDOW}} DAY), {{COL_NEW_CONVERSIONS}}, 0)) AS s_win,
         SUM(IF({{COL_REPORT_DATE}} <= DATE_ADD({{COL_GOLIVE}}, INTERVAL {{PAYBACK_WINDOW}} DAY), {{COL_VALUE_ADDED}},      0)) AS v_win,
         SUM(IF({{COL_REPORT_DATE}} <= DATE_ADD({{COL_GOLIVE}}, INTERVAL {{PAYBACK_WINDOW}} DAY), {{COL_DAILY_REVENUE}},    0)) AS r_win,
         SUM({{COL_NEW_CONVERSIONS}}) AS s_lt,
         SUM({{COL_VALUE_ADDED}})     AS v_lt,
         SUM({{COL_DAILY_REVENUE}})   AS r_lt
  FROM `{{WAREHOUSE_PROJECT}}.{{TBL_CAMPAIGN_DAILY}}`
  WHERE {{COL_CAMPAIGN}} NOT LIKE '{{CAMPAIGN_PREFIX_PROMO}}%'
    AND {{COL_CAMPAIGN}} NOT LIKE '{{CAMPAIGN_PREFIX_AFFILIATE}}%'
    AND {{COL_POST_UTM}} IS NOT NULL AND {{COL_GOLIVE}} IS NOT NULL
  GROUP BY 1
),
promo_daily AS (
  -- Promo-code outcomes: creator-level, no post key. See trap 2.
  SELECT {{COL_CREATOR_NAME}}, {{COL_REPORT_DATE}},
         SUM({{COL_NEW_CONVERSIONS}}) AS p_subs,
         SUM({{COL_VALUE_ADDED}})     AS p_val,
         SUM({{COL_DAILY_REVENUE}})   AS p_rev
  FROM `{{WAREHOUSE_PROJECT}}.{{TBL_CAMPAIGN_DAILY}}`
  WHERE {{COL_CAMPAIGN}} LIKE '{{CAMPAIGN_PREFIX_PROMO}}%'
  GROUP BY 1, 2
),
promo_cover AS (
  -- How many of this creator's posts are in-window on that day. This count is
  -- the divisor that stops the same promo conversion being counted once per post.
  SELECT b.creator_name, pd.{{COL_REPORT_DATE}} AS report_date, COUNT(*) AS n_posts
  FROM base b
  JOIN promo_daily pd ON pd.{{COL_CREATOR_NAME}} = b.creator_name
   AND pd.{{COL_REPORT_DATE}} BETWEEN b.go_live AND DATE_ADD(b.go_live, INTERVAL {{PAYBACK_WINDOW}} DAY)
  GROUP BY 1, 2
),
promo_alloc AS (
  SELECT b.post_id,
         SUM(pd.p_subs / pc.n_posts) AS ps_win,
         SUM(pd.p_val  / pc.n_posts) AS pv_win,
         SUM(pd.p_rev  / pc.n_posts) AS pr_win
  FROM base b
  JOIN promo_daily pd ON pd.{{COL_CREATOR_NAME}} = b.creator_name
   AND pd.{{COL_REPORT_DATE}} BETWEEN b.go_live AND DATE_ADD(b.go_live, INTERVAL {{PAYBACK_WINDOW}} DAY)
  JOIN promo_cover pc ON pc.creator_name = pd.{{COL_CREATOR_NAME}} AND pc.report_date = pd.{{COL_REPORT_DATE}}
  GROUP BY 1
),
boost_flag AS (
  -- Any post whose window overlaps paid amplification of the same creator. Trap 4.
  SELECT DISTINCT b.post_id
  FROM base b
  JOIN `{{WAREHOUSE_PROJECT}}.{{TBL_BOOST_DAILY}}` bc
    ON LOWER(TRIM(bc.{{COL_HANDLE}})) = b.handle AND bc.{{COL_BOOST_SPEND}} > 0
   AND bc.{{COL_REPORT_DATE}} BETWEEN b.go_live AND DATE_ADD(b.go_live, INTERVAL {{PAYBACK_WINDOW}} DAY)
),
corpus AS (
  SELECT b.post_id, b.handle, b.creator_name, b.niche, b.tier, b.country, b.platform, b.dt,
         b.pay, b.views, b.go_live, b.age_days, b.lead_status, b.owner, b.deal_stage_label, b.aff_rate,
         COALESCE(o.s_win, 0) + COALESCE(pa.ps_win, 0) AS subs_win,
         COALESCE(o.v_win, 0) + COALESCE(pa.pv_win, 0) AS val_win,
         COALESCE(o.r_win, 0) + COALESCE(pa.pr_win, 0) AS rev_win,
         COALESCE(o.s_win, 0) AS link_s_win,
         COALESCE(o.v_win, 0) AS link_v_win,
         COALESCE(pa.ps_win, 0) AS promo_s_win,
         COALESCE(o.s_lt, 0) AS link_s_lt,
         COALESCE(o.v_lt, 0) AS link_v_lt,
         COALESCE(o.r_lt, 0) AS link_r_lt,
         CAST(bf.post_id IS NOT NULL AS INT64) AS boosted_window,
         -- Confirmed leaks. Substitute the list from
         -- benchmarks.json meta.exclusions.known_leaks. Keep it as a literal
         -- IN-list rather than a table so the exclusion is visible in the query
         -- that produced the numbers - a silent exclusion is how a benchmark
         -- becomes unexplainable six months later.
         CAST(b.handle IN ({{KNOWN_LEAK_HANDLES}}) AS INT64) AS known_leak,
         -- Auto promo-leak heuristic, two-sided (absolute AND share). Thresholds
         -- from benchmarks.json meta.exclusions.auto_rules.promo_leak.
         CAST(COALESCE(
           (cf.promo_s >= {{LEAK_PROMO_ABS_LOW}}  AND SAFE_DIVIDE(cf.promo_s, cf.promo_s + cf.link_s) >= {{LEAK_PROMO_SHARE_HIGH}}) OR
           (cf.promo_s >= {{LEAK_PROMO_ABS_HIGH}} AND SAFE_DIVIDE(cf.promo_s, cf.promo_s + cf.link_s) >= {{LEAK_PROMO_SHARE_LOW}}),
           FALSE) AS INT64) AS leak_suspect
  FROM base b
  LEFT JOIN outcomes o USING (utm)
  LEFT JOIN promo_alloc pa USING (post_id)
  LEFT JOIN boost_flag bf USING (post_id)
  LEFT JOIN creator_flags cf ON cf.{{COL_CREATOR_NAME}} = b.creator_name
)


-- #################### Q1 - COHORT TABLES -> cohorts.json ####################
-- Produces both the CPM bands (what you actually pay) and the value rates
-- (what a post is actually worth) at four levels of specificity.
-- append to the shared block:
, conv_excl AS (
  -- Auto link-leak exclusion. Absolute floor AND rate test; social platforms
  -- only, because newsletter conversion rates are legitimately an order of
  -- magnitude higher and would all trip a view-based rate test.
  SELECT handle FROM (
    SELECT handle, SUM(link_s_win) AS s, SUM(views) AS v
    FROM corpus
    WHERE platform IN ('youtube','instagram','tiktok') AND handle IS NOT NULL
    GROUP BY 1)
  WHERE s >= {{LEAK_LINK_ABS}} AND SAFE_DIVIDE(s, NULLIF(v,0))*1000 >= {{LEAK_LINK_RATE_PER_1K}}
),
ranked AS (
  SELECT c.platform, c.niche, c.dt, c.pay, c.views, c.go_live, c.age_days, c.val_win, c.subs_win,
         -- decay weight: half-life 12 months
         POW(0.5, c.age_days/365.0) AS w,
         -- "clean" = paid, mature, above the views floor, not boost-overlapped.
         -- Traps 4, 5 and 6 all live in this one boolean.
         (c.pay > 0 AND c.views IS NOT NULL AND c.views >= 300
            AND c.age_days >= {{PAYBACK_WINDOW}} AND c.boosted_window = 0) AS clean
  FROM corpus c
  WHERE c.known_leak = 0 AND c.leak_suspect = 0
    AND (c.handle IS NULL OR c.handle NOT IN (SELECT handle FROM conv_excl))
),
lv AS (
  SELECT 'pnd' AS level, CONCAT(platform,'|',niche,'|',dt) AS cohort_key,
         pay, views, go_live, age_days, val_win, subs_win, w, clean FROM ranked
  UNION ALL
  SELECT 'pn', CONCAT(platform,'|',niche), pay, views, go_live, age_days, val_win, subs_win, w, clean FROM ranked
  UNION ALL
  SELECT 'p', platform, pay, views, go_live, age_days, val_win, subs_win, w, clean FROM ranked
  UNION ALL
  SELECT 'd', dt, pay, views, go_live, age_days, val_win, subs_win, w, clean FROM ranked
)
SELECT level, cohort_key,
  -- CPM band, trailing 24 months. Preferred window: old enough to have sample,
  -- recent enough to still be the market you are buying in.
  ROUND(APPROX_QUANTILES(IF(pay>0 AND views>=300 AND age_days<=730, SAFE_DIVIDE(pay,views)*1000, NULL),100)[OFFSET(25)],1) AS b24_p25,
  ROUND(APPROX_QUANTILES(IF(pay>0 AND views>=300 AND age_days<=730, SAFE_DIVIDE(pay,views)*1000, NULL),100)[OFFSET(50)],1) AS b24_med,
  ROUND(APPROX_QUANTILES(IF(pay>0 AND views>=300 AND age_days<=730, SAFE_DIVIDE(pay,views)*1000, NULL),100)[OFFSET(75)],1) AS b24_p75,
  COUNTIF(pay>0 AND views>=300 AND age_days<=730) AS b24_n,
  -- current-regime CPM, for drift reading only
  ROUND(APPROX_QUANTILES(IF(pay>0 AND views>=300 AND go_live>='{{REGIME_START_DATE}}', SAFE_DIVIDE(pay,views)*1000, NULL),100)[OFFSET(50)],1) AS bnow_med,
  COUNTIF(pay>0 AND views>=300 AND go_live>='{{REGIME_START_DATE}}') AS bnow_n,
  -- all-history fallback band, used only when the 24m sample is too thin
  ROUND(APPROX_QUANTILES(IF(pay>0 AND views>=300, SAFE_DIVIDE(pay,views)*1000, NULL),100)[OFFSET(25)],1) AS ball_p25,
  ROUND(APPROX_QUANTILES(IF(pay>0 AND views>=300, SAFE_DIVIDE(pay,views)*1000, NULL),100)[OFFSET(50)],1) AS ball_med,
  ROUND(APPROX_QUANTILES(IF(pay>0 AND views>=300, SAFE_DIVIDE(pay,views)*1000, NULL),100)[OFFSET(75)],1) AS ball_p75,
  COUNTIF(pay>0 AND views>=300) AS ball_n,
  -- absolute fee medians, for cohorts where views are missing on most rows
  ROUND(APPROX_QUANTILES(IF(pay>0 AND age_days<=730, pay, NULL),100)[OFFSET(50)],0) AS fee24_med,
  COUNTIF(pay>0 AND age_days<=730) AS fee24_n,
  ROUND(APPROX_QUANTILES(IF(pay>0, pay, NULL),100)[OFFSET(50)],0) AS feeall_med,
  COUNTIF(pay>0) AS feeall_n,
  -- decay-weighted value rates. Note these are ratios of weighted SUMS, not
  -- means of per-post ratios: a 500k-view post should dominate a 2k-view post,
  -- and averaging ratios would give them equal votes.
  ROUND(SAFE_DIVIDE(SUM(IF(clean, w*val_win, 0)),  SUM(IF(clean, w*views, 0)))*1000, 2) AS w_v_per_1k,
  ROUND(SAFE_DIVIDE(SUM(IF(clean, w*subs_win, 0)), SUM(IF(clean, w*views, 0)))*1000, 3) AS w_s_per_1k,
  ROUND(SAFE_DIVIDE(SUM(IF(clean, w*val_win, 0)),  SUM(IF(clean, w*subs_win, 0))), 1)   AS w_value_per_conv,
  COUNTIF(clean) AS vr_n,
  ROUND(SUM(IF(clean, w, 0)),1) AS vr_neff,   -- effective n after decay - watch this, not vr_n
  -- current-regime value rates, unweighted (the window is short enough)
  ROUND(SAFE_DIVIDE(SUM(IF(clean AND go_live>='{{REGIME_START_DATE}}', val_win, 0)),  SUM(IF(clean AND go_live>='{{REGIME_START_DATE}}', views, 0)))*1000, 2) AS vnow_v_per_1k,
  ROUND(SAFE_DIVIDE(SUM(IF(clean AND go_live>='{{REGIME_START_DATE}}', subs_win, 0)), SUM(IF(clean AND go_live>='{{REGIME_START_DATE}}', views, 0)))*1000, 3) AS snow_per_1k,
  COUNTIF(clean AND go_live>='{{REGIME_START_DATE}}') AS vnow_n,
  ROUND(SAFE_DIVIDE(SUM(IF(clean, val_win, 0)), SUM(IF(clean, views, 0)))*1000, 2) AS vall_v_per_1k,
  -- share of clean posts that paid for themselves inside the window. Expect this
  -- to be well under half even in a healthy portfolio - the returns are hit-driven.
  ROUND(SAFE_DIVIDE(COUNTIF(clean AND val_win>=pay), COUNTIF(clean)), 3) AS prof_window
FROM lv
GROUP BY 1,2
HAVING b24_n>=8 OR ball_n>=8 OR vr_n>=8
ORDER BY level, vr_n DESC


-- #################### Q2 - GEO CELLS -> geo_cells.json ####################
-- Geo multipliers are MEASURED, not assumed. Comparing tiers within a
-- platform x niche cell holds the content type constant; comparing tiers
-- globally just measures which tier your cheap platforms happen to skew to.
-- append to the shared block:
SELECT platform, niche, tier,
       COUNTIF(pay>0 AND views>=300) AS n_cpm,
       ROUND(APPROX_QUANTILES(IF(pay>0 AND views>=300, SAFE_DIVIDE(pay,views)*1000, NULL),100)[OFFSET(50)],1) AS med_cpm,
       SUM(IF(pay>0 AND views>=300 AND age_days>={{PAYBACK_WINDOW}}, views, 0)) AS views_sum,
       ROUND(SUM(IF(pay>0 AND views>=300 AND age_days>={{PAYBACK_WINDOW}}, link_v_win, 0)),0) AS v_sum,
       ROUND(SUM(IF(pay>0 AND views>=300 AND age_days>={{PAYBACK_WINDOW}}, link_s_win, 0)),0) AS s_sum
FROM corpus
WHERE tier IS NOT NULL AND known_leak = 0 AND leak_suspect = 0
  AND platform IN ('youtube','instagram','tiktok')
GROUP BY 1,2,3
HAVING n_cpm >= 6
ORDER BY platform, niche, tier


-- #################### Q3 - DRIFT year x platform -> drift.json ####################
-- The regime-change detector. Run it every refresh and read it before you argue
-- with anyone about "what things cost now". If median CPM and conversion per
-- view are both moving fast in opposite directions, your intuition is stale and
-- so is everyone else's.
-- append to the shared block:
, clean AS (
  SELECT EXTRACT(YEAR FROM go_live) AS yr, platform, pay, views, subs_win, val_win, rev_win
  FROM corpus
  WHERE pay > 0 AND views IS NOT NULL AND views >= 300 AND age_days >= {{PAYBACK_WINDOW}}
    AND boosted_window = 0 AND known_leak = 0 AND leak_suspect = 0
    AND platform IN ('youtube','instagram','tiktok')
),
byp AS (
  SELECT yr, platform, COUNT(*) AS n, ROUND(SUM(pay),0) AS spend,
         ROUND(APPROX_QUANTILES(pay,100)[OFFSET(50)],0) AS med_fee,
         ROUND(APPROX_QUANTILES(SAFE_DIVIDE(pay,views)*1000,100)[OFFSET(50)],1) AS med_cpm,
         SUM(views) AS views_sum, ROUND(SUM(subs_win),0) AS subs_win,
         ROUND(SAFE_DIVIDE(SUM(subs_win), SUM(views))*1000, 3) AS s_per_1k,
         ROUND(SAFE_DIVIDE(SUM(pay), NULLIF(SUM(subs_win),0)),0) AS cac,
         ROUND(SUM(val_win),0) AS v_win,
         ROUND(SAFE_DIVIDE(SUM(val_win), NULLIF(SUM(subs_win),0)),0) AS value_per_conv,
         ROUND(SAFE_DIVIDE(SUM(val_win), NULLIF(SUM(pay),0)),2) AS ltv_cac,
         ROUND(SAFE_DIVIDE(SUM(val_win)-SUM(pay), NULLIF(SUM(pay),0))*100,0) AS roi_pct,
         -- cash payback is the honest twin of ROI: value_added may be a
         -- prediction, revenue is money that actually arrived
         ROUND(SAFE_DIVIDE(SUM(rev_win), NULLIF(SUM(pay),0))*100,0) AS payback_pct
  FROM clean GROUP BY 1,2
),
allp AS (
  SELECT yr, 'ALL' AS platform, COUNT(*) AS n, ROUND(SUM(pay),0) AS spend,
         ROUND(APPROX_QUANTILES(pay,100)[OFFSET(50)],0) AS med_fee,
         ROUND(APPROX_QUANTILES(SAFE_DIVIDE(pay,views)*1000,100)[OFFSET(50)],1) AS med_cpm,
         SUM(views) AS views_sum, ROUND(SUM(subs_win),0) AS subs_win,
         ROUND(SAFE_DIVIDE(SUM(subs_win), SUM(views))*1000, 3) AS s_per_1k,
         ROUND(SAFE_DIVIDE(SUM(pay), NULLIF(SUM(subs_win),0)),0) AS cac,
         ROUND(SUM(val_win),0) AS v_win,
         ROUND(SAFE_DIVIDE(SUM(val_win), NULLIF(SUM(subs_win),0)),0) AS value_per_conv,
         ROUND(SAFE_DIVIDE(SUM(val_win), NULLIF(SUM(pay),0)),2) AS ltv_cac,
         ROUND(SAFE_DIVIDE(SUM(val_win)-SUM(pay), NULLIF(SUM(pay),0))*100,0) AS roi_pct,
         ROUND(SAFE_DIVIDE(SUM(rev_win), NULLIF(SUM(pay),0))*100,0) AS payback_pct
  FROM clean GROUP BY 1
)
SELECT yr, platform, n, spend, med_fee, med_cpm, views_sum, subs_win, s_per_1k, cac, v_win,
       value_per_conv, ltv_cac, roi_pct, payback_pct FROM byp
UNION ALL
SELECT yr, platform, n, spend, med_fee, med_cpm, views_sum, subs_win, s_per_1k, cac, v_win,
       value_per_conv, ltv_cac, roi_pct, payback_pct FROM allp
ORDER BY platform, yr


-- #################### Q4 - BACKTEST pay vs EV -> backtest.json ####################
-- The query that justifies TARGET = 0.5x EV. It reprices every historical post
-- with the CURRENT estimator, buckets by what you actually paid as a multiple of
-- that EV, and reports pooled ROI per bucket. Two honesty notes:
--   * this is in-sample - the same posts inform r_cur and get scored by it. It
--     is directional, not a clean out-of-sample test. Splitting by era at least
--     shows whether the shape is stable across regimes.
--   * read pooled_roi_pct, not profitable_share. The portfolio is hit-driven:
--     a bucket can have a low win rate and still be the most profitable one.
-- append to the shared block:
, clean AS (
  SELECT platform, niche, dt, pay, views, go_live, age_days, val_win,
         POW(0.5, age_days/365.0) AS w
  FROM corpus
  WHERE pay > 0 AND views IS NOT NULL AND views >= 300 AND age_days >= {{PAYBACK_WINDOW}}
    AND boosted_window = 0 AND known_leak = 0 AND leak_suspect = 0
),
vr AS (
  SELECT level, cohort_key,
         SAFE_DIVIDE(SUM(w*val_win), SUM(w*views))*1000 AS rw,
         SAFE_DIVIDE(SUM(IF(go_live>='{{REGIME_START_DATE}}', val_win, 0)),
                     SUM(IF(go_live>='{{REGIME_START_DATE}}', views, 0)))*1000 AS r_now,
         COUNTIF(go_live>='{{REGIME_START_DATE}}') AS n_now,
         COUNT(*) AS n
  FROM (
    SELECT 'pnd' AS level, CONCAT(platform,'|',niche,'|',dt) AS cohort_key, w, val_win, views, go_live FROM clean
    UNION ALL SELECT 'pn', CONCAT(platform,'|',niche), w, val_win, views, go_live FROM clean
    UNION ALL SELECT 'p', platform, w, val_win, views, go_live FROM clean
  )
  GROUP BY 1, 2
  HAVING n >= 15
),
rcur AS (
  -- same shrinkage as the engine: k = 25
  SELECT level, cohort_key,
         SAFE_DIVIDE(COALESCE(n_now,0) * COALESCE(r_now, rw) + 25 * rw, COALESCE(n_now,0) + 25) AS r_cur
  FROM vr
),
ev AS (
  -- cohort fallback chain, most specific first
  SELECT c.pay, c.views, c.go_live, c.val_win,
         c.views / 1000 * COALESCE(r_pnd.r_cur, r_pn.r_cur, r_p.r_cur) AS ev_win
  FROM clean c
  LEFT JOIN rcur r_pnd ON r_pnd.level='pnd' AND r_pnd.cohort_key = CONCAT(c.platform,'|',c.niche,'|',c.dt)
  LEFT JOIN rcur r_pn  ON r_pn.level='pn'   AND r_pn.cohort_key  = CONCAT(c.platform,'|',c.niche)
  LEFT JOIN rcur r_p   ON r_p.level='p'     AND r_p.cohort_key   = c.platform
)
SELECT IF(go_live>='{{REGIME_START_DATE}}','current','prior') AS era,
       CASE WHEN pay <= ev_win*0.4 THEN '1_<=0.4'
            WHEN pay <= ev_win*0.5 THEN '2_<=0.5'
            WHEN pay <= ev_win*0.8 THEN '3_<=0.8'
            WHEN pay <= ev_win*1.0 THEN '4_<=1.0'
            WHEN pay <= ev_win*1.5 THEN '5_<=1.5'
            ELSE '6_>1.5' END AS bucket,
       COUNT(*) AS n,
       ROUND(SAFE_DIVIDE(COUNTIF(val_win>=pay), COUNT(*)), 3) AS profitable_share,
       ROUND(SUM(pay),0) AS spend,
       ROUND(SUM(val_win),0) AS v_win,
       ROUND(SAFE_DIVIDE(SUM(val_win)-SUM(pay), NULLIF(SUM(pay),0))*100, 0) AS pooled_roi_pct
FROM ev
WHERE ev_win IS NOT NULL AND ev_win > 0
GROUP BY 1, 2
ORDER BY era, bucket


-- #################### Q5 - CREATOR SNAPSHOT -> snapshot_all.json ####################
-- Per-creator aggregate: price book, realized value per post, unit economics,
-- leak flags. Output feeds creators_snapshot.json, which is LOCAL ONLY - it
-- contains named creators with fees paid and realized value and must never be
-- committed to a skill repo.
--
-- If your gateway caps result rows, run this twice on a handle range and merge:
--   WHERE a.handle IS NULL OR a.handle < 'j'      -- first run
--   WHERE a.handle >= 'j'                          -- second run
-- Split further if either half returns exactly the cap.
-- append to the shared block:
, pb AS (
  -- price book: the last few paid fees per deliverable. This is the
  -- re-onboarding anchor - you cannot renegotiate what you cannot see.
  SELECT handle, dt,
         COUNTIF(pay>0) AS n_paid,
         ARRAY_AGG(IF(pay>0, STRUCT(pay, views, CAST(go_live AS STRING) AS d), NULL) IGNORE NULLS
                   ORDER BY go_live DESC LIMIT 5) AS recent_paid
  FROM corpus GROUP BY 1,2
),
pbj AS (
  SELECT handle, TO_JSON_STRING(ARRAY_AGG(STRUCT(dt, n_paid, recent_paid))) AS price_book
  FROM pb WHERE n_paid > 0 GROUP BY 1
),
recent_views AS (
  -- unpaid posts included on purpose: organic reach is organic reach, and the
  -- median of the last handful is the views basis for the next card
  SELECT handle, TO_JSON_STRING(ARRAY_AGG(views IGNORE NULLS ORDER BY go_live DESC LIMIT 8)) AS recent_views
  FROM corpus GROUP BY 1
),
agg AS (
  SELECT handle,
    ANY_VALUE(creator_name) AS name,
    -- MAX_BY on go_live: creators change platform, niche and country over time
    -- and the engine wants the CURRENT state, not the modal one
    MAX_BY(platform, go_live) AS platform_latest,
    MAX_BY(niche, go_live) AS niche,
    MAX_BY(tier, go_live) AS tier,
    MAX_BY(country, go_live) AS country,
    MAX_BY(owner, go_live) AS owner,
    MAX_BY(lead_status, go_live) AS lead_status,
    MAX_BY(deal_stage_label, go_live) AS latest_deal_stage,
    MAX_BY(aff_rate, go_live) AS aff_rate,
    COUNT(*) AS lt_posts,
    COUNTIF(pay>0) AS paid_posts,
    CAST(MIN(go_live) AS STRING) AS first_live,
    CAST(MAX(go_live) AS STRING) AS last_live,
    COUNTIF(age_days<=365) AS posts_12m,
    ROUND(SUM(IF(pay>0,pay,0)),0) AS pay_total,
    ROUND(SUM(subs_win),1) AS subs_win_total,
    ROUND(SUM(val_win),0) AS val_win_total,
    ROUND(SUM(rev_win),0) AS rev_win_total,
    ROUND(SUM(link_v_win),0) AS link_v_win_total,
    ROUND(SUM(promo_s_win),1) AS promo_s_win_total,
    SUM(link_s_lt) AS link_s_lt_total,
    ROUND(SUM(link_v_lt),0) AS link_v_lt_total,
    ROUND(SUM(link_r_lt),0) AS link_r_lt_total,
    SUM(boosted_window) AS boosted_posts,
    MAX(known_leak) AS known_leak,
    MAX(leak_suspect) AS leak_suspect,
    SUM(views) AS views_total,
    SUM(IF(pay>0, views, 0)) AS views_paid_total,
    -- social-only link conversions and views: the denominator for the
    -- conversions-per-1k leak test (newsletters would skew it, see Q1)
    ROUND(SUM(IF(platform IN ('youtube','instagram','tiktok'), link_s_win, 0)),1) AS link_s_win_social,
    SUM(IF(platform IN ('youtube','instagram','tiktok'), views, 0)) AS views_social,
    -- vpp = decay-weighted realized value per PAID, MATURE, UNBOOSTED post.
    -- This is what replaces the cohort rate for proven creators.
    ROUND(SAFE_DIVIDE(SUM(IF(pay>0 AND age_days>={{PAYBACK_WINDOW}} AND boosted_window=0, POW(0.5, age_days/365.0)*val_win, 0)),
                      SUM(IF(pay>0 AND age_days>={{PAYBACK_WINDOW}} AND boosted_window=0, POW(0.5, age_days/365.0), 0))),0) AS vpp,
    -- link-only twin, used when the creator is promo-suspect
    ROUND(SAFE_DIVIDE(SUM(IF(pay>0 AND age_days>={{PAYBACK_WINDOW}} AND boosted_window=0, POW(0.5, age_days/365.0)*link_v_win, 0)),
                      SUM(IF(pay>0 AND age_days>={{PAYBACK_WINDOW}} AND boosted_window=0, POW(0.5, age_days/365.0), 0))),0) AS vpp_link,
    COUNTIF(pay>0 AND age_days>={{PAYBACK_WINDOW}} AND boosted_window=0) AS vpp_n
  FROM corpus
  GROUP BY 1
)
SELECT a.handle, a.name, a.platform_latest, a.niche, a.tier, a.country, a.owner, a.lead_status,
       a.latest_deal_stage, a.aff_rate, a.lt_posts, a.paid_posts, a.first_live, a.last_live,
       a.posts_12m, a.pay_total, a.subs_win_total, a.val_win_total, a.rev_win_total,
       a.link_v_win_total, a.promo_s_win_total, a.link_s_lt_total, a.link_v_lt_total,
       a.link_r_lt_total, a.boosted_posts, a.known_leak, a.leak_suspect, a.vpp, a.vpp_link,
       a.vpp_n, a.views_total, a.views_paid_total, a.link_s_win_social, a.views_social,
       f.promo_s AS promo_s_lifetime, f.link_s AS link_s_lifetime,
       pbj.price_book, rv.recent_views
FROM agg a
LEFT JOIN creator_flags f ON f.{{COL_CREATOR_NAME}} = a.name
LEFT JOIN pbj USING (handle)
LEFT JOIN recent_views rv USING (handle)
WHERE a.handle IS NULL OR a.handle < 'j'   -- second run: WHERE a.handle >= 'j'
ORDER BY a.handle
