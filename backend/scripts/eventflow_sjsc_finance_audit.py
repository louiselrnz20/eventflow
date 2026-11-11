from pathlib import Path
from openpyxl import load_workbook

BASE_DIR = Path(__file__).resolve().parents[2]
FILE_PATH = BASE_DIR / "data" / "raw" / "sjsc_workshops.xlsx"

SHEET_NAME = "Finance Report"
TOTAL_CELL = "E19"
DATA_START_ROW = 2
DATA_END_ROW = 18

def numeric_value(value):
    """Return numeric cell values; treat blank cells as zero."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    raise ValueError(f"Expected a numeric cell value, received: {value!r}")

def main():
    if not FILE_PATH.exists():
        raise FileNotFoundError(
            f"Workbook not found: {FILE_PATH}\n"
            "Copy the original workbook to data/raw/sjsc_workshops.xlsx."
        )

    # data_only=True reads the cached results of Excel formulas.
    workbook = load_workbook(FILE_PATH, data_only=True, read_only=True)

    if SHEET_NAME not in workbook.sheetnames:
        raise ValueError(
            f"Missing worksheet '{SHEET_NAME}'. "
            f"Available sheets: {workbook.sheetnames}"
        )

    sheet = workbook[SHEET_NAME]

    early_bird_revenue = sum(
        numeric_value(sheet[f"B{row}"].value)
        for row in range(DATA_START_ROW, DATA_END_ROW + 1)
    )
    regular_revenue = sum(
        numeric_value(sheet[f"C{row}"].value)
        for row in range(DATA_START_ROW, DATA_END_ROW + 1)
    )
    walk_in_revenue = sum(
        numeric_value(sheet[f"D{row}"].value)
        for row in range(DATA_START_ROW, DATA_END_ROW + 1)
    )

    recomputed_total = (
        early_bird_revenue + regular_revenue + walk_in_revenue
    )
    reported_total = numeric_value(sheet[TOTAL_CELL].value)
    difference = recomputed_total - reported_total

    print("=" * 60)
    print("EVENTFLOW | SJSC FINANCE RECONCILIATION")
    print("=" * 60)
    print(f"Early-bird category revenue : PHP {early_bird_revenue:,.2f}")
    print(f"Regular-price revenue       : PHP {regular_revenue:,.2f}")
    print(f"Walk-in revenue             : PHP {walk_in_revenue:,.2f}")
    print("-" * 60)
    print(f"Recomputed total            : PHP {recomputed_total:,.2f}")
    print(f"Workbook reported total     : PHP {reported_total:,.2f}")
    print(f"Difference                  : PHP {difference:,.2f}")

    # E2:E6 are instructor-level allocation/summary formulas.
    # They overlap with revenue already represented in B2:D18.
    instructor_allocations = [
        numeric_value(sheet[f"E{row}"].value)
        for row in range(2, 7)
    ]
    print()
    print(
        "NOTE: Do not add instructor-level totals E2:E6 to the "
        "consolidated total."
    )
    print(
        "Those formulas allocate/reuse package and other category "
        "amounts, so summing them would double-count revenue."
    )
    print(
        "Instructor allocation total (reference only): "
        f"PHP {sum(instructor_allocations):,.2f}"
    )

    if abs(difference) < 0.005:
        print("\nSTATUS: PASS - B2:D18 reconciles with E19.")
    else:
        print("\nSTATUS: REVIEW - reported and recomputed totals differ.")

    print(
        "\nPrivacy: this audit intentionally does not print attendee names, "
        "email addresses, phone numbers, or payment proof links."
    )

    workbook.close()

if __name__ == "__main__":
    main()
