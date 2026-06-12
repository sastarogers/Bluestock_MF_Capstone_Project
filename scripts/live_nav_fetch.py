"""
Live NAV Fetch
==============
Fetch live NAV data from the MFAPI (mfapi.in) for selected
bluechip schemes and save as CSV in ``data/raw/``.

Usage:
    python3 scripts/live_nav_fetch.py
"""

import logging
from pathlib import Path

import pandas as pd
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

SCHEMES = {
    "125497": "HDFC_Top_100_Direct",
    "119551": "SBI_Bluechip",
    "120503": "ICICI_Bluechip",
    "118632": "Nippon_Large_Cap",
    "119092": "Axis_Bluechip",
    "120841": "Kotak_Bluechip",
}


def fetch_nav(amfi_code: str, scheme_name: str) -> None:
    """Fetch historical NAV data for a single scheme and save to CSV.

    Parameters
    ----------
    amfi_code : str
        AMFI scheme code.
    scheme_name : str
        Human-readable scheme label used for the output filename.
    """
    url = f"https://api.mfapi.in/mf/{amfi_code}"
    log.info("Fetching NAV for %s (%s)", scheme_name, amfi_code)

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()
    nav_df = pd.DataFrame(data["data"])

    output_path = RAW_DATA_DIR / f"{scheme_name}_nav.csv"
    nav_df.to_csv(output_path, index=False)
    log.info("Saved: %s", output_path)


def main() -> None:
    """Fetch live NAV data for all configured schemes."""
    for code, scheme in SCHEMES.items():
        try:
            fetch_nav(code, scheme)
        except Exception as exc:
            log.error("Error fetching %s: %s", scheme, exc)

    log.info("Live NAV fetch complete.")


if __name__ == "__main__":
    main()
