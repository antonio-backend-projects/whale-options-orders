import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_order(order):
    prompt = (
        f"Analizza questo ordine di opzioni:\n"
        f"- Ticker: {order['ticker']}\n"
        f"- Tipo: {order['type']}\n"
        f"- Strike: {order['strike']}\n"
        f"- Scadenza: {order['expiry']}\n"
        f"- Premio: {order['premium']}$\n"
        f"- Tipo ordine: {order['trade_type']}\n"
        f"- Volume: {order['volume']}\n"
        f"- Open Interest: {order['oi']}\n\n"
        f"Questo è un ordine considerabile smart money? Perché? Rispondi in modo tecnico ma chiaro."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content.strip()
