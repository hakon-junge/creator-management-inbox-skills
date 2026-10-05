# Data sources (DEMO - fictional)

## CRM

- `{{CRM_PLATFORM}}`: a Google Sheet, "Creator Tracker 2026" (demo: the creator notes stand in for it)
- How Claude can read it: not connected in the demo - read the creator notes
- Where a creator's record lives: one row per booking, tab per campaign
- Fields worth reading:
  - `{{CRM_FIELD_PROMO_CODE}}`: Code
  - `{{CRM_FIELD_COUNTRY}}`: Audience country
  - `{{CRM_FIELD_VIEWS_LONGFORM}}`: none
  - `{{CRM_FIELD_VIEWS_SHORTFORM}}`: Median views
  - `{{CRM_FIELD_LEAD_STATUS}}`: Status
  - Deal stage / fee / go-live date: Stage, Fee (USD), Go-live, PO number, Invoice status

## Performance data

- `{{DATA_AGENT}}`: see `me.md`
- `{{WAREHOUSE_PLATFORM}}`: none
- Tracking link format: `https://quillmoss.example/?utm_source=creator&utm_campaign=<campaign>-<handle>`
- `{{TRACKING_LINK_FORMAT}}`: see above
