import os
import time
import pandas as pd
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from datetime import datetime

load_dotenv()

BARCHART_USER = os.getenv("BARCHART_USER")
BARCHART_PASSWORD = os.getenv("BARCHART_PASSWORD")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
CSV_FILENAME = "unusual-stock-options-activity.csv"


def is_smart_money(order):
    try:
        vol = float(order["Volume"])
        oi = float(order["Open Int"])
        vol_oi_ratio = vol / oi if oi else float("inf")
        delta = float(order["Delta"])
        imp_vol = float(str(order["Imp Vol"]).replace("%", ""))
        bid = float(order["Bid"])
        ask = float(order["Ask"])
        strike = float(order["Strike"])
        price = float(order["Price~"])
        exp_date = datetime.strptime(order["Exp Date"], "%Y-%m-%d")
        today = datetime.today()
        days_to_expiry = (exp_date - today).days

        # Calcolo premio stimato
        mid_price = (bid + ask) / 2
        premium = mid_price * 100 * vol

        return (
            vol >= 500 and
            vol_oi_ratio >= 3 and
            premium >= 10000 and
            0.20 <= delta <= 0.60 and
            imp_vol >= 40 and
            days_to_expiry >= 7 and
            (ask - bid) <= 0.05  # spread ragionevole
        )
    except Exception:
        return False



def normalize_order(row):
    return {
        "ticker": row["Symbol"],
        "price": float(row["Price~"]),
        "expiry": row["Exp Date"],
        "type": row["Type"],
        "strike": float(row["Strike"]),
        "moneyness": row["Moneyness"],
        "bid": float(row["Bid"]),
        "ask": float(row["Ask"]),
        "volume": float(row["Volume"]),
        "oi": float(row["Open Int"]),
        "vol_oi": float(row["Vol/OI"]),
        "iv": row["Imp Vol"],
        "delta": float(row["Delta"]),
        "time": row["Time"],
        "premium": round((float(row["Bid"]) + float(row["Ask"])) / 2 * float(row["Volume"]), 2),
        "trade_type": "Sweep (stimato)"  # Può essere raffinato se servono heuristics più complesse
    }


def get_unusual_option_activity():
    if CSV_FILE_PATH and os.path.exists(CSV_FILE_PATH):
        print(f"📂 Utilizzo file CSV locale: {CSV_FILE_PATH}")
        df = pd.read_csv(CSV_FILE_PATH)
    else:
        print("🌐 Accesso a Barchart per scaricare i dati...")
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()

            page.goto("https://www.barchart.com/login")
            print("🌐 Navigazione verso pagina login...")
            page.wait_for_selector('input[placeholder="Login with email"]', timeout=10000)
            page.fill('input[placeholder="Login with email"]', BARCHART_USER)
            page.fill('input[placeholder="Password"]', BARCHART_PASSWORD)
            page.click('form button[type="submit"], form input[type="submit"]')
            page.wait_for_load_state("networkidle")
            print("✅ Login effettuato.")

            page.goto("https://www.barchart.com/options/unusual-activity/stocks", timeout=60000)
            page.wait_for_selector('a[data-bc-download-button]')

            with page.expect_download() as download_info:
                page.click('a[data-bc-download-button]')
            download = download_info.value
            download_path = os.path.join(DOWNLOAD_DIR, CSV_FILENAME)
            download.save_as(download_path)
            print(f"📥 File CSV scaricato: {download_path}")

            browser.close()

        df = pd.read_csv(download_path)

    print("🔍 Analisi opzioni sospette...")
    smart_money_orders = []

    for _, row in df.iterrows():
        if is_smart_money(row):
            smart_money_orders.append(normalize_order(row))

    if not smart_money_orders:
        print("❌ Nessuna operazione da smart money rilevata.")
        return []

    print(f"✅ Trovate {len(smart_money_orders)} operazioni da smart money.")
    return smart_money_orders
