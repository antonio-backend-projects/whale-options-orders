import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Ottieni il contesto temporale: anno e mese corrente
current_date = datetime.now().strftime("%Y-%m")

def analyze_order(order):
    prompt = (
        f"Siamo nel mese di {current_date}. Analizza questo ordine di opzioni:\n"
        f"- Ticker: {order['ticker']}\n"
        f"- Tipo: {order['type']}\n"
        f"- Strike: {order['strike']}\n"
        f"- Scadenza: {order['expiry']}\n"
        f"- Premio stimato totale: {order['premium']:.2f}$\n"
        f"- Tipo ordine: {order['trade_type']}\n"
        f"- Volume: {order['volume']}\n"
        f"- Open Interest: {order['oi']}\n\n"
        f"È un ordine da smart money? Motiva la risposta in modo tecnico ma chiaro."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Errore nell'analisi GPT: {e}"
