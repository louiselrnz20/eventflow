
from pathlib import Path
from decimal import Decimal

import pandas as pd
from sqlalchemy import text

from app.core.database import engine

# Locate the project and CSV file
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = PROJECT_ROOT / "data" / "raw" / "summerjam_ticket_sales_by_date.csv"

EVENT_NAME = "SummerJam Competition"
SOURCE_TYPE = "ticketmelon_daily_sales"

def load_and_validate_csv():
    """Read the CSV and validate its columns and values."""

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    required_columns = [
        "Date",
        "View",
        "Visitor",
        "Total Amount",
        "Number Of Order",
        "Number Of Ticket",
    ]

    missing_columns = set(required_columns) - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    # Convert dates using DD/MM/YYYY format
    df["Date"] = pd.to_datetime(
        df["Date"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    if df["Date"].isna().any():
        raise ValueError("The CSV contains invalid dates.")

    # Convert numeric columns
    numeric_columns = [
        "View",
        "Visitor",
        "Total Amount",
        "Number Of Order",
        "Number Of Ticket",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        if df[column].isna().any():
            raise ValueError(f"Invalid numeric values in {column}.")

        if (df[column] < 0).any():
            raise ValueError(f"Negative values found in {column}.")

    # Count fields must contain whole numbers
    count_columns = [
        "View",
        "Visitor",
        "Number Of Order",
        "Number Of Ticket",
    ]

    for column in count_columns:
        if not (df[column] % 1 == 0).all():
            raise ValueError(f"Non-integer values found in {column}.")

    # Check for duplicate dates
    if df["Date"].duplicated().any():
        raise ValueError("Duplicate sales dates found in CSV.")

    return df

def import_data():
    df = load_and_validate_csv()

    print("CSV validation successful.")
    print(f"Records to import: {len(df)}")

    # Prepare records for PostgreSQL
    records = []

    for _, row in df.iterrows():
        records.append({
            "sales_date": row["Date"].date(),
            "views": int(row["View"]),
            "visitors": int(row["Visitor"]),
            "total_amount": Decimal(str(row["Total Amount"])),
            "number_of_orders": int(row["Number Of Order"]),
            "number_of_tickets": int(row["Number Of Ticket"]),
        })

    # Insert everything in one database transaction
    with engine.begin() as connection:

        # Find or create the event
        event_id = connection.execute(
            text("""
                SELECT id
                FROM events
                WHERE event_name = :event_name
                LIMIT 1
            """),
            {"event_name": EVENT_NAME}
        ).scalar_one_or_none()

        if event_id is None:
            event_id = connection.execute(
                text("""
                    INSERT INTO events (event_name, event_type)
                    VALUES (:event_name, :event_type)
                    RETURNING id
                """),
                {
                    "event_name": EVENT_NAME,
                    "event_type": "Competition"
                }
            ).scalar_one()

        # Prevent importing the same completed file twice
        existing_import = connection.execute(
            text("""
                SELECT id
                FROM data_imports
                WHERE event_id = :event_id
                  AND filename = :filename
                  AND source_type = :source_type
                  AND import_status = 'completed'
                LIMIT 1
            """),
            {
                "event_id": event_id,
                "filename": CSV_PATH.name,
                "source_type": SOURCE_TYPE,
            }
        ).scalar_one_or_none()

        if existing_import is not None:
            print("This file has already been imported.")
            print(f"Existing import ID: {existing_import}")
            return

        # Create import history record
        import_id = connection.execute(
            text("""
                INSERT INTO data_imports (
                    event_id,
                    filename,
                    source_type,
                    import_status
                )
                VALUES (
                    :event_id,
                    :filename,
                    :source_type,
                    'completed'
                )
                RETURNING id
            """),
            {
                "event_id": event_id,
                "filename": CSV_PATH.name,
                "source_type": SOURCE_TYPE,
            }
        ).scalar_one()

        # Insert daily sales records
        connection.execute(
            text("""
                INSERT INTO ticket_sales_daily (
                    import_id,
                    sales_date,
                    views,
                    visitors,
                    total_amount,
                    number_of_orders,
                    number_of_tickets
                )
                VALUES (
                    :import_id,
                    :sales_date,
                    :views,
                    :visitors,
                    :total_amount,
                    :number_of_orders,
                    :number_of_tickets
                )
            """),
            [
                {"import_id": import_id, **record}
                for record in records
            ]
        )

    # Transaction committed successfully
    print("\nIMPORT SUCCESSFUL")
    print(f"Event: {EVENT_NAME}")
    print(f"Import ID: {import_id}")
    print(f"Records imported: {len(records)}")
    print(f"Total revenue: PHP {df['Total Amount'].sum():,.2f}")
    print(f"Total orders: {df['Number Of Order'].sum():,.0f}")
    print(f"Total tickets: {df['Number Of Ticket'].sum():,.0f}")

if __name__ == "__main__":
    try:
        import_data()
    except Exception as error:
        print(f"\nIMPORT FAILED: {error}")
        raise