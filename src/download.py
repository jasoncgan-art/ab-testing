"""Download the A/B test dataset (only needed if data/ab_data.csv is missing).

Source: public GitHub mirror of the Udacity e-commerce A/B test dataset.
Run: python3 src/download.py
"""
import urllib.request
from pathlib import Path

URL = ("https://raw.githubusercontent.com/beery4010/Analyze-AB-Test-Results/"
       "master/ab_data.csv")
DEST = Path(__file__).resolve().parent.parent / "data" / "ab_data.csv"

DEST.parent.mkdir(parents=True, exist_ok=True)
urllib.request.urlretrieve(URL, DEST)
print(f"Downloaded {DEST} ({DEST.stat().st_size:,} bytes)")
