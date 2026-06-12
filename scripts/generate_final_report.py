"""Generate Final PDF Report
============================
Build a professional 15-20 page PDF report covering all capstone
deliverables: executive summary, data sources, ETL design, EDA
findings, performance analysis, dashboard screenshots,
limitations, and recommendations.

Usage:
    python3 scripts/generate_final_report.py
"""

import logging
from pathlib import Path

from fpdf import FPDF

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = BASE_DIR / "reports"
CHART_DIR_DAY3 = REPORTS_DIR / "charts" / "day3"
CHART_DIR_DAY4 = REPORTS_DIR / "charts" / "day4"
DASHBOARD_DIR = BASE_DIR / "dashboard"
LOGO_PATH = DASHBOARD_DIR / "bluestock_logo.png"

# ── Colour palette ───────────────────────────────────────────────
NAVY = (1, 41, 112)
WHITE = (255, 255, 255)
LIGHT_GREY = (240, 240, 245)
DARK_TEXT = (30, 30, 30)
ACCENT = (240, 85, 55)


class BluestockPDF(FPDF):
    """Custom PDF with branded header/footer."""

    def header(self):
        """Render page header with blue bar and title."""
        if self.page_no() == 1:
            return  # Title page has its own header
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 12, "F")
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 8)
        self.set_y(3)
        self.cell(0, 6, "Bluestock Mutual Fund Capstone - Final Report", align="C")
        self.set_text_color(*DARK_TEXT)
        self.ln(12)

    def footer(self):
        """Render page footer with page number."""
        if self.page_no() == 1:
            return
        self.set_y(-10)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")

    def section_title(self, title: str, num: str = ""):
        """Add a styled section heading."""
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*NAVY)
        label = f"{num}  {title}" if num else title
        self.cell(0, 12, label, new_x="LMARGIN", new_y="NEXT")
        # Accent underline
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.8)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)
        self.set_text_color(*DARK_TEXT)

    def sub_heading(self, text: str):
        """Add a sub-section heading."""
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*NAVY)
        self.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*DARK_TEXT)
        self.ln(2)

    def body_text(self, text: str):
        """Add body paragraph text."""
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text: str):
        """Add a bullet point."""
        self.set_font("Helvetica", "", 10)
        self.cell(6, 5.5, "-")
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def add_table(self, headers: list[str], rows: list[list[str]], col_widths: list[int] = None):
        """Add a styled table."""
        if col_widths is None:
            col_widths = [int(190 / len(headers))] * len(headers)

        # Header row
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(*NAVY)
        self.set_text_color(*WHITE)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=1, fill=True, align="C")
        self.ln()

        # Data rows
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*DARK_TEXT)
        fill = False
        for row in rows:
            if fill:
                self.set_fill_color(*LIGHT_GREY)
            else:
                self.set_fill_color(*WHITE)
            for i, cell_val in enumerate(row):
                self.cell(col_widths[i], 6, str(cell_val), border=1, fill=True, align="C")
            self.ln()
            fill = not fill
        self.ln(4)

    def safe_image(self, path: Path, w: int = 180):
        """Add an image if the file exists, otherwise a placeholder note."""
        if path.exists():
            self.image(str(path), x=15, w=w)
            self.ln(4)
        else:
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(150, 150, 150)
            self.cell(0, 6, f"[Chart not found: {path.name}]", new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(*DARK_TEXT)
            self.ln(2)


def build_title_page(pdf: BluestockPDF):
    """Build the branded title page."""
    pdf.add_page()

    # Navy background block
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, 210, 297, "F")

    # Title
    pdf.set_y(80)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 14, "Bluestock Mutual Fund", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 14, "Capstone Project", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    pdf.set_font("Helvetica", "", 16)
    pdf.cell(0, 10, "Final Report", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)

    # Accent line
    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(1.5)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(12)

    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, "Data Engineering & Analytics Capstone", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Indian Mutual Fund Industry", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.cell(0, 8, "Prepared by: Atharva Ranjan", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "June 2026", align="C", new_x="LMARGIN", new_y="NEXT")


def build_toc(pdf: BluestockPDF):
    """Build the table of contents."""
    pdf.add_page()
    pdf.section_title("Table of Contents")

    toc = [
        ("1", "Executive Summary", "3"),
        ("2", "Data Sources", "5"),
        ("3", "ETL Design", "7"),
        ("4", "EDA Findings", "9"),
        ("5", "Performance Analysis", "12"),
        ("6", "Dashboard Screenshots", "15"),
        ("7", "Limitations", "17"),
        ("8", "Recommendations", "18"),
    ]
    pdf.set_font("Helvetica", "", 12)
    for num, title, page in toc:
        pdf.cell(10, 8, num)
        pdf.cell(140, 8, title)
        pdf.cell(30, 8, page, align="R")
        pdf.ln()
    pdf.ln(8)


def build_executive_summary(pdf: BluestockPDF):
    """Build the executive summary section."""
    pdf.add_page()
    pdf.section_title("Executive Summary", "1")

    pdf.body_text(
        "This report presents the complete findings of the Bluestock Mutual Fund Capstone Project - "
        "a multi-phase data engineering and analytics initiative covering the Indian mutual fund industry. "
        "The project ingested, cleaned, and warehoused 10 datasets comprising over 100,000 records, "
        "built a star-schema SQLite database, performed comprehensive exploratory and performance "
        "analytics, and delivered an interactive Tableau dashboard."
    )

    pdf.sub_heading("Key Outcomes")
    pdf.bullet("40 mutual fund schemes across 10 fund houses analysed end-to-end.")
    pdf.bullet("64,320 daily NAV rows after calendar forward-fill (from 46,000 raw rows).")
    pdf.bullet("SIP inflows reached Rs 31,002 Cr all-time high in December 2025.")
    pdf.bullet("Industry folios grew from 13.26 Cr to 26.12 Cr (nearly doubled).")
    pdf.bullet("Composite fund scorecard built with 5-factor scoring (CAGR, Sharpe, Alpha, Expense, Drawdown).")
    pdf.bullet("VaR/CVaR computed for all 40 schemes; rolling 90-day Sharpe tracked.")
    pdf.bullet("4-page interactive Tableau dashboard delivered with 17 visualisations.")

    pdf.sub_heading("Project Phases")
    pdf.add_table(
        ["Day", "Phase", "Key Deliverables"],
        [
            ["1", "Data Ingestion", "10 CSVs loaded, profiled, AMFI validated"],
            ["2", "Cleaning + SQLite", "Star schema, 11 tables, quality reports"],
            ["3", "EDA", "18 charts, Jupyter notebook, 10 findings"],
            ["4", "Performance", "Scorecard, CAGR, Sharpe, alpha/beta"],
            ["5", "Dashboard", "4-page Tableau workbook"],
            ["6", "Advanced Analytics", "VaR, HHI, cohort, SIP continuity"],
        ],
        [15, 60, 115],
    )


def build_data_sources(pdf: BluestockPDF):
    """Build the data sources section."""
    pdf.add_page()
    pdf.section_title("Data Sources", "2")

    pdf.body_text(
        "The project uses 10 structured CSV datasets representing different facets of the Indian "
        "mutual fund industry. An additional live NAV feed from mfapi.in supplements historical data "
        "for 6 bluechip schemes."
    )

    pdf.sub_heading("Raw Dataset Inventory")
    pdf.add_table(
        ["#", "Dataset", "Records", "Key Columns"],
        [
            ["01", "Fund Master", "40", "amfi_code, fund_house, category, risk"],
            ["02", "NAV History", "46,000", "amfi_code, date, nav"],
            ["03", "AUM by Fund House", "~80", "fund_house, aum_crore, date"],
            ["04", "Monthly SIP Inflows", "48", "month, sip_inflow_crore"],
            ["05", "Category Inflows", "~240", "month, category, net_inflow_crore"],
            ["06", "Industry Folio Count", "12", "month, total_folios_crore"],
            ["07", "Scheme Performance", "40", "returns, alpha, beta, sharpe"],
            ["08", "Investor Transactions", "50,000", "investor_id, amount, state, age"],
            ["09", "Portfolio Holdings", "~400", "stock, sector, weight_pct"],
            ["10", "Benchmark Indices", "~4,000", "index_name, date, close_value"],
        ],
        [10, 55, 25, 100],
    )

    pdf.sub_heading("Live Data Feed")
    pdf.body_text(
        "The live_nav_fetch.py script queries the MFAPI (https://api.mfapi.in) for historical NAV "
        "data for 6 flagship schemes: HDFC Top 100, SBI Bluechip, ICICI Bluechip, Nippon Large Cap, "
        "Axis Bluechip, and Kotak Bluechip."
    )

    pdf.sub_heading("Data Quality Profile")
    pdf.body_text(
        "Day 1 profiling revealed zero critical data issues across all 10 files. All AMFI codes "
        "in fund_master were validated against nav_history with zero missing matches. "
        "Day 2 cleaning expanded 46,000 raw NAV rows to 64,320 after calendar gap filling, "
        "excluded 0 invalid transactions, and flagged 0 scheme performance anomalies."
    )


def build_etl_design(pdf: BluestockPDF):
    """Build the ETL design section."""
    pdf.add_page()
    pdf.section_title("ETL Design", "3")

    pdf.sub_heading("Architecture Overview")
    pdf.body_text(
        "The ETL pipeline follows a classic Extract -> Transform -> Load pattern, "
        "implemented in Python with Pandas for transformation and SQLAlchemy for "
        "loading into a SQLite star-schema warehouse."
    )

    pdf.body_text(
        "Pipeline flow:  Raw CSVs  ->  Python cleaning scripts  ->  Processed CSVs  "
        "->  SQLite star schema  ->  Analytics / Tableau"
    )

    pdf.sub_heading("Star Schema Design")
    pdf.body_text(
        "The SQLite warehouse uses a star schema with 2 dimension tables and 4 fact tables, "
        "plus 5 auxiliary tables for industry-level metrics."
    )

    pdf.add_table(
        ["Table", "Type", "Grain", "Row Count"],
        [
            ["dim_fund", "Dimension", "One row per AMFI scheme", "40"],
            ["dim_date", "Dimension", "One row per calendar date", "~1,500"],
            ["fact_nav", "Fact", "Scheme x calendar date", "64,320"],
            ["fact_transactions", "Fact", "One row per transaction", "50,000"],
            ["fact_performance", "Fact", "One row per scheme", "40"],
            ["fact_aum", "Fact", "Fund house x date", "~80"],
        ],
        [42, 28, 70, 50],
    )

    pdf.sub_heading("Key Cleaning Rules")
    pdf.bullet("NAV History: parsed dates, sorted, deduplicated, forward-filled calendar gaps, validated NAV > 0.")
    pdf.bullet("Transactions: standardised types (SIP/Lumpsum/Redemption), validated amounts > 0, KYC enum check.")
    pdf.bullet("Performance: coerced numeric fields, flagged returns outside +/-100%, expense ratio validated 0.1-2.5%.")
    pdf.bullet("All tables: duplicate removal, date parsing, foreign-key integrity via date_key joins.")

    pdf.sub_heading("Calendar Forward-Fill")
    pdf.body_text(
        "Missing calendar dates within each scheme's NAV history were filled using forward-fill (ffill). "
        "This expanded the dataset from 46,000 raw rows to 64,320 daily rows, with 18,320 synthetic "
        "rows inserted. This ensures continuous time-series for return calculations."
    )


def build_eda_findings(pdf: BluestockPDF):
    """Build the EDA findings section."""
    pdf.add_page()
    pdf.section_title("EDA Findings", "4")

    pdf.body_text(
        "Day 3 exploratory analysis generated 18 publication-quality charts examining NAV trends, "
        "AUM concentration, SIP inflows, investor demographics, portfolio composition, and risk-return profiles."
    )

    # Chart: NAV trend
    pdf.sub_heading("4.1 NAV Trends")
    pdf.safe_image(CHART_DIR_DAY3 / "01_nav_trend_all_40_schemes.png")
    pdf.body_text(
        "Daily NAV trends for all 40 schemes (2022-2026) with the 2023 bull-run and 2024 correction "
        "windows highlighted. NAV levels vary significantly across schemes."
    )

    # Chart: AUM growth
    if pdf.get_y() > 200:
        pdf.add_page()
    pdf.sub_heading("4.2 AUM Growth")
    pdf.safe_image(CHART_DIR_DAY3 / "03_aum_growth_by_fund_house.png")
    pdf.body_text("SBI Mutual Fund leads as the dominant AUM leader.")

    # Chart: SIP inflows
    pdf.add_page()
    pdf.sub_heading("4.3 SIP Inflows")
    pdf.safe_image(CHART_DIR_DAY3 / "05_sip_inflow_time_series.png")
    pdf.body_text("SIP inflows grew steadily and reached an all-time high of Rs 31,002 Cr in Dec 2025.")

    # Chart: Category heatmap
    if pdf.get_y() > 200:
        pdf.add_page()
    pdf.sub_heading("4.4 Category Inflows")
    pdf.safe_image(CHART_DIR_DAY3 / "07_category_inflow_heatmap.png")

    # Chart: Risk-return
    pdf.add_page()
    pdf.sub_heading("4.5 Risk-Return Profile")
    pdf.safe_image(CHART_DIR_DAY3 / "17_risk_return_scatter.png")
    pdf.body_text(
        "Risk-return scatter shows the trade-off between 3-year returns and annualised volatility, "
        "with bubble size proportional to AUM."
    )

    # Key findings
    pdf.sub_heading("10 Key EDA Findings")
    findings = [
        "NAV levels vary widely; indexed views are required before comparing growth.",
        "Several schemes compounded meaningfully after the 2023 rally window.",
        "SBI Mutual Fund is the clear AUM leader with Rs 12.5L Cr dominance.",
        "SIP inflows reached Rs 31,002 Cr all-time high in Dec 2025.",
        "Category inflows are uneven, with concentrated bursts in selected categories.",
        "Investor participation is distributed across multiple age bands.",
        "SIP ticket sizes differ by age group with notable outliers.",
        "SIP contribution is geographically concentrated in top states.",
        "Industry folios approximately doubled from 13.26 Cr to 26.12 Cr.",
        "Selected fund returns are positively correlated, limiting diversification benefit.",
    ]
    for f in findings:
        pdf.bullet(f)


def build_performance_analysis(pdf: BluestockPDF):
    """Build the performance analysis section."""
    pdf.add_page()
    pdf.section_title("Performance Analysis", "5")

    pdf.sub_heading("5.1 Scorecard Methodology")
    pdf.body_text(
        "A composite 0-100 fund score was built from five percentile-ranked factors:"
    )
    pdf.add_table(
        ["Factor", "Weight", "Direction"],
        [
            ["3-Year CAGR", "30%", "Higher is better"],
            ["Sharpe Ratio", "25%", "Higher is better"],
            ["Alpha (vs NIFTY100)", "20%", "Higher is better"],
            ["Expense Ratio", "15%", "Lower is better"],
            ["Max Drawdown", "10%", "Less negative is better"],
        ],
        [70, 40, 80],
    )

    pdf.sub_heading("5.2 Risk Metrics")
    pdf.body_text(
        "Daily returns were computed as NAV(t)/NAV(t-1) - 1 for all 40 schemes. "
        "Sharpe Ratio uses a 6.5% annual risk-free rate proxy. Sortino Ratio uses downside "
        "volatility only. Alpha and beta are estimated via OLS regression against NIFTY100."
    )

    # Benchmark chart
    pdf.sub_heading("5.3 Benchmark Comparison")
    pdf.safe_image(CHART_DIR_DAY4 / "benchmark_comparison_top5_vs_indices.png")
    pdf.body_text(
        "3-year indexed performance of the top 5 scorecard funds vs NIFTY50 and NIFTY100 benchmarks."
    )

    # VaR chart
    pdf.add_page()
    pdf.sub_heading("5.4 Value-at-Risk Analysis")
    var_chart = REPORTS_DIR / "var_cvar_chart.png"
    pdf.safe_image(var_chart)
    pdf.body_text(
        "Historical VaR (95%) and CVaR were computed for all 40 schemes. VaR represents "
        "the worst daily loss expected on 19 out of 20 days. CVaR (Expected Shortfall) is "
        "the average loss on the worst 5% of days."
    )

    # Rolling Sharpe
    pdf.sub_heading("5.5 Rolling Sharpe Ratio")
    rolling_chart = REPORTS_DIR / "rolling_sharpe_chart.png"
    pdf.safe_image(rolling_chart)
    pdf.body_text(
        "90-day rolling Sharpe Ratio for the top 5 funds by overall Sharpe, showing how "
        "risk-adjusted performance evolves over time."
    )


def build_dashboard_screenshots(pdf: BluestockPDF):
    """Build the dashboard screenshots section."""
    pdf.add_page()
    pdf.section_title("Dashboard", "6")

    pdf.body_text(
        "A 4-page interactive Tableau dashboard was built to visualise all analytical outputs. "
        "Below are screenshots of each dashboard page."
    )

    pages = [
        ("1. Industry Overview.png", "Industry Overview: KPIs, AUM timeline, fund house ranking"),
        ("2. Fund Performance.png", "Fund Performance: Risk-return scatter, scorecard, NAV comparison"),
        ("3. Investor Analytics.png", "Investor Analytics: Demographics, geography, transaction patterns"),
        ("4. SIP & Market Trends.png", "SIP & Market Trends: SIP vs Nifty, category inflows, YoY growth"),
    ]

    for filename, caption in pages:
        path = DASHBOARD_DIR / filename
        if pdf.get_y() > 140:
            pdf.add_page()
        pdf.sub_heading(caption)
        pdf.safe_image(path)
        pdf.ln(2)


def build_limitations(pdf: BluestockPDF):
    """Build the limitations section."""
    pdf.add_page()
    pdf.section_title("Limitations", "7")

    limitations = [
        (
            "5-Year CAGR Unavailable",
            "The cleaned NAV history starts in January 2022, providing only ~4 years of data. "
            "True 5-year CAGR cannot be computed and is flagged as unavailable in the scorecard."
        ),
        (
            "Synthetic Investor Data",
            "The investor transactions dataset is synthetically generated for capstone purposes. "
            "Demographic distributions may not reflect real-world patterns."
        ),
        (
            "No Real-Time Pipeline",
            "The ETL pipeline runs as a batch process. There is no streaming or scheduled ingestion. "
            "NAV data requires manual refresh via live_nav_fetch.py."
        ),
        (
            "Forward-Fill Bias",
            "Calendar gaps in NAV history are forward-filled, which creates zero-return days. "
            "This slightly dampens volatility estimates and may understate true risk."
        ),
        (
            "Single Benchmark Regression",
            "Alpha and beta are computed against NIFTY100 only. Multi-factor models (Fama-French) "
            "would provide more robust risk attribution."
        ),
        (
            "Static Dashboard",
            "The Tableau workbook uses flat CSV extracts. It does not connect to a live database "
            "and requires manual data refresh."
        ),
    ]

    for title, desc in limitations:
        pdf.sub_heading(title)
        pdf.body_text(desc)


def build_recommendations(pdf: BluestockPDF):
    """Build the recommendations section."""
    pdf.add_page()
    pdf.section_title("Recommendations", "8")

    recs = [
        (
            "Real-Time API Integration",
            "Connect the pipeline to MFAPI or AMFI feeds for automated daily NAV ingestion "
            "using Apache Airflow or a scheduled cron job."
        ),
        (
            "ML-Based Fund Recommender",
            "Replace the rule-based recommender with a collaborative filtering or content-based "
            "model trained on investor transaction patterns and fund features."
        ),
        (
            "Multi-Factor Risk Model",
            "Extend alpha/beta analysis with Fama-French 3-factor or Carhart 4-factor models "
            "for more robust risk-adjusted performance attribution."
        ),
        (
            "SIP Churn Prediction",
            "Build a classification model to predict SIP discontinuation using the SIP continuity "
            "features (gap days, frequency, amount trends) as input features."
        ),
        (
            "Portfolio Optimisation",
            "Implement mean-variance (Markowitz) or risk-parity portfolio optimisation to suggest "
            "optimal fund allocations based on investor risk profiles."
        ),
        (
            "Cloud Deployment",
            "Migrate the SQLite warehouse to PostgreSQL on a cloud platform (AWS RDS / GCP Cloud SQL) "
            "and deploy the dashboard via Tableau Public or a Streamlit web application."
        ),
    ]

    for title, desc in recs:
        pdf.sub_heading(title)
        pdf.body_text(desc)


def main() -> None:
    """Generate the complete Final_Report.pdf."""
    pdf = BluestockPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    build_title_page(pdf)
    build_toc(pdf)
    build_executive_summary(pdf)
    build_data_sources(pdf)
    build_etl_design(pdf)
    build_eda_findings(pdf)
    build_performance_analysis(pdf)
    build_dashboard_screenshots(pdf)
    build_limitations(pdf)
    build_recommendations(pdf)

    output_path = REPORTS_DIR / "Final_Report.pdf"
    pdf.output(str(output_path))
    log.info("Final report generated: %s (%d pages)", output_path, pdf.page_no())


if __name__ == "__main__":
    main()
