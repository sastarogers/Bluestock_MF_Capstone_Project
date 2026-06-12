"""Master Pipeline Runner
========================
Orchestrate all Bluestock MF Capstone pipeline stages with
logging, timing, and selective execution support.

Usage:
    python3 scripts/run_pipeline.py              # Run all stages
    python3 scripts/run_pipeline.py --stage 3    # Run from stage 3 onwards
    python3 scripts/run_pipeline.py --only 4     # Run only stage 4
    python3 scripts/run_pipeline.py --list       # List all stages
"""

import argparse
import importlib
import logging
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# Ensure the project root is on the path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / "scripts"))


# ── Stage definitions ────────────────────────────────────────────
STAGES = [
    {
        "id": 1,
        "name": "Data Ingestion",
        "module": "data_ingestion",
        "description": "Load and profile all 10 raw CSV datasets.",
    },
    {
        "id": 2,
        "name": "Live NAV Fetch",
        "module": "live_nav_fetch",
        "description": "Fetch live NAV data from mfapi.in (requires network).",
        "optional": True,
    },
    {
        "id": 3,
        "name": "Data Cleaning + SQLite",
        "module": "day2_clean_sqlite",
        "description": "Clean datasets, build star-schema SQLite warehouse.",
    },
    {
        "id": 4,
        "name": "Exploratory Data Analysis",
        "module": "day3_eda",
        "description": "Generate 18 EDA charts and Jupyter notebook.",
    },
    {
        "id": 5,
        "name": "Performance Analytics",
        "module": "day4_performance_analytics",
        "description": "Compute returns, CAGR, Sharpe, alpha/beta, scorecard.",
    },
    {
        "id": 6,
        "name": "Tableau Data Export",
        "module": "build_tableau_data",
        "description": "Export flat CSVs for Tableau dashboard pages.",
    },
    {
        "id": 7,
        "name": "Tableau Workbook Generation",
        "module": "generate_tableau_workbook",
        "description": "Generate .twb workbook with data-source connections.",
    },
    {
        "id": 8,
        "name": "Advanced Analytics Notebook",
        "module": "generate_advanced_notebook",
        "description": "Build Advanced_Analytics.ipynb (VaR, Sharpe, HHI).",
        "script_mode": True,
    },
    {
        "id": 9,
        "name": "Final PDF Report",
        "module": "generate_final_report",
        "description": "Generate 15-20 page Final_Report.pdf.",
    },
    {
        "id": 10,
        "name": "Presentation",
        "module": "generate_presentation",
        "description": "Generate 12-slide Bluestock_MF_Presentation.pptx.",
    },
]


def run_stage(stage: dict) -> bool:
    """Import and execute a single pipeline stage.

    Parameters
    ----------
    stage : dict
        Stage definition with 'id', 'name', 'module', and optional flags.

    Returns
    -------
    bool
        True if the stage succeeded, False otherwise.
    """
    stage_id = stage["id"]
    name = stage["name"]
    module_name = stage["module"]
    is_optional = stage.get("optional", False)

    log.info("=" * 60)
    log.info("STAGE %d: %s", stage_id, name)
    log.info("=" * 60)

    start = time.time()
    try:
        if stage.get("script_mode"):
            # Script-mode modules execute at import time
            importlib.import_module(module_name)
        else:
            mod = importlib.import_module(module_name)
            mod.main()
        elapsed = time.time() - start
        log.info("✓ Stage %d completed in %.1fs", stage_id, elapsed)
        return True
    except Exception as exc:
        elapsed = time.time() - start
        if is_optional:
            log.warning(
                "⚠ Stage %d (%s) failed after %.1fs — skipping (optional): %s",
                stage_id, name, elapsed, exc,
            )
            return True
        log.error(
            "✗ Stage %d (%s) failed after %.1fs: %s",
            stage_id, name, elapsed, exc,
        )
        return False


def main() -> None:
    """Parse arguments and run selected pipeline stages."""
    parser = argparse.ArgumentParser(
        description="Bluestock MF Capstone — Master Pipeline Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--stage", type=int, metavar="N",
        help="Start from stage N (inclusive).",
    )
    parser.add_argument(
        "--only", type=int, metavar="N",
        help="Run only stage N.",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List all pipeline stages and exit.",
    )
    parser.add_argument(
        "--skip-optional", action="store_true",
        help="Skip optional stages (e.g., live NAV fetch).",
    )
    args = parser.parse_args()

    if args.list:
        print("\nBluestock MF Capstone — Pipeline Stages\n")
        for s in STAGES:
            opt = " (optional)" if s.get("optional") else ""
            print(f"  Stage {s['id']:2d}: {s['name']:<35s} {s['description']}{opt}")
        print()
        return

    # Determine which stages to run
    stages_to_run = STAGES
    if args.only:
        stages_to_run = [s for s in STAGES if s["id"] == args.only]
        if not stages_to_run:
            log.error("Stage %d not found.", args.only)
            sys.exit(1)
    elif args.stage:
        stages_to_run = [s for s in STAGES if s["id"] >= args.stage]

    if args.skip_optional:
        stages_to_run = [s for s in stages_to_run if not s.get("optional")]

    log.info("Bluestock MF Capstone — Pipeline Start")
    log.info("Running %d stage(s)", len(stages_to_run))

    total_start = time.time()
    passed = 0
    failed = 0

    for stage in stages_to_run:
        ok = run_stage(stage)
        if ok:
            passed += 1
        else:
            failed += 1
            log.error("Pipeline halted at stage %d.", stage["id"])
            break

    total_elapsed = time.time() - total_start
    log.info("=" * 60)
    log.info(
        "Pipeline finished: %d passed, %d failed, %.1fs total",
        passed, failed, total_elapsed,
    )
    log.info("=" * 60)

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
