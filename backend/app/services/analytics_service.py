
from decimal import Decimal

from sqlalchemy import text

from app.core.database import engine


def get_overview():
    competition_query = text("""
        SELECT
            COALESCE(SUM(ts.total_amount), 0) AS total_revenue,
            COALESCE(SUM(ts.number_of_orders), 0) AS total_orders,
            COALESCE(SUM(ts.number_of_tickets), 0) AS total_tickets
        FROM ticket_sales_daily ts
        JOIN data_imports di
            ON di.id = ts.import_id
        WHERE di.import_status = 'completed'
          AND di.source_type = 'ticketmelon_daily_sales'
    """)

    workshops_query = text("""
        SELECT
            COALESCE(SUM(fs.reported_total), 0) AS total_revenue
        FROM workshop_finance_summary fs
        JOIN data_imports di
            ON di.id = fs.import_id
        WHERE di.import_status = 'completed'
          AND di.source_type = 'sjsc_finance_report'
    """)

    with engine.connect() as connection:
        competition = connection.execute(
            competition_query
        ).mappings().one()

        workshops = connection.execute(
            workshops_query
        ).mappings().one()

    competition_revenue = Decimal(str(competition["total_revenue"]))
    workshops_revenue = Decimal(str(workshops["total_revenue"]))

    combined_revenue = competition_revenue + workshops_revenue

    return {
        "competition": {
            "event_name": "SJSC Competition",
            "total_revenue": float(competition_revenue),
            "total_orders": int(competition["total_orders"]),
            "total_tickets": int(competition["total_tickets"]),
        },
        "workshops": {
            "event_name": "SJSC Workshops",
            "total_revenue": float(workshops_revenue),
        },
        "combined": {
            "total_revenue": float(combined_revenue),
        },
    }


def get_event_comparison():
    overview = get_overview()

    competition = overview["competition"]
    workshops = overview["workshops"]

    total_revenue = Decimal(
        str(overview["combined"]["total_revenue"])
    )

    events = []

    for event in [competition, workshops]:
        revenue = Decimal(str(event["total_revenue"]))

        share = (
            (revenue / total_revenue) * 100
            if total_revenue > 0
            else Decimal("0")
        )

        events.append({
            "event_name": event["event_name"],
            "total_revenue": float(revenue),
            "revenue_share_percentage": round(float(share), 2),
        })

    events.sort(
        key=lambda event: event["total_revenue"],
        reverse=True
    )

    return {
        "total_revenue": float(total_revenue),
        "highest_revenue_event": (
            events[0]["event_name"] if events else None
        ),
        "events": events,
    }



def get_sales_trends():
    query = text("""
        SELECT
            ts.sales_date,
            COALESCE(SUM(ts.total_amount), 0) AS total_revenue,
            COALESCE(SUM(ts.number_of_orders), 0) AS total_orders,
            COALESCE(SUM(ts.number_of_tickets), 0) AS total_tickets
        FROM ticket_sales_daily ts
        JOIN data_imports di
            ON di.id = ts.import_id
        WHERE di.import_status = 'completed'
          AND di.source_type = 'ticketmelon_daily_sales'
        GROUP BY ts.sales_date
        ORDER BY ts.sales_date ASC
    """)

    with engine.connect() as connection:
        results = connection.execute(
            query
        ).mappings().all()

    daily_sales = []

    for row in results:
        daily_sales.append({
            "sales_date": row["sales_date"],
            "total_revenue": float(row["total_revenue"]),
            "total_orders": int(row["total_orders"]),
            "total_tickets": int(row["total_tickets"]),
        })

    total_revenue = sum(
        (Decimal(str(day["total_revenue"])) for day in daily_sales),
        Decimal("0.00")
    )

    total_orders = sum(
        day["total_orders"] for day in daily_sales
    )

    total_tickets = sum(
        day["total_tickets"] for day in daily_sales
    )

    # Revenue statistics
    highest_revenue_day = max(
        daily_sales,
        key=lambda day: day["total_revenue"],
        default=None
    )

    days_with_sales = [
        day for day in daily_sales
        if day["total_revenue"] > 0
    ]

    zero_sales_days = [
        day for day in daily_sales
        if day["total_revenue"] == 0
    ]

    lowest_revenue_day = min(
        days_with_sales,
        key=lambda day: day["total_revenue"],
        default=None
    )

    average_daily_revenue = (
        float(total_revenue) / len(daily_sales)
        if daily_sales else 0
    )

    average_revenue_per_order = (
        float(total_revenue) / total_orders
        if total_orders > 0 else 0
    )

    average_ticket_value = (
        float(total_revenue) / total_tickets
        if total_tickets > 0 else 0
    )

    return {
        "event_name": "SJSC Competition",

        "summary": {
            "total_revenue": float(total_revenue),
            "total_orders": total_orders,
            "total_tickets": total_tickets,
            "recorded_days": len(daily_sales),
            "days_with_sales": len(days_with_sales),
            "zero_sales_days": len(zero_sales_days),
        },

        "performance_metrics": {
            "average_daily_revenue": round(
                average_daily_revenue, 2
            ),
            "average_revenue_per_order": round(
                average_revenue_per_order, 2
            ),
            "average_ticket_value": round(
                average_ticket_value, 2
            ),
        },

        "highest_revenue_day": (
            highest_revenue_day
        ),

        "lowest_revenue_day": (
            lowest_revenue_day
        ),

        "zero_sales_dates": [
            day["sales_date"]
            for day in zero_sales_days
        ],

        "daily_sales": daily_sales,
    }


def get_workshop_analytics():
    summary_query = text("""
        SELECT
            COALESCE(SUM(fs.early_bird_revenue), 0) AS early_bird_revenue,
            COALESCE(SUM(fs.regular_revenue), 0) AS regular_revenue,
            COALESCE(SUM(fs.walk_in_revenue), 0) AS walk_in_revenue,
            COALESCE(SUM(fs.reported_total), 0) AS total_revenue
        FROM workshop_finance_summary fs
        JOIN data_imports di ON di.id = fs.import_id
        WHERE di.import_status = 'completed'
          AND di.source_type = 'sjsc_finance_report'
    """)

    finance_query = text("""
        SELECT
            wf.category,
            wf.category_type,
            SUM(wf.revenue_amount) AS revenue_amount
        FROM workshop_finance wf
        JOIN data_imports di ON di.id = wf.import_id
        WHERE di.import_status = 'completed'
          AND di.source_type = 'sjsc_finance_report'
        GROUP BY wf.category, wf.category_type
        ORDER BY wf.category
    """)

    package_query = text("""
        SELECT
            pp.package_name,
            pp.early_bird_price,
            pp.regular_price,
            pp.walk_in_price
        FROM workshop_package_prices pp
        JOIN data_imports di ON di.id = pp.import_id
        WHERE di.import_status = 'completed'
          AND di.source_type = 'sjsc_finance_report'
        ORDER BY pp.package_name
    """)

    merchandise_query = text("""
        SELECT
            wm.item_or_instructor,
            SUM(wm.revenue_amount) AS revenue_amount
        FROM workshop_merchandise wm
        JOIN data_imports di ON di.id = wm.import_id
        WHERE di.import_status = 'completed'
          AND di.source_type = 'sjsc_finance_report'
        GROUP BY wm.item_or_instructor
        ORDER BY wm.item_or_instructor
    """)

    discounts_query = text("""
        SELECT
            wd.package_name,
            SUM(wd.recorded_amount) AS recorded_amount
        FROM workshop_discounts wd
        JOIN data_imports di ON di.id = wd.import_id
        WHERE di.import_status = 'completed'
          AND di.source_type = 'sjsc_finance_report'
        GROUP BY wd.package_name
        ORDER BY wd.package_name
    """)

    sales_query = text("""
        SELECT
            ws.description,
            SUM(ws.quantity) AS quantity,
            ws.unit_price,
            SUM(ws.total_amount) AS total_amount
        FROM workshop_sales_breakdown ws
        JOIN data_imports di ON di.id = ws.import_id
        WHERE di.import_status = 'completed'
          AND di.source_type = 'sjsc_finance_report'
        GROUP BY ws.description, ws.unit_price
        ORDER BY ws.description
    """)

    instructor_query = text("""
        SELECT
            ia.instructor_name,
            ia.early_bird_revenue,
            ia.regular_revenue,
            ia.walk_in_revenue,
            ia.reported_total
        FROM workshop_instructor_allocations ia
        JOIN data_imports di ON di.id = ia.import_id
        WHERE di.import_status = 'completed'
          AND di.source_type = 'sjsc_finance_report'
        ORDER BY ia.instructor_name
    """)

    with engine.connect() as connection:
        summary = connection.execute(
            summary_query
        ).mappings().one()

        finance_rows = connection.execute(
            finance_query
        ).mappings().all()

        package_rows = connection.execute(
            package_query
        ).mappings().all()

        merchandise_rows = connection.execute(
            merchandise_query
        ).mappings().all()

        discount_rows = connection.execute(
            discounts_query
        ).mappings().all()

        sales_rows = connection.execute(
            sales_query
        ).mappings().all()

        instructor_rows = connection.execute(
            instructor_query
        ).mappings().all()

    def to_float(value):
        return float(value or 0)

    # --------------------------------------------------
    # INSTRUCTOR GROUPS
    # --------------------------------------------------

    instructor_schedules = {
        "Ashvinder Singh": "1:00 PM - 2:30 PM",
        "Afrodite": "2:45 PM - 4:15 PM",
        "Nica Santos": "4:30 PM - 6:00 PM",
        "Nick Joseph": "7:00 PM - 8:30 PM",
        "Adrian Vendiola": "8:45 PM - 10:15 PM",
    }

    local_instructors = []
    international_instructors = []

    for row in instructor_rows:
        full_name = row["instructor_name"]

        instructor_name = next(
            (
                name for name in instructor_schedules
                if full_name.startswith(name)
            ),
            full_name
        )

        instructor_data = {
            "instructor_name": instructor_name,
            "schedule": instructor_schedules.get(
                instructor_name,
                "Schedule not specified"
            ),
            "early_bird_revenue": to_float(
                row["early_bird_revenue"]
            ),
            "regular_revenue": to_float(
                row["regular_revenue"]
            ),
            "walk_in_revenue": to_float(
                row["walk_in_revenue"]
            ),
            "source_reported_total": to_float(
                row["reported_total"]
            ),
        }

        if instructor_name in [
            "Ashvinder Singh",
            "Afrodite",
            "Nica Santos"
        ]:
            local_instructors.append(instructor_data)
        else:
            international_instructors.append(instructor_data)

    # --------------------------------------------------
    # PACKAGE PRICING
    # --------------------------------------------------

    single_class_pricing = []
    bundle_pricing = []

    discounted_package_names = {
        "DISCOUNTED Local Class Pass": "Local Class Pass",
        "DISCOUNTED International Class": "International Class Pass",
        "DISCOUNTED All In Bundle": "All In Bundle",
    }

    discounted_prices = {}

    for row in package_rows:
        package_name = row["package_name"]

        if package_name in discounted_package_names:
            normalized_name = discounted_package_names[package_name]

            discounted_prices[normalized_name] = to_float(
                row["regular_price"]
            )

    for row in package_rows:
        package_name = row["package_name"]

        # Do not include discounted reference rows twice.
        if package_name in discounted_package_names:
            continue

        pricing_data = {
    "package_name": package_name,
    "early_bird_price": (
        float(row["early_bird_price"])
        if row["early_bird_price"] is not None
        else None
    ),
    "regular_price": (
        float(row["regular_price"])
        if row["regular_price"] is not None
        else None
    ),
    "walk_in_price": (
        float(row["walk_in_price"])
        if row["walk_in_price"] is not None
        else None
    ),
}

        if package_name in [
            "Local Class",
            "International Class"
        ]:
            single_class_pricing.append(pricing_data)

        else:
            normalized_name = package_name

            if package_name == "Local Class w/ Merch":
                normalized_name = "Local Class Pass with Merch"

            pricing_data["package_name"] = normalized_name
            pricing_data["discounted_price"] = discounted_prices.get(
                normalized_name
            )

            bundle_pricing.append(pricing_data)

    # --------------------------------------------------
    # OTHER FINANCIAL RECORDS
    # --------------------------------------------------

    return {
        "event_name": "SJSC Workshops",

        "revenue_summary": {
            "early_bird": to_float(
                summary["early_bird_revenue"]
            ),
            "regular": to_float(
                summary["regular_revenue"]
            ),
            "walk_ins": to_float(
                summary["walk_in_revenue"]
            ),
            "total_revenue": to_float(
                summary["total_revenue"]
            ),
        },

        "instructors": {
            "local": local_instructors,
            "international": international_instructors,
            "note": (
                "Instructor reported totals are source-reported "
                "figures and are not additional workshop revenue."
            ),
        },

        "single_class_pricing": single_class_pricing,

        "bundle_pricing": bundle_pricing,

        "package_revenue_breakdown": [
            {
                "category": row["category"],
                "category_type": row["category_type"],
                "revenue_amount": to_float(
                    row["revenue_amount"]
                ),
            }
            for row in finance_rows
        ],

        "with_merch": [
            {
                "item_or_instructor": row["item_or_instructor"],
                "revenue_amount": to_float(
                    row["revenue_amount"]
                ),
            }
            for row in merchandise_rows
        ],

        "discount_records": [
            {
                "package_name": row["package_name"],
                "recorded_amount": to_float(
                    row["recorded_amount"]
                ),
            }
            for row in discount_rows
        ],

        "nick_joseph_sales_breakdown": [
            {
                "description": row["description"],
                "quantity": int(row["quantity"] or 0),
                "unit_price": to_float(row["unit_price"]),
                "total_amount": to_float(row["total_amount"]),
            }
            for row in sales_rows
        ],

        "data_notes": [
            "Pricing values are reference prices, not actual revenue.",
            "The consolidated workshop revenue is reported separately.",
            "The sales breakdown contains Nick Joseph records only.",
            "With-merch records are shown separately from consolidated revenue.",
        ],
    }