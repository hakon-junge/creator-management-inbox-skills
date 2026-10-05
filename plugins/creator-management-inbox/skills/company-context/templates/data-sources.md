# Data sources (advanced, optional)

> Only for teams with a CRM or a data warehouse they want the workflow to read.
> Leave everything as `none` and the workflow uses your creator notes
> (`~/.claude/inbox/creators/`) instead - that is enough to get great drafts.
> The workflow never WRITES to a CRM on its own; it tells you what to update.

## CRM

- `{{CRM_PLATFORM}}`: none - e.g. HubSpot, Airtable, Notion, a Google Sheet
- How Claude can read it: none - e.g. "the HubSpot connector in Claude", "a CSV export
  at ~/Documents/creators.csv"
- Where a creator's record lives: none - the object or sheet
- Fields worth reading (write the real field name next to each, or `none`):
  - `{{CRM_FIELD_PROMO_CODE}}`: none
  - `{{CRM_FIELD_COUNTRY}}`: none
  - `{{CRM_FIELD_VIEWS_LONGFORM}}`: none - median views, long-form
  - `{{CRM_FIELD_VIEWS_SHORTFORM}}`: none - median views, short-form
  - `{{CRM_FIELD_LEAD_STATUS}}`: none
  - Deal stage / fee / go-live date: none

## Performance data

- `{{DATA_AGENT}}`: see `me.md`
- `{{WAREHOUSE_PLATFORM}}`: none - e.g. BigQuery, Snowflake. Only needed for the
  rate engine's advanced mode (`rate-engine/references/README.md`).
- Tracking link format: none - e.g. `https://yourbrand.com/?utm_source=creator&utm_campaign=<handle>`
- `{{TRACKING_LINK_FORMAT}}`: see above
