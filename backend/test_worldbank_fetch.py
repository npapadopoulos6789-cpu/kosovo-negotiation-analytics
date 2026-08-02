"""
Δοκιμαστικό script -- κατεβάζει και τυπώνει δεδομένα από το World Bank
API, ώστε να δούμε τα πραγματικά νούμερα πριν τα βάλουμε στο seed script.
"""

import requests

COUNTRIES = {
    "Serbia": "SRB",
    "Kosovo": "XKX",
}

INDICATORS = {
    "GDP_growth": "NY.GDP.MKTP.KD.ZG",
    "unemployment_rate": "SL.UEM.TOTL.ZS",
    "military_expenditure_pct_gdp": "MS.MIL.XPND.GD.ZS",  # ΝΕΟ -- πηγή SIPRI
}


def fetch_indicator(country_code: str, indicator_code: str) -> list[dict]:
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}"
    params = {"format": "json", "date": "1997:2024", "per_page": 100}

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    if len(data) < 2 or data[1] is None:
        return []

    results = []
    for entry in data[1]:
        results.append({"year": int(entry["date"]), "value": entry["value"]})
    return results


if __name__ == "__main__":
    for country_name, country_code in COUNTRIES.items():
        for indicator_name, indicator_code in INDICATORS.items():
            print(f"\n=== {country_name} — {indicator_name} ===")
            rows = fetch_indicator(country_code, indicator_code)

            if not rows:
                print("  (ΚΕΝΟ)")
                continue

            non_null = [r for r in rows if r["value"] is not None]
            non_null.sort(key=lambda r: r["year"])

            for r in non_null:
                print(f"  {r['year']}: {r['value']:.2f}")

            print(f"  --> {len(non_null)} έτη με δεδομένα (από {len(rows)} συνολικά)")