
"""
Fetch live NAV data from mfapi.in
"""

from pathlib import Path
import pandas as pd
import requests

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

SCHEMES = {
    "125497": "HDFC_Top_100_Direct",
    "119551": "SBI_Bluechip",
    "120503": "ICICI_Bluechip",
    "118632": "Nippon_Large_Cap",
    "119092": "Axis_Bluechip",
    "120841": "Kotak_Bluechip"
}

def fetch_nav(amfi_code, scheme_name):
    url = f"https://api.mfapi.in/mf/{amfi_code}"

    print(f"Fetching NAV for {scheme_name} ({amfi_code})")

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    nav_df = pd.DataFrame(data["data"])

    output_path = RAW_DATA_DIR / f"{scheme_name}_nav.csv"

    nav_df.to_csv(output_path, index=False)

    print(f"Saved: {output_path}")

if __name__ == "__main__":

    for code, scheme in SCHEMES.items():
        try:
            fetch_nav(code, scheme)
        except Exception as e:
            print(f"Error fetching {scheme}: {e}")

    print("\nLive NAV fetch complete.")
