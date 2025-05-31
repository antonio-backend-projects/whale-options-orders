import os
import time
import pandas as pd
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

BARCHART_USER = os.getenv("BARCHART_USER")
BARCHART_PASSWORD = os.getenv("BARCHART_PASSWORD")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")  # Percorso opzionale a file CSV locale
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
CSV_FILENAME = "unusual-stock-options-activity.csv"

def get_unusual_option_activity():
    # Se presente, usa il file CSV fornito manualmente
    if CSV_FILE_PATH and os.path.exists(CSV_FILE_PATH):
        print(f"📂 Utilizzo file CSV locale: {CSV_FILE_PATH}")
        df = pd.read_csv(CSV_FILE_PATH)
    else:
        # Altrimenti accedi e scarica da Barchart
        print("🌐 Accesso a Barchart per scaricare i dati...")
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()

            # Login
            page.goto("https://www.barchart.com/login")
            print("🌐 Navigazione verso pagina login...")
            page.wait_for_selector('input[placeholder="Login with email"]', timeout=10000)
            page.fill('input[placeholder="Login with email"]', BARCHART_USER)
            page.fill('input[placeholder="Password"]', BARCHART_PASSWORD)
            page.click('form button[type="submit"], form input[type="submit"]')
            page.wait_for_load_state("networkidle")
            print("✅ Login effettuato.")

            # Vai alla pagina unusual activity
            page.goto("https://www.barchart.com/options/unusual-activity/stocks", timeout=60000)
            page.wait_for_selector('a[data-bc-download-button]')

            # Scarica il CSV
            with page.expect_download() as download_info:
                page.click('a[data-bc-download-button]')
            download = download_info.value
            download_path = os.path.join(DOWNLOAD_DIR, CSV_FILENAME)
            download.save_as(download_path)
            print(f"📥 File CSV scaricato: {download_path}")

            browser.close()

        df = pd.read_csv(download_path)

    # Analizza il CSV
    print("🔍 Analisi opzioni sospette...")
    filtered = df[(df["Volume"] > 1000) & (df["Trade Count"] > 10)]

    if filtered.empty:
        print("❌ Nessuna opzione sospetta trovata al momento.")
        return []

    print(f"✅ Trovate {len(filtered)} opzioni sospette.")
    return filtered.to_dict(orient="records")
