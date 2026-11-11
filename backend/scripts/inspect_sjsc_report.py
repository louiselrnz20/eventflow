
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

FILE_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "sjsc_workshop_finance_report.csv"
)

# Read without assuming the first row is the header.
df = pd.read_csv(FILE_PATH, header=None, dtype=str)

print("=" * 65)
print("EVENTFLOW | SJSC FINANCE REPORT AUDIT")
print("=" * 65)

# Display original row numbers and values.
for index, row in df.iterrows():
    row_number = index + 1

    values = [
        str(value).strip()
        if pd.notna(value)
        else ""
        for value in row.tolist()
    ]

    # Skip completely empty rows.
    if not any(values):
        continue

    print(f"\nROW {row_number:02d}")
    print("-" * 40)

    for column_number, value in enumerate(values, start=1):
        if value:
            print(f"Column {column_number}: {value}")

print("\n" + "=" * 65)
print("AUDIT COMPLETE")
print("=" * 65)
