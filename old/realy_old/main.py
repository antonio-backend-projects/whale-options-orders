from utils.scraper import get_unusual_option_activity
from utils.gpt_analysis import analyze_order

def main():
    print("📡 Cercando opzioni sospette su titoli principali...\n")
    orders = get_unusual_option_activity()

    if not orders:
        print("❌ Nessuna opzione sospetta trovata al momento.")
        return

    for order in orders:
        print(f"\n📈 Ordine sospetto su {order['ticker']} (Call {order['strike']} @ {order['expiry']})")
        print(f"💰 Premio: ${order['premium']:,.0f} | Vol: {order['volume']} | OI: {order['oi']}")
        print(f"⚡ Tipo: {order['trade_type']}")

        analysis = analyze_order(order)
        print("\n🧠 Analisi AI:")
        print(analysis)
        print("-" * 50)

if __name__ == "__main__":
    main()
