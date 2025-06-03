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

def classify_trade_type(row):
    try:
        price = float(row["Price~"])
        bid = float(row["Bid"])
        ask = float(row["Ask"])
        option_type = str(row["Type"]).upper()  # forza a stringa per evitare errori
        volume = int(row["Volume"])
        open_int = int(row["Open Int"])
    except Exception as e:
        print(f"Errore classify_trade_type: {e} - row: {row.to_dict()}")
        return "UNKNOWN"

    is_buy = abs(price - ask) < abs(price - bid)
    is_new_position = volume >= open_int

    if is_buy and is_new_position:
        return f"BUY {option_type}"
    elif not is_buy and is_new_position:
        return f"SELL {option_type}"
    elif is_buy and not is_new_position:
        return f"COVER {option_type}"
    else:
        return f"CLOSE {option_type}"




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

        # Parsing della data di scadenza in formato corretto
        exp_date = datetime.strptime(order["Exp Date"], "%Y-%m-%d")
        today = datetime.today()
        days_to_expiry = (exp_date - today).days

        # Calcolo premio stimato: prezzo medio * 100 * volume
        mid_price = (bid + ask) / 2
        premium = mid_price * 100 * vol

        # Condizioni di filtro "smart money"
        return (
            vol >= 500 and
            vol_oi_ratio >= 3 and
            premium >= 10000 and
            0.20 <= abs(delta) <= 0.60 and  # delta tra 0.2 e 0.6 in valore assoluto
            imp_vol >= 40 and
            days_to_expiry >= 7 and        # almeno 7 giorni alla scadenza
            (ask - bid) <= 0.05            # spread massimo 5 centesimi
        )
    except Exception as e:
        # Se c'è errore nel parsing, ignora la riga
        return False



# Funzione per identificare attività insolita in termini di volume estrapolata da notebookLM
def is_unusual_volume_activity(order):
    try:
        # Estrai i dati necessari. Attenzione al formato dello Strike se usa la virgola [6, 19, 20, 22, 26, 28, 34, 38, 39, 42, 44-50, 52]
        # La gestione della virgola per Strike è già presente nella tua funzione originale, la manteniamo.
        vol = float(order["Volume"]) #[1-57]
        oi = float(order["Open Int"]) #[1-57]
        # Calcola il rapporto Vol/OI - gestisce il caso oi=0 [1-57]
        vol_oi_ratio = vol / oi if oi else float("inf") #[1-57]

        # Le fonti usano principalmente il Vol/OI per identificare l'attività "insolita" [1]
        # Usiamo un'alta soglia di Vol/OI come primo criterio
        # La SOGLIA_VOL_OI non è definita nelle fonti e va scelta in base ai dati (es. > 10, > 20)
        SOGLIA_VOL_OI = 3 # Esempio: mantenere la tua soglia originale come punto di partenza

        # Le fonti mostrano anche operazioni con Volume assoluto molto elevato,
        # che rappresentano un alto "volume di affari" indipendentemente dall'OI [12, 15-19, 23, 32, 33]
        # Usiamo un'alta soglia di Volume assoluto come secondo criterio
        # La SOGLIA_VOLUME_ASSOLUTO non è definita nelle fonti e va scelta in base ai dati (es. > 10000)
        SOGLIA_VOLUME_ASSOLUTO = 500 # Esempio: mantenere la tua soglia originale come punto di partenza

        # *** Condizioni Basate Esclusivamente sulle Fonti e Conversazione ***
        # Un'operazione è considerata "insolita in termini di volume" se soddisfa ALMENO UNO
        # dei due criteri principali impliciti nelle fonti: alto Vol/OI o alto Volume assoluto.
        # Puoi scegliere di richiedere entrambe le condizioni (usando 'and' invece di 'or')
        # se vuoi essere più restrittivo. Manteniamo 'or' per includere operazioni
        # con alto volume anche se il rapporto Vol/OI non è altissimo (ma comunque > 3 nell'esempio).
        # Se vuoi basarti strettamente sull'ordinamento delle fonti, dovresti solo filtrare per alto Vol/OI.
        # Se vuoi anche catturare i maggiori volumi assoluti, usi anche la condizione sul Volume.

        # Rimosse le condizioni su premio, Delta, Imp Vol, giorni a scadenza, spread Bid/Ask
        # perché le fonti non le presentano come criteri per l'attività "insolita".
        # Questi dati sono presenti [1-57] ma la loro rilevanza come filtro per
        # l'"insolita" non è supportata dalle fonti stesse.

        return (
            vol_oi_ratio >= SOGLIA_VOL_OI or # Criterio principale delle fonti: alto rapporto Vol/OI [1]
            vol >= SOGLIA_VOLUME_ASSOLUTO    # Criterio secondario implicito: alto Volume assoluto [Conversazione precedente, esempi]
        )

    except Exception as e:
        # In caso di errori (es. dati mancanti o formato errato), ignora la riga
        print(f"Errore nell'elaborazione della riga: {e}") # Opzionale: stampa l'errore per debug
        return False

# Esempio di utilizzo (assumendo di avere un elenco di dizionari 'orders'):
# for order in orders_list:
#     if is_unusual_volume_activity(order):
#         print(f"Operazione con attività di volume insolita trovata: {order}")



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
        "iv": float(str(row["Imp Vol"]).replace("%", "")),
        "delta": float(row["Delta"]),
        "time": row["Time"],
        "premium": round(((float(row["Bid"]) + float(row["Ask"])) / 2) * float(row["Volume"]) * 100, 2),
        "trade_type": classify_trade_type(row)  # placeholder per tipo di trade
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
            page.wait_for_selector('a[data-bc-download-button]', timeout=40000)

            # Primo click: apre popup/modal
            page.click('a[data-bc-download-button]')
            print("📥 Bottone iniziale cliccato, attesa popup...")

            # Attende e clicca il secondo bottone "Download Anyway"
            page.wait_for_selector('button.button.download.contact-us', timeout=40000)
            with page.expect_download() as download_info:
                page.click('button.button.download.contact-us')

            download = download_info.value
            download_path = os.path.join(DOWNLOAD_DIR, CSV_FILENAME)
            download.save_as(download_path)
            print(f"📥 File CSV scaricato: {download_path}")

            browser.close()

        df = pd.read_csv(download_path)
        

    df["Trade Type"] = df.apply(classify_trade_type, axis=1)
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
