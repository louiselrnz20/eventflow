"""Read-only first-pass profiler for EventFlow's two source CSV files."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
SUMMERJAM = RAW / "summerjam_ticket_sales_by_date.csv"
SJSC = RAW / "sjsc_workshop_finance_report.csv"


def money(series: pd.Series) -> pd.Series:
    cleaned = (series.astype("string").str.replace(r"[₱, ]", "", regex=True)
              .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA}))
    return pd.to_numeric(cleaned, errors="coerce")


def profile_summerjam() -> None:
    if not SUMMERJAM.exists():
        print(f"MISSING: {SUMMERJAM}")
        return
    df = pd.read_csv(SUMMERJAM)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    print("\n=== SUMMERJAM TICKETMELON DAILY EXPORT ===")
    print(f"Rows: {len(df)} | Columns: {len(df.columns)}")
    print("Columns:", list(df.columns))
    print("Null counts:\n", df.isna().sum().to_string())
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    for col in ["View", "Visitor", "Total Amount", "Number Of Order", "Number Of Ticket"]:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    print(f"Total amount (sum of daily rows): PHP {df['Total Amount'].sum():,.2f}")
    print(f"Orders: {df['Number Of Order'].sum():,.0f}")
    print(f"Tickets: {df['Number Of Ticket'].sum():,.0f}")
    print(f"Days with sales: {(df['Total Amount'].fillna(0) > 0).sum()}")
    if df["Total Amount"].notna().any():
        peak = df.loc[df["Total Amount"].idxmax()]
        print(f"Highest-revenue date: {peak['Date'].date()} | PHP {peak['Total Amount']:,.2f}")


def profile_sjsc() -> None:
    if not SJSC.exists():
        print(f"MISSING: {SJSC}")
        return
    df = pd.read_csv(SJSC)
    print("\n=== SJSC WORKSHOP FINANCE REPORT ===")
    print(f"Rows: {len(df)} | Columns: {len(df.columns)}")
    print("Columns:", list(df.columns))
    print("Null counts:\n", df.isna().sum().to_string())

    # This CSV contains multiple sections side-by-side / vertically. Keep them
    # as raw sections until their intended meaning and grain are confirmed.
    class_col = df.get("CLASS", pd.Series(dtype="string")).astype("string").str.strip()
    total_col = money(df.get("TOTAL", pd.Series(dtype="string")))
    stated_total = total_col[class_col.eq("TOTAL")]
    first_five_sum = total_col.iloc[:5].sum(min_count=1)
    print("Stated TOTAL row(s):", stated_total.dropna().tolist())
    print(f"Sum of first five class-row TOTAL cells: PHP {first_five_sum:,.2f}")
    if not stated_total.empty and pd.notna(first_five_sum):
        declared = stated_total.iloc[0]
        if abs(declared - first_five_sum) > 0.01:
            print("VALIDATION WARNING: stated total does not match the first five class-row totals.")
            print("Do not publish a consolidated workshop revenue KPI until the report sections are reconciled.")


if __name__ == "__main__":
    print("EventFlow | Read-only source data profile")
    profile_summerjam()
    profile_sjsc()
