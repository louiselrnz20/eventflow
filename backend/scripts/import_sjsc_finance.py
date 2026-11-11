from pathlib import Path
from decimal import Decimal

from openpyxl import load_workbook
from sqlalchemy import text

from app.core.database import engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXCEL_PATH = PROJECT_ROOT / "data" / "raw" / "sjsc_workshops.xlsx"

EVENT_NAME = "SJSC PH Qualifier Vol. 3"
SOURCE_TYPE = "sjsc_finance_report"


def money(value):
    """Convert Excel numeric values to Decimal, preserving blanks."""
    if value is None:
        return None
    return Decimal(str(value))


def load_finance_report():
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(f"File not found: {EXCEL_PATH}")

    workbook = load_workbook(
        EXCEL_PATH,
        read_only=False,
        data_only=True
    )

    try:
        if "Finance Report" not in workbook.sheetnames:
            raise ValueError("Finance Report sheet not found.")

        sheet = workbook["Finance Report"]

        # Read only the financial report, not attendee sheets.
        # Columns B, C, and D contain revenue categories.
        early_bird = sum(
            (money(sheet.cell(row, 2).value) or Decimal("0"))
            for row in range(2, 19)
        )

        regular = sum(
            (money(sheet.cell(row, 3).value) or Decimal("0"))
            for row in range(2, 19)
        )

        walk_ins = sum(
            (money(sheet.cell(row, 4).value) or Decimal("0"))
            for row in range(2, 19)
        )

        calculated_total = early_bird + regular + walk_ins
        reported_total = money(sheet["E19"].value)

        if reported_total is None:
            raise ValueError("Reported total in E19 is missing.")

        if calculated_total != reported_total:
            raise ValueError(
                f"Revenue mismatch. Calculated: {calculated_total}; "
                f"Reported: {reported_total}"
            )

        return {
            "early_bird": early_bird,
            "regular": regular,
            "walk_ins": walk_ins,
            "reported_total": reported_total,
            "instructors": [
                {
                    "name": sheet.cell(row, 1).value.strip(),
                    "early_bird": money(sheet.cell(row, 2).value),
                    "regular": money(sheet.cell(row, 3).value),
                    "walk_ins": money(sheet.cell(row, 4).value),
                    "total": money(sheet.cell(row, 5).value),
                }
                for row in range(2, 7)
            ],
            "package_revenue": [
                {
                    "name": sheet.cell(row, 1).value.strip(),
                    "early_bird": money(sheet.cell(row, 2).value),
                    "regular": money(sheet.cell(row, 3).value),
                    "walk_ins": money(sheet.cell(row, 4).value),
                }
                for row in range(7, 10)
            ],
            "package_prices": [
                {
                    "name": sheet.cell(row, 7).value.strip(),
                    "early_bird": money(sheet.cell(row, 8).value),
                    "regular": money(sheet.cell(row, 9).value),
                    "walk_in": money(sheet.cell(row, 10).value),
                }
                for row in range(2, 11)
            ],
            "merchandise": [
                {
                    "name": sheet.cell(row, 1).value.strip(),
                    "amount": money(sheet.cell(row, 3).value),
                }
                for row in range(11, 14)
            ],
            "discounts": [
                {
                    "name": sheet.cell(row, 1).value.strip(),
                    "amount": money(sheet.cell(row, 3).value),
                }
                for row in range(15, 19)
            ],
            "sales_breakdown": [
                {
                    "description": sheet.cell(row, 1).value.strip(),
                    "quantity": int(sheet.cell(row, 2).value),
                    "unit_price": money(sheet.cell(row, 3).value),
                    "total_amount": money(sheet.cell(row, 5).value),
                }
                for row in range(22, 27)
            ],
        }

    finally:
        workbook.close()


def import_data():
    report = load_finance_report()

    print("FINANCE REPORT VALIDATION: PASS")
    print(f"Early-bird revenue: PHP {report['early_bird']:,.2f}")
    print(f"Regular revenue: PHP {report['regular']:,.2f}")
    print(f"Walk-in revenue: PHP {report['walk_ins']:,.2f}")
    print(f"Reported total: PHP {report['reported_total']:,.2f}")

    with engine.begin() as connection:

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
                    VALUES (:event_name, 'Workshop')
                    RETURNING id
                """),
                {"event_name": EVENT_NAME}
            ).scalar_one()

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
                "filename": EXCEL_PATH.name,
                "source_type": SOURCE_TYPE,
            }
        ).scalar_one_or_none()

        if existing_import is not None:
            print("\nThis file has already been imported.")
            print(f"Existing import ID: {existing_import}")
            return

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
                    'pending'
                )
                RETURNING id
            """),
            {
                "event_id": event_id,
                "filename": EXCEL_PATH.name,
                "source_type": SOURCE_TYPE,
            }
        ).scalar_one()

        # 1. Consolidated financial summary
        connection.execute(
            text("""
                INSERT INTO workshop_finance_summary (
                    import_id,
                    early_bird_revenue,
                    regular_revenue,
                    walk_in_revenue,
                    reported_total
                )
                VALUES (
                    :import_id,
                    :early_bird,
                    :regular,
                    :walk_ins,
                    :reported_total
                )
            """),
            {
                "import_id": import_id,
                **report,
            }
        )

        # 2. Instructor allocations
        for item in report["instructors"]:
            connection.execute(
                text("""
                    INSERT INTO workshop_instructor_allocations (
                        import_id,
                        instructor_name,
                        early_bird_revenue,
                        regular_revenue,
                        walk_in_revenue,
                        reported_total
                    )
                    VALUES (
                        :import_id,
                        :name,
                        :early_bird,
                        :regular,
                        :walk_ins,
                        :total
                    )
                """),
                {"import_id": import_id, **item}
            )

        # 3. Package reference prices
        for item in report["package_prices"]:
            connection.execute(
                text("""
                    INSERT INTO workshop_package_prices (
                        import_id,
                        package_name,
                        early_bird_price,
                        regular_price,
                        walk_in_price
                    )
                    VALUES (
                        :import_id,
                        :name,
                        :early_bird,
                        :regular,
                        :walk_in
                    )
                """),
                {"import_id": import_id, **item}
            )

        # 4. Package revenue components
        # Each recorded channel amount is stored separately.
        for item in report["package_revenue"]:
            for channel in ("early_bird", "regular", "walk_ins"):
                amount = item[channel]

                if amount is not None:
                    connection.execute(
                        text("""
                            INSERT INTO workshop_finance (
                                import_id,
                                category,
                                revenue_amount,
                                category_type
                            )
                            VALUES (
                                :import_id,
                                :category,
                                :amount,
                                :category_type
                            )
                        """),
                        {
                            "import_id": import_id,
                            "category": item["name"],
                            "amount": amount,
                            "category_type": channel,
                        }
                    )

        # 5. Merchandise
        for item in report["merchandise"]:
            connection.execute(
                text("""
                    INSERT INTO workshop_merchandise (
                        import_id,
                        item_or_instructor,
                        revenue_amount
                    )
                    VALUES (
                        :import_id,
                        :name,
                        :amount
                    )
                """),
                {
                    "import_id": import_id,
                    "name": item["name"],
                    "amount": item["amount"],
                }
            )

        # 6. Discount-category amounts
        for item in report["discounts"]:
            connection.execute(
                text("""
                    INSERT INTO workshop_discounts (
                        import_id,
                        package_name,
                        recorded_amount
                    )
                    VALUES (
                        :import_id,
                        :name,
                        :amount
                    )
                """),
                {
                    "import_id": import_id,
                    "name": item["name"],
                    "amount": item["amount"],
                }
            )

        # 7. Nick Joseph item-level breakdown
        for item in report["sales_breakdown"]:
            connection.execute(
                text("""
                    INSERT INTO workshop_sales_breakdown (
                        import_id,
                        description,
                        quantity,
                        unit_price,
                        total_amount
                    )
                    VALUES (
                        :import_id,
                        :description,
                        :quantity,
                        :unit_price,
                        :total_amount
                    )
                """),
                {
                    "import_id": import_id,
                    **item,
                }
            )

        # Mark import completed only after all inserts succeed.
        connection.execute(
            text("""
                UPDATE data_imports
                SET import_status = 'completed'
                WHERE id = :import_id
            """),
            {"import_id": import_id}
        )

    print("\nSJSC IMPORT SUCCESSFUL")
    print(f"Event: {EVENT_NAME}")
    print(f"Import ID: {import_id}")
    print(f"Instructor records: {len(report['instructors'])}")
    print(f"Package price records: {len(report['package_prices'])}")
    print(f"Merchandise records: {len(report['merchandise'])}")
    print(f"Discount records: {len(report['discounts'])}")
    print(f"Sales breakdown records: {len(report['sales_breakdown'])}")
    print(f"Consolidated revenue: PHP {report['reported_total']:,.2f}")


if __name__ == "__main__":
    try:
        import_data()
    except Exception as error:
        print(f"\nIMPORT FAILED: {error}")
        raise
