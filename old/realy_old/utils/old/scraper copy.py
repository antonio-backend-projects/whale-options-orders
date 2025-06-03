import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime


def get_unusual_option_activity_barchart():
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

            # Smart money filter (NO sweep)
            if option_type == "Call" and premium >= 500_000 and volume > open_interest:
                unusual_orders.append({
                    "source": "Barchart",
                    "ticker": ticker,
                    "expiry": expiry,
                    "strike": strike,
                    "type": option_type,
                    "volume": volume,
                    "open_interest": open_interest,
                    "last_price": last_price,
                    "premium": premium
                })
        except Exception:
            continue

    return unusual_orders


def get_top_sentiment_swaggy():
    url = "https://swaggystocks.com/dashboard/wallstreetbets/ticker-sentiment"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    tickers = []
    try:
        table = soup.find("table")
        rows = table.find_all("tr")[1:]  # Skip header
        for row in rows[:20]:  # Primi 20 titoli
            cols = row.find_all("td")
            if len(cols) >= 2:
                ticker = cols[0].get_text(strip=True)
                sentiment = cols[1].get_text(strip=True)
                tickers.append({"source": "SwaggyStocks", "ticker": ticker, "sentiment": sentiment})
    except Exception:
        pass

    return tickers


def cross_reference(unusual, sentiment):
    trending = set([s['ticker'] for s in sentiment])
    highlighted = [entry for entry in unusual if entry['ticker'] in trending]
    return highlighted


if __name__ == "__main__":
    barchart_data = get_unusual_option_activity_barchart()
    swaggy_data = get_top_sentiment_swaggy()
    combined = cross_reference(barchart_data, swaggy_data)

    now = datetime.now().strftime("%Y-%m-%d_%H-%M")

    with open(f"unusual_options_{now}.json", "w") as f:
        json.dump({"highlighted": combined, "barchart": barchart_data, "swaggy": swaggy_data}, f, indent=2)

    print(f"Salvati {len(combined)} segnali incrociati su {len(barchart_data)} ordini insoliti.")
