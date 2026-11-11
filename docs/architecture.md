# EventFlow Architecture

```text
CSV exports (Ticketmelon + SJSC finance)
              |
              v
      FastAPI ingestion API
              |
              v
   pandas cleaning + validation
              |
      +-------+--------+
      |                |
      v                v
Daily ticket sales   Workshop finance
(normalized daily    (separate staging +
 aggregates)          reconciliation)
      |                |
      +-------+--------+
              v
       PostgreSQL database
              |
              v
      FastAPI analytics API
              |
              v
 React + TypeScript dashboard
 (KPIs, trends, filters, warnings)
```

## Core design decision: preserve data grain
- Ticketmelon file: one row per calendar date, with aggregate views, visitors, amount, orders, and tickets.
- SJSC finance file: mixed report layout containing class-level figures, pricing reference rows, and a stated total row. It must be parsed into separate staging sections and reconciled before aggregate reporting.

## Initial database entities (planned)
- `events`: event metadata and event identifier.
- `imports`: filename, source type, imported timestamp, row count, validation status.
- `ticket_sales_daily`: event_id, sale_date, views, visitors, gross_amount, order_count, ticket_count, import_id.
- `workshop_classes`: event_id, instructor/class label, scheduled time.
- `workshop_sales_summary`: class_id, early_bird_amount, regular_amount, walk_in_amount, reported_total, import_id.
- `validation_issues`: import_id, severity, issue_code, description, affected_row.

Money should use PostgreSQL `NUMERIC(12,2)`. Source values and derived values should be stored distinctly where possible.
