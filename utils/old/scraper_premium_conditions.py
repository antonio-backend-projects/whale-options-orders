import requests
from bs4 import BeautifulSoup


def get_unusual_option_activity():
    url = "https://www.barchart.com/options/unusual-activity/stocks"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    table = soup.find("table", {"class": "bc-table-scrollable-inner"})
    if not table:
        return []

    rows = table.find_all("tr")[1:]  # Skip header

    unusual_orders = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 9:
            continue

        try:
            ticker = cols[0].get_text(strip=True)
            expiry = cols[2].get_text(strip=True)
            strike = cols[3].get_text(strip=True)
            option_type = cols[4].get_text(strip=True)
            volume = int(cols[5].get_text(strip=True).replace(",", ""))
            open_interest = int(cols[6].get_text(strip=True).replace(",", ""))
            last_price = float(cols[7].get_text(strip=True).replace("$", ""))
            premium_str = cols[8].get_text(strip=True).replace("$", "")

            if "M" in premium_str:
                premium = float(premium_str.replace("M", "")) * 1_000_000
            elif "K" in premium_str:
                premium = float(premium_str.replace("K", "")) * 1_000
            else:
                premium = float(premium_str)

            if option_type == "Call" and premium >= 500_000 and volume > open_interest:
                unusual_orders.append({
                    "ticker": ticker,
                    "expiry": expiry,
                    "strike": strike,
                    "type": option_type,
                    "volume": volume,
                    "oi": open_interest,
                    "last_price": last_price,
                    "premium": premium,
                    "trade_type": "Unknown"  # Placeholder, not available in public Barchart HTML
                })
        except Exception:
            continue

    return unusual_orders
