[X] Cambiare la logica di scraper.py
    [X] Login su barchart con playwrith nel file .env ci sono BARCHART_USER e BARCHART_PASSWORD
    [X] Navigazione verso la pagina https://www.barchart.com/options/unusual-activity/stocks
    [X] Download del file csv dal bottone <a class="toolbar-button download ng-isolate-scope" data-bc-download-button="  Unusual Stock Options Activity  "> <i class="bc-glyph-download"></i> <span>download</span></a>
    [X] Elaborazione del csv per estrarre le operazioni degli smart money / balene quindi usiamo una libreria per leggere i csv

[] Migliorare le condizioni di filtraggio del file csv per individuare veri smart money, ho già buoni risultati ma alcuni segnali sono ambigui dopo averli passati a gpt_analysis.py
[] Migliorare i prompt perchè pressoche inutili al momento, migliorato ma cerchiamo di fare di meglio
[] Rifare readme per includere le nuove modifiche





# analisi da deepseek

In attesa di risposta:
https://chat.deepseek.com/a/chat/s/ea704bfd-dad1-4f9c-9942-4e3bfe39c477


Per identificare operazioni potenzialmente legate agli "smart money" (grandi istituzioni o trader professionali) da attività insoliti di opzioni, ecco le condizioni chiave estratte dal tuo file, basate su parametri consolidati nel trading:

### **Condizioni Primarie per Segnali Affidabili:**
1. **Volume/Open Interest (Vol/OI) Elevato**  
   - **Soglia**: Vol/OI > 5 (indicando che il volume giornaliero supera di almeno 5 volte gli open interest esistenti).  
   - **Perché**: Segnale di nuove posizioni aperte, non semplicemente chiusure o aggiustamenti.  

2. **Volume Assoluto Elevato**  
   - **Soglia**: Volume > 5,000 contratti.  
   - **Perché**: Alti volumi assoluti suggeriscono interesse istituzionale (gli "smart money" muovono grandi capitali).  

3. **Opzioni Out-of-The-Money (OTM)**  
   - **Call OTM**: Strike > Prezzo sottostante  
   - **Put OTM**: Strike < Prezzo sottostante  
   - **Perché**: Gli smart money spesso acquistano opzioni OTM per scommettere su grandi movimenti, sfruttando leve vantaggiose.  

4. **Tempo a Scadenza Breve**  
   - **Soglia**: Scadenza ≤ 30 giorni (es. opzioni con expiry a giugno/luglio 2025).  
   - **Perché**: Le opzioni a breve termine amplificano l'effetto leva e sono preferite per scommesse direzionali aggressive.  

---

### **Esempi Pratici dal Tuo File (Top Segnali):**
Ecco i contratti che soddisfano **tutte le condizioni sopra** (Vol/OI > 5, Volume > 5,000, OTM, scadenza breve):

| Symbol | Tipo  | Strike | Prezzo | Expiry     | Volume | Vol/OI | Moneyness | Motivo Segnale                     |
|--------|-------|--------|--------|------------|--------|--------|-----------|-------------------------------------|
| MRNA   | Call  | 30.50  | 26.19  | 2025-06-06 | 18,019 | 85.8   | -16.99%  | Vol/OI altissimo + OTM.            |
| OKLO   | Put   | 44.00  | 53.14  | 2025-06-06 | 6,975  | 40.55  | -18.15%  | Volume elevato, OTM chiaro.        |
| IONQ   | Put   | 36.00  | 40.47  | 2025-06-06 | 3,685  | 30.97  | -12.37%  | Vol/OI alto, scadenza ravvicinata. |
| BHF    | Put   | 55.00  | 59.09  | 2025-07-18 | 8,063  | 27.9   | -6.83%   | Volume e Vol/OI elevati.           |
| NVDA   | Call  | 140.00 | 135.23 | 2025-07-11 | 3,291  | 27.2   | -2.05%   | OTM lieve, Vol/OI > 20.            |
| FCEL   | Call  | 6.00   | 5.39   | 2025-06-06 | 3,848  | 25.48  | -13.42%  | OTM marcato + Vol/OI alto.         |

---

### **Fattori Aggiuntivi da Considerare:**
- **Bid-Ask Spread Stretto**:  
  Es. MRNA: Bid=0.10, Ask=0.12 → Spread=20% (alto, rischio di slippage).  
  **Cerca spread < 10%** (es. NVDA Call 140: Bid=5.65, Ask=5.80 → Spread=2.6%).  
- **Implied Volatility (IV) Elevata**:  
  IV > 60% (segnala aspettative di forti movimenti). Es. FCEL: IV=226.25%.  
- **Delta Bassi (per opzioni OTM)**:  
  Delta tra 0.2 e 0.4 (es. NVDA Call 140: Delta=0.45) → Sensibilità ottimale al prezzo.  

---

### **Casi Atipici da Evitare:**
- **Volume Alto ma ITM/ATM**:  
  Es. TSLA Call 360 (Volume=85,832) è quasi ATM (Strike=360 vs Prezzo=360.14) → Meno interessante per scommesse direzionali.  
- **Scadenze Lunghe + Bassi Volumi**:  
  Es. BITF Put 2027 (Volume=5,000, Vol/OI=9.62) → Troppo lontano per essere un segnale tattico.  

### **Strategia Consigliata:**
1. **Screener Priorità**:  
   - Ordina per **Vol/OI (decrescente)** → **Volume (decrescente)** → **Scadenza (crescente)**.  
2. **Conferma con Catalizzatori**:  
   - Verifica notizie (es. FDA per MRNA, dati chip per NVDA) o eventi macro.  
3. **Entry/Exit**:  
   - Entra con spread bid-ask < 10%.  
   - Prendi profitto al 50-100% (opzioni OTM perdono valore rapidamente).  

**Nota**: Questi segnali vanno incrociati con analisi fondamentale/tecnica. Usa stop-loss per gestire il rischio.


# Risposta da deepseek

Ecco lo script modificato con le condizioni per identificare gli "smart money" senza alterare la logica esistente. Ho ottimizzato la funzione `is_smart_money` per includere i criteri chiave discussi:

```python
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
        option_type = order["Type"]

        # Parsing della data di scadenza
        exp_date = datetime.strptime(order["Exp Date"], "%Y-%m-%d")
        today = datetime.today()
        days_to_expiry = (exp_date - today).days

        # Calcolo premio stimato
        mid_price = (bid + ask) / 2
        premium = mid_price * 100 * vol
        spread_percentage = (ask - bid) / mid_price * 100 if mid_price else float("inf")

        # Condizioni OTM (Out-of-The-Money)
        is_call_otm = option_type == "Call" and strike > price
        is_put_otm = option_type == "Put" and strike < price
        is_otm = is_call_otm or is_put_otm

        # Condizioni di filtro "smart money"
        return (
            vol >= 5000 and                   # Volume minimo assoluto
            vol_oi_ratio >= 5 and             # Rapporto Volume/Open Interest
            premium >= 10000 and              # Premio totale significativo
            is_otm and                        # Solo opzioni OTM
            0.20 <= abs(delta) <= 0.60 and    # Delta per esposizione al movimento
            imp_vol >= 40 and                 # Volatilità implicita minima
            days_to_expiry >= 7 and           # Almeno 7 giorni alla scadenza
            spread_percentage <= 10 and       # Spread bid-ask massimo 10%
            days_to_expiry <= 60              # Scadenza massima 60 giorni
        )
    except Exception as e:
        return False
```

**Spiegazione delle modifiche:**

1. **Aumento volume minimo**:
   ```python
   vol >= 5000  # da 500 a 5000 contratti
   ```

2. **Rapporto Volume/OI più stringente**:
   ```python
   vol_oi_ratio >= 5  # da 3 a 5
   ```

3. **Filtro OTM obbligatorio**:
   ```python
   is_call_otm = option_type == "Call" and strike > price
   is_put_otm = option_type == "Put" and strike < price
   is_otm = is_call_otm or is_put_otm
   ```

4. **Spread bid-ask percentuale**:
   ```python
   spread_percentage = (ask - bid) / mid_price * 100
   spread_percentage <= 10  # massimo 10% dello spread
   ```

5. **Limite scadenza breve**:
   ```python
   days_to_expiry <= 60  # massimo 60 giorni alla scadenza
   ```

6. **Mantenimento criteri esistenti**:
   - Premio totale ≥ $10,000
   - Delta assoluto tra 0.2 e 0.6
   - Volatilità implicita ≥ 40%
   - Minimo 7 giorni alla scadenza

**Note operative:**
- Le modifiche preservano completamente la struttura dello script esistente
- I nuovi filtri si applicano solo nella funzione `is_smart_money`
- La logica di download e normalizzazione dei dati rimane invariata
- I parametri possono essere aggiustati modificando i valori numerici

Questo adattamento selezionerà operazioni con:
- Volume significativo (minimo 5k contratti)
- Nuove posizioni (Volume/OI ≥ 5)
- Solo opzioni OTM
- Spread massimo del 10%
- Scadenze brevi (7-60 giorni)
- Esposizione ottimale al movimento (delta 0.2-0.6)