
import { useEffect, useState } from "react";
import {
  Activity,
  CalendarDays,
  PhilippinePeso,
  ShoppingCart,
  Ticket,
  LayoutDashboard,
  Users,
  Shirt,
  Tag,
  ArrowLeft,
} from "lucide-react";

import {
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Bar,
} from "recharts";

import api from "./services/api";
import brandLogo from "./assets/sjsc/sjsc-white.png";
import "./App.css";

// --------------------------------------------------
// TYPES
// --------------------------------------------------

interface OverviewData {
  competition: {
    event_name: string;
    total_revenue: number;
    total_orders: number;
    total_tickets: number;
  };
  workshops: {
    event_name: string;
    total_revenue: number;
  };
  combined: {
    total_revenue: number;
  };
}

interface EventComparison {
  total_revenue: number;
  highest_revenue_event: string | null;
  events: {
    event_name: string;
    total_revenue: number;
    revenue_share_percentage: number;
  }[];
}

interface DailySalesItem {
  sales_date: string;
  total_revenue: number;
  total_orders: number;
  total_tickets: number;
}

interface SalesTrends {
  event_name: string;
  summary: {
    total_revenue: number;
    total_orders: number;
    total_tickets: number;
    recorded_days: number;
    days_with_sales: number;
    zero_sales_days: number;
  };
  performance_metrics: {
    average_daily_revenue: number;
    average_revenue_per_order: number;
    average_ticket_value: number;
  };
  highest_revenue_day: DailySalesItem | null;
  lowest_revenue_day: DailySalesItem | null;
  zero_sales_dates: string[];
  daily_sales: DailySalesItem[];
}

interface WorkshopInstructor {
  instructor_name: string;
  schedule: string;
  early_bird_revenue: number;
  regular_revenue: number;
  walk_in_revenue: number;
  source_reported_total: number;
}

interface WorkshopPricing {
  package_name: string;
  early_bird_price: number;
  regular_price: number;
  walk_in_price: number;
  discounted_price: number | null;
}

interface WorkshopAnalytics {
  event_name: string;

  revenue_summary: {
    early_bird: number;
    regular: number;
    walk_ins: number;
    total_revenue: number;
  };

  instructors: {
    local: WorkshopInstructor[];
    international: WorkshopInstructor[];
    note: string;
  };

  single_class_pricing: WorkshopPricing[];
  bundle_pricing: WorkshopPricing[];

  package_revenue_breakdown: {
    category: string;
    category_type: string;
    revenue_amount: number;
  }[];

  with_merch: {
    item_or_instructor: string;
    revenue_amount: number;
  }[];

  discount_records: {
    package_name: string;
    recorded_amount: number;
  }[];

  nick_joseph_sales_breakdown: {
    description: string;
    quantity: number;
    unit_price: number;
    total_amount: number;
  }[];

  data_notes: string[];
}

// --------------------------------------------------
// HELPERS
// --------------------------------------------------

const peso = (amount: number | null | undefined) =>
  new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
    maximumFractionDigits: 2,
  }).format(amount ?? 0);

const formatPrice = (amount: number | null | undefined) => {
  if (amount === null || amount === undefined || amount === 0) {
    return "N/A";
  }

  return peso(amount);
};

const formatDate = (date: string) =>
  new Date(`${date}T00:00:00`).toLocaleDateString("en-PH", {
    month: "long",
    day: "numeric",
    year: "numeric",
  });


// --------------------------------------------------
// MAIN APP
// --------------------------------------------------

function App() {
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [comparison, setComparison] = useState<EventComparison | null>(null);
  const [trends, setTrends] = useState<SalesTrends | null>(null);
  const [workshops, setWorkshops] = useState<WorkshopAnalytics | null>(null);

  const [activePage, setActivePage] = useState<
    "dashboard" | "workshops" | "competition"
  >("dashboard");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError("");

        const [
          overviewResponse,
          comparisonResponse,
          trendsResponse,
          workshopResponse,
        ] = await Promise.all([
          api.get<OverviewData>("/api/analytics/overview"),
          api.get<EventComparison>("/api/analytics/events"),
          api.get<SalesTrends>("/api/analytics/sales-trends"),
          api.get<WorkshopAnalytics>("/api/analytics/workshops"),
        ]);

        setOverview(overviewResponse.data);
        setComparison(comparisonResponse.data);
        setTrends(trendsResponse.data);
        setWorkshops(workshopResponse.data);
      } catch (err) {
        console.error("Dashboard loading error:", err);

        setError(
          "Unable to load analytics data. Check that the backend is running and all analytics endpoints are working."
        );
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  if (loading) {
    return (
      <main className="loading-screen">
        <Activity size={32} />
        <p>Loading EventFlow analytics...</p>
      </main>
    );
  }

  if (error || !overview || !comparison || !trends || !workshops) {
    return (
      <main className="loading-screen">
        <p className="error-message">
          {error || "No dashboard data available."}
        </p>
      </main>
    );
  }

  const dailyChartData = (trends.daily_sales ?? []).map((day) => ({
    ...day,
    displayDate: formatDate(day.sales_date).replace(", 2026", ""),
  }));

  const eventColors = ["#b44225", "#6e624c"];

  return (
    <div className="app-layout">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="brand">
          <img src={brandLogo} alt="Road to Summer Jam Showcase Competition, Philippine Qualifier" />
        </div>

        <nav className="nav-section" aria-label="Event analytics">

          <button
            type="button"
            className={`nav-item ${
              activePage === "dashboard" ? "active" : ""
            }`}
            aria-current={activePage === "dashboard" ? "page" : undefined}
            onClick={() => setActivePage("dashboard")}
          >
            <LayoutDashboard size={18} />
            <span>Dashboard</span>
          </button>

          <button
            type="button"
            className={`nav-item ${
              activePage === "competition" ? "active" : ""
            }`}
            aria-current={activePage === "competition" ? "page" : undefined}
            onClick={() => setActivePage("competition")}
          >
            <Ticket size={18} />
            <span>Competition</span>
          </button>

          <button
            type="button"
            className={`nav-item ${
              activePage === "workshops" ? "active" : ""
            }`}
            aria-current={activePage === "workshops" ? "page" : undefined}
            onClick={() => setActivePage("workshops")}
          >
            <Users size={18} />
            <span>Workshops</span>
          </button>

        </nav>

        <div className="sidebar-footer">
          <span className="status-dot" />
          Data connected
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="main-content">
        {activePage === "dashboard" ? (
          <DashboardPage
            overview={overview}
            comparison={comparison}
            trends={trends}
            dailyChartData={dailyChartData}
            eventColors={eventColors}
          />
        ) : activePage === "workshops" ? (
          <WorkshopPage
            workshops={workshops}
            onBack={() => setActivePage("dashboard")}
          />
        ) : (
          <CompetitionPage
            trends={trends}
            onBack={() => setActivePage("dashboard")}
          />
        )}
      </main>
    </div>
  );
}

// --------------------------------------------------
// DASHBOARD PAGE
// --------------------------------------------------

function DashboardPage({
  overview,
  comparison,
  trends,
  dailyChartData,
  eventColors,
}: {
  overview: OverviewData;
  comparison: EventComparison;
  trends: SalesTrends;
  dailyChartData: (DailySalesItem & { displayDate: string })[];
  eventColors: string[];
}) {
  const events = comparison.events ?? [];

  return (
    <>
      <header className="topbar overview-hero">
        <div>
          <p className="eyebrow">SUMMER JAM SHOWDOWN</p>
          <h1>Analytics Dashboard</h1>
          <p className="subtitle">
            Competition ticket sales and workshop revenue.
          </p>
        </div>

        <div className="date-label">
          <CalendarDays size={16} />
          Data through October 24, 2026
        </div>
      </header>

      {/* KPI CARDS */}
      <section className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-heading">
            <span>Total Revenue</span>
            <div className="kpi-icon blue">
              <PhilippinePeso size={20} />
            </div>
          </div>

          <h2>{peso(overview.combined.total_revenue)}</h2>
          <p>Combined revenue across all events</p>
        </div>

        <div className="kpi-card">
          <div className="kpi-heading">
            <span>Total Events</span>
            <div className="kpi-icon purple">
              <CalendarDays size={20} />
            </div>
          </div>

          <h2>{events.length}</h2>
          <p>Events with imported financial data</p>
        </div>

        <div className="kpi-card">
          <div className="kpi-heading">
            <span>Total Orders</span>
            <div className="kpi-icon orange">
              <ShoppingCart size={20} />
            </div>
          </div>

          <h2>
            {(overview.competition.total_orders ?? 0).toLocaleString()}
          </h2>
          <p>SJSC Competition orders</p>
        </div>

        <div className="kpi-card">
          <div className="kpi-heading">
            <span>Tickets Sold</span>
            <div className="kpi-icon green">
              <Ticket size={20} />
            </div>
          </div>

          <h2>
            {(overview.competition.total_tickets ?? 0).toLocaleString()}
          </h2>
          <p>SJSC Competition tickets</p>
        </div>
      </section>

      {/* CHARTS */}
      <section className="chart-grid">
        <div className="panel sales-panel">
          <div className="panel-heading">
            <div>
              <h3>Daily Sales Revenue</h3>
              <p>SJSC Competition revenue performance over time</p>
            </div>
          </div>

          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={dailyChartData}>
                <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />

                <XAxis
                  dataKey="displayDate"
                  tick={{ fontSize: 11 }}
                  interval="preserveStartEnd"
                />

                <YAxis
                  tickFormatter={(value) =>
                    `₱${Number(value).toLocaleString("en-PH")}`
                  }
                  tick={{ fontSize: 11 }}
                  width={85}
                />

                <Tooltip
                  formatter={(value) => peso(Number(value))}
                  labelFormatter={(label) => `Date: ${label}`}
                />

                <Line
                  type="monotone"
                  dataKey="total_revenue"
                  name="Revenue"
                  stroke="var(--chart-accent)"
                  strokeWidth={3}
                  dot={false}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel">
          <div className="panel-heading">
            <div>
              <h3>Revenue by Event</h3>
              <p>Comparison of event revenue</p>
            </div>
          </div>

          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={events}
                layout="vertical"
                margin={{ left: 12, right: 20 }}
              >
                <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" horizontal={false} />

                <XAxis
                  type="number"
                  tickFormatter={(value) =>
                    `₱${Number(value).toLocaleString("en-PH")}`
                  }
                  tick={{ fontSize: 10 }}
                />

                <YAxis
                  type="category"
                  dataKey="event_name"
                  width={145}
                  tick={{ fontSize: 11 }}
                />

                <Tooltip formatter={(value) => peso(Number(value))} />

                <Bar
                  dataKey="total_revenue"
                  name="Revenue"
                  barSize={24}
                  radius={[0, 5, 5, 0]}
                >
                  {events.map((event, index) => (
                    <Cell
                      key={event.event_name}
                      fill={eventColors[index % eventColors.length]}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      {/* CONTRIBUTION AND HIGHLIGHTS */}
      <section className="bottom-grid">
        <div className="panel">
          <div className="panel-heading">
            <div>
              <h3>Revenue Contribution</h3>
              <p>Percentage share of combined revenue</p>
            </div>
          </div>

          <div className="chart-container pie-container">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={events}
                  dataKey="total_revenue"
                  nameKey="event_name"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={91}
                  paddingAngle={2}
                  label={({ percent }) =>
                    `${((percent ?? 0) * 100).toFixed(1)}%`
                  }
                >
                  {events.map((event, index) => (
                    <Cell
                      key={event.event_name}
                      fill={eventColors[index % eventColors.length]}
                    />
                  ))}
                </Pie>

                <Tooltip formatter={(value) => peso(Number(value))} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel performance-panel">
          <div className="panel-heading">
            <div>
              <h3>Sales Highlights</h3>
              <p>Important performance indicators</p>
            </div>
          </div>

          <div className="highlight-item">
            <span>Highest sales date</span>
            <strong>
              {trends.highest_revenue_day
                ? formatDate(trends.highest_revenue_day.sales_date)
                : "N/A"}
            </strong>
          </div>

          <div className="highlight-item">
            <span>Revenue on highest sales date</span>
            <strong>
              {peso(trends.highest_revenue_day?.total_revenue)}
            </strong>
          </div>

          <div className="highlight-item">
            <span>Highest event contribution</span>
            <strong>
              {events[0]?.revenue_share_percentage ?? 0}%
            </strong>
          </div>

          <div className="highlight-item">
            <span>Average daily revenue</span>
            <strong>
              {peso(trends.performance_metrics.average_daily_revenue)}
            </strong>
          </div>

          <div className="highlight-item">
            <span>Days with sales</span>
            <strong>
              {trends.summary.days_with_sales} / {trends.summary.recorded_days}
            </strong>
          </div>
        </div>
      </section>
    </>
  );
}

// --------------------------------------------------
// WORKSHOPS PAGE
// --------------------------------------------------

function WorkshopPage({
  workshops,
  onBack,
}: {
  workshops: WorkshopAnalytics;
  onBack: () => void;
}) {
  // Combine local and international instructors safely.
  const instructors = [
    ...(workshops.instructors?.local ?? []),
    ...(workshops.instructors?.international ?? []),
  ];

  const singleClassPricing = workshops.single_class_pricing ?? [];
  const bundlePricing = workshops.bundle_pricing ?? [];
  const packageRevenue = workshops.package_revenue_breakdown ?? [];
  const merchandise = workshops.with_merch ?? [];
  const discounts = workshops.discount_records ?? [];
  const salesBreakdown = workshops.nick_joseph_sales_breakdown ?? [];
  const dataNotes = workshops.data_notes ?? [];

  const revenueSummary = workshops.revenue_summary ?? {
    early_bird: 0,
    regular: 0,
    walk_ins: 0,
    total_revenue: 0,
  };

  return (
    <>
      <header className="topbar">
        <div>
          <button type="button" onClick={onBack} className="back-button">
            <ArrowLeft size={16} />
            Back to Dashboard
          </button>

          <p className="eyebrow">EVENT MANAGEMENT / WORKSHOPS</p>
          <h1>{workshops.event_name}</h1>

          <p className="subtitle">
            Workshop revenue, instructor allocations, pricing, and financial records.
          </p>
        </div>

        <div className="date-label">
          <CalendarDays size={16} />
          Workshop Financial Report
        </div>
      </header>

      {/* REVENUE SUMMARY */}
      <section className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-heading">
            <span>Total Workshop Revenue</span>
            <div className="kpi-icon blue">
              <PhilippinePeso size={20} />
            </div>
          </div>

          <h2>{peso(revenueSummary.total_revenue)}</h2>
          <p>Consolidated workshop revenue</p>
        </div>

        <div className="kpi-card">
          <div className="kpi-heading">
            <span>Early Bird Revenue</span>
            <div className="kpi-icon purple">
              <Ticket size={20} />
            </div>
          </div>

          <h2>{peso(revenueSummary.early_bird)}</h2>
          <p>Early bird payment category</p>
        </div>

        <div className="kpi-card">
          <div className="kpi-heading">
            <span>Regular Revenue</span>
            <div className="kpi-icon orange">
              <ShoppingCart size={20} />
            </div>
          </div>

          <h2>{peso(revenueSummary.regular)}</h2>
          <p>Regular payment category</p>
        </div>

        <div className="kpi-card">
          <div className="kpi-heading">
            <span>Walk-in Revenue</span>
            <div className="kpi-icon green">
              <Users size={20} />
            </div>
          </div>

          <h2>{peso(revenueSummary.walk_ins)}</h2>
          <p>Walk-in payment category</p>
        </div>
      </section>

      {/* INSTRUCTOR ALLOCATIONS */}
      <section className="workshop-section">
        <div className="section-heading">
          <div>
            <h2>Instructor Allocations</h2>
            <p>Financial figures recorded for each instructor</p>
          </div>
        </div>

        <div className="panel workshop-panel">
          <div className="table-wrapper">
            <table className="workshop-table">
              <thead>
                <tr>
                  <th>Instructor</th>
                  <th>Schedule</th>
                  <th>Early Bird</th>
                  <th>Regular</th>
                  <th>Walk-in</th>
                  <th>Source-reported Total</th>
                </tr>
              </thead>

              <tbody>
                {instructors.map((item, index) => (
                  <tr key={`${item.instructor_name}-${index}`}>
                    <td><strong>{item.instructor_name}</strong></td>
                    <td>{item.schedule}</td>
                    <td>{peso(item.early_bird_revenue)}</td>
                    <td>{peso(item.regular_revenue)}</td>
                    <td>{peso(item.walk_in_revenue)}</td>
                    <td>
                      <strong>{peso(item.source_reported_total)}</strong>
                    </td>
                  </tr>
                ))}

                {instructors.length === 0 && (
                  <tr>
                    <td colSpan={6}>No instructor records available.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <p className="data-note">
            {workshops.instructors?.note ??
              "Instructor reported totals are displayed separately from consolidated workshop revenue."}
          </p>
        </div>
      </section>

      {/* SINGLE CLASS PRICING */}
      <section className="workshop-section">
        <div className="section-heading">
          <div>
            <h2>Single Class Pricing</h2>
            <p>Reference prices for individual workshop classes</p>
          </div>
        </div>

        <div className="panel workshop-panel">
          <div className="table-wrapper">
            <table className="workshop-table">
              <thead>
                <tr>
                  <th>Class</th>
                  <th>Early Bird</th>
                  <th>Regular</th>
                  <th>Walk-in</th>
                </tr>
              </thead>

              <tbody>
                {singleClassPricing.map((item, index) => (
                  <tr key={`${item.package_name}-${index}`}>
                    <td><strong>{item.package_name}</strong></td>
                    <td>{formatPrice(item.early_bird_price)}</td>
                    <td>{formatPrice(item.regular_price)}</td>
                    <td>{formatPrice(item.walk_in_price)}</td>
                  </tr>
                ))}

                {singleClassPricing.length === 0 && (
                  <tr>
                    <td colSpan={4}>
                      No single-class pricing records available.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* BUNDLE PRICING */}
      <section className="workshop-section">
        <div className="section-heading">
          <div>
            <h2>Bundle Pricing</h2>
            <p>Reference prices for workshop packages and class passes</p>
          </div>
        </div>

        <div className="panel workshop-panel">
          <div className="table-wrapper">
            <table className="workshop-table">
              <thead>
                <tr>
                  <th>Package</th>
                  <th>Early Bird</th>
                  <th>Regular</th>
                  <th>Walk-in</th>
                  <th>Discounted Price</th>
                </tr>
              </thead>

              <tbody>
                {bundlePricing.map((item, index) => (
                  <tr key={`${item.package_name}-${index}`}>
                    <td><strong>{item.package_name}</strong></td>
                    <td>{formatPrice(item.early_bird_price)}</td>
                    <td>{formatPrice(item.regular_price)}</td>
                    <td>{formatPrice(item.walk_in_price)}</td>
                    <td>{formatPrice(item.discounted_price)}</td>
                  </tr>
                ))}

                {bundlePricing.length === 0 && (
                  <tr>
                    <td colSpan={5}>No bundle pricing records available.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* PACKAGE REVENUE BREAKDOWN */}
      <section className="workshop-section">
        <div className="section-heading">
          <div>
            <h2>Package Revenue Breakdown</h2>
            <p>Recorded package revenue by payment category</p>
          </div>
        </div>

        <div className="panel workshop-panel">
          <div className="table-wrapper">
            <table className="workshop-table">
              <thead>
                <tr>
                  <th>Package</th>
                  <th>Payment Category</th>
                  <th>Recorded Revenue</th>
                </tr>
              </thead>

              <tbody>
                {packageRevenue.map((item, index) => (
                  <tr key={`${item.category}-${item.category_type}-${index}`}>
                    <td><strong>{item.category}</strong></td>
                    <td>{item.category_type.replace("_", " ")}</td>
                    <td>{peso(item.revenue_amount)}</td>
                  </tr>
                ))}

                {packageRevenue.length === 0 && (
                  <tr>
                    <td colSpan={3}>No package revenue records available.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* ADDITIONAL FINANCIAL RECORDS */}
      <section className="workshop-section">
        <div className="section-heading">
          <div>
            <h2>Additional Financial Records</h2>
            <p>Other entries from the workshop financial report</p>
          </div>
        </div>

        <div className="workshop-detail-grid">
          {/* MERCHANDISE */}
          <div className="panel workshop-panel">
            <div className="panel-heading">
              <div>
                <h3><Shirt size={17} /> With-Merch Records</h3>
                <p>Recorded amounts associated with these entries</p>
              </div>
            </div>

            {merchandise.map((item, index) => (
              <div
                className="highlight-item"
                key={`${item.item_or_instructor}-${index}`}
              >
                <span>{item.item_or_instructor}</span>
                <strong>{peso(item.revenue_amount)}</strong>
              </div>
            ))}

            {merchandise.length === 0 && (
              <p className="data-note">No merchandise records available.</p>
            )}
          </div>

          {/* DISCOUNTS */}
          <div className="panel workshop-panel">
            <div className="panel-heading">
              <div>
                <h3><Tag size={17} /> Discount Records</h3>
                <p>Amounts recorded in the discount section</p>
              </div>
            </div>

            {discounts.map((item, index) => (
              <div
                className="highlight-item"
                key={`${item.package_name}-${index}`}
              >
                <span>{item.package_name}</span>
                <strong>{peso(item.recorded_amount)}</strong>
              </div>
            ))}

            {discounts.length === 0 && (
              <p className="data-note">No discount records available.</p>
            )}
          </div>
        </div>
      </section>

      {/* NICK JOSEPH SALES BREAKDOWN */}
      <section className="workshop-section">
        <div className="section-heading">
          <div>
            <h2>Nick Joseph Sales Breakdown</h2>
            <p>
              Partial sales records only, not the complete workshop sales report
            </p>
          </div>
        </div>

        <div className="panel workshop-panel">
          <div className="table-wrapper">
            <table className="workshop-table">
              <thead>
                <tr>
                  <th>Description</th>
                  <th>Quantity</th>
                  <th>Unit Price</th>
                  <th>Total Amount</th>
                </tr>
              </thead>

              <tbody>
                {salesBreakdown.map((item, index) => (
                  <tr key={`${item.description}-${index}`}>
                    <td>{item.description}</td>
                    <td>{item.quantity}</td>
                    <td>{peso(item.unit_price)}</td>
                    <td><strong>{peso(item.total_amount)}</strong></td>
                  </tr>
                ))}

                {salesBreakdown.length === 0 && (
                  <tr>
                    <td colSpan={4}>
                      No sales breakdown records available.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* DATA NOTES */}
      <section className="workshop-section">
        <div className="panel workshop-panel">
          <div className="panel-heading">
            <div>
              <h3>Data Notes</h3>
              <p>Important context for interpreting the financial records</p>
            </div>
          </div>

          <ul className="data-notes-list">
            {dataNotes.map((note, index) => (
              <li key={index}>{note}</li>
            ))}
          </ul>
        </div>
      </section>
    </>
  );
}

// --------------------------------------------------
// SJSC COMPETITION PAGE
// --------------------------------------------------

function CompetitionPage({
  trends,
  onBack,
}: {
  trends: SalesTrends;
  onBack: () => void;
}) {
  const dailySales = trends.daily_sales ?? [];
  const zeroSalesDates = trends.zero_sales_dates ?? [];

  const dailyChartData = dailySales.map((day) => ({
    ...day,
    displayDate: formatDate(day.sales_date).replace(", 2026", ""),
  }));

  return (
    <>
      <header className="topbar">
        <div>
          <button type="button" onClick={onBack} className="back-button">
            <ArrowLeft size={16} />
            Back to Dashboard
          </button>

          <p className="eyebrow">EVENT MANAGEMENT / COMPETITION</p>
          <h1>{trends.event_name}</h1>

          <p className="subtitle">
            Ticket sales, daily revenue, and competition performance.
          </p>
        </div>

        <div className="date-label">
          <CalendarDays size={16} />
          September 2 – October 24, 2026
        </div>
      </header>

      {/* COMPETITION SUMMARY */}
      <section className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-heading">
            <span>Total Revenue</span>
            <div className="kpi-icon blue">
              <PhilippinePeso size={20} />
            </div>
          </div>

          <h2>{peso(trends.summary.total_revenue)}</h2>
          <p>Total recorded competition revenue</p>
        </div>

        <div className="kpi-card">
          <div className="kpi-heading">
            <span>Total Orders</span>
            <div className="kpi-icon purple">
              <ShoppingCart size={20} />
            </div>
          </div>

          <h2>{trends.summary.total_orders.toLocaleString()}</h2>
          <p>Recorded Ticketmelon orders</p>
        </div>

        <div className="kpi-card">
          <div className="kpi-heading">
            <span>Tickets Sold</span>
            <div className="kpi-icon green">
              <Ticket size={20} />
            </div>
          </div>

          <h2>{trends.summary.total_tickets.toLocaleString()}</h2>
          <p>Total recorded tickets</p>
        </div>

        <div className="kpi-card">
          <div className="kpi-heading">
            <span>Recorded Days</span>
            <div className="kpi-icon orange">
              <CalendarDays size={20} />
            </div>
          </div>

          <h2>{trends.summary.recorded_days}</h2>
          <p>Days in the sales dataset</p>
        </div>
      </section>

      {/* PERFORMANCE METRICS */}
      <section className="kpi-grid">
        <div className="kpi-card">
          <span>Average Daily Revenue</span>
          <h2>{peso(trends.performance_metrics.average_daily_revenue)}</h2>
          <p>Average across recorded days</p>
        </div>

        <div className="kpi-card">
          <span>Average Revenue per Order</span>
          <h2>{peso(trends.performance_metrics.average_revenue_per_order)}</h2>
          <p>Revenue divided by orders</p>
        </div>

        <div className="kpi-card">
          <span>Average Ticket Value</span>
          <h2>{peso(trends.performance_metrics.average_ticket_value)}</h2>
          <p>Revenue divided by tickets</p>
        </div>

        <div className="kpi-card">
          <span>Days with Sales</span>
          <h2>
            {trends.summary.days_with_sales} / {trends.summary.recorded_days}
          </h2>
          <p>
            {trends.summary.zero_sales_days} days with zero recorded sales
          </p>
        </div>
      </section>

      {/* DAILY REVENUE CHART */}
      <section className="workshop-section">
        <div className="panel workshop-panel">
          <div className="panel-heading">
            <div>
              <h3>Daily Revenue Trend</h3>
              <p>Competition revenue from September 2 to October 24, 2026</p>
            </div>
          </div>

          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={dailyChartData}>
                <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />

                <XAxis
                  dataKey="displayDate"
                  tick={{ fontSize: 11 }}
                  interval="preserveStartEnd"
                />

                <YAxis
                  tickFormatter={(value) =>
                    `₱${Number(value).toLocaleString("en-PH")}`
                  }
                  tick={{ fontSize: 11 }}
                  width={85}
                />

                <Tooltip
                  formatter={(value) => peso(Number(value))}
                  labelFormatter={(label) => `Date: ${label}`}
                />

                <Line
                  type="monotone"
                  dataKey="total_revenue"
                  name="Revenue"
                  stroke="var(--chart-accent)"
                  strokeWidth={3}
                  dot={false}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      {/* HIGHEST AND LOWEST DAYS */}
      <section className="bottom-grid">
        <div className="panel performance-panel">
          <div className="panel-heading">
            <div>
              <h3>Highest Revenue Day</h3>
              <p>Best recorded sales performance</p>
            </div>
          </div>

          {trends.highest_revenue_day ? (
            <>
              <div className="highlight-item">
                <span>Date</span>
                <strong>
                  {formatDate(trends.highest_revenue_day.sales_date)}
                </strong>
              </div>

              <div className="highlight-item">
                <span>Revenue</span>
                <strong>
                  {peso(trends.highest_revenue_day.total_revenue)}
                </strong>
              </div>

              <div className="highlight-item">
                <span>Orders</span>
                <strong>{trends.highest_revenue_day.total_orders}</strong>
              </div>

              <div className="highlight-item">
                <span>Tickets</span>
                <strong>{trends.highest_revenue_day.total_tickets}</strong>
              </div>
            </>
          ) : (
            <p>No highest-revenue day available.</p>
          )}
        </div>

        <div className="panel performance-panel">
          <div className="panel-heading">
            <div>
              <h3>Lowest Revenue Day</h3>
              <p>Lowest day with recorded sales</p>
            </div>
          </div>

          {trends.lowest_revenue_day ? (
            <>
              <div className="highlight-item">
                <span>Date</span>
                <strong>
                  {formatDate(trends.lowest_revenue_day.sales_date)}
                </strong>
              </div>

              <div className="highlight-item">
                <span>Revenue</span>
                <strong>
                  {peso(trends.lowest_revenue_day.total_revenue)}
                </strong>
              </div>

              <div className="highlight-item">
                <span>Orders</span>
                <strong>{trends.lowest_revenue_day.total_orders}</strong>
              </div>

              <div className="highlight-item">
                <span>Tickets</span>
                <strong>{trends.lowest_revenue_day.total_tickets}</strong>
              </div>
            </>
          ) : (
            <p>No lowest-revenue day available.</p>
          )}
        </div>
      </section>

      {/* DAILY SALES TABLE */}
      <section className="workshop-section">
        <div className="section-heading">
          <div>
            <h2>Daily Sales Records</h2>
            <p>
              All recorded competition sales dates, including zero-sales days
            </p>
          </div>
        </div>

        <div className="panel workshop-panel">
          <div className="table-wrapper">
            <table className="workshop-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Revenue</th>
                  <th>Orders</th>
                  <th>Tickets</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {dailySales.map((day) => (
                  <tr key={day.sales_date}>
                    <td>{formatDate(day.sales_date)}</td>
                    <td><strong>{peso(day.total_revenue)}</strong></td>
                    <td>{day.total_orders}</td>
                    <td>{day.total_tickets}</td>
                    <td>
                      {day.total_revenue > 0 ? "With sales" : "Zero sales"}
                    </td>
                  </tr>
                ))}

                {dailySales.length === 0 && (
                  <tr>
                    <td colSpan={5}>No daily sales records available.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* ZERO SALES DATES */}
      <section className="workshop-section">
        <div className="panel workshop-panel">
          <div className="panel-heading">
            <div>
              <h3>Zero-Sales Dates</h3>
              <p>
                {zeroSalesDates.length} recorded days with no sales
              </p>
            </div>
          </div>

          <div className="data-notes-list">
            {zeroSalesDates.map((date) => (
              <span key={date} className="highlight-item">
                {formatDate(date)}
              </span>
            ))}

            {zeroSalesDates.length === 0 && (
              <p>No zero-sales dates available.</p>
            )}
          </div>
        </div>
      </section>
    </>
  );
}

export default App;
