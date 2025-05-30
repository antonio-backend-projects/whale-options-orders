## 📘 Whale options orders — Smart Money Options Monitor

https://chatgpt.com/share/68396729-4c5c-8011-ac6f-54bdb95ff2f2

### 📊 Monitora automaticamente le opzioni call sospette su titoli principali (tipo Sweep) e interpreta i flussi con OpenAI.

---

### 🚀 Funzionalità

* ✅ Scraping da sito pubblico gratuito (Barchart)
* 📈 Rilevamento opzioni call con:

  * Tipo ordine: **Sweep**
  * **Premio ≥ \$500k**
  * Volume > Open Interest
  * Scadenza entro 90 giorni
* 🤖 Analisi automatica con **OpenAI GPT-4**
* 🔐 Sicurezza API tramite `.env`

---

## 🖥️ Requisiti

* Python **3.9+** installato
* Connessione Internet

---

## 🔧 Setup su Windows

### 1. Clona o scarica il progetto

```bash
git clone https://github.com/tuo-utente/smartmoney_tsla.git
cd smartmoney_tsla
```

### 2. Crea un ambiente virtuale (Windows)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Installa le dipendenze

```bash
pip install -r requirements.txt
```

---

### 4. Crea il file `.env` nella root del progetto

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> ❗ Non condividere mai la tua chiave OpenAI.

---

### 5. Avvia lo script

```bash
python main.py
```

---

## 📂 Struttura del progetto

```
smartmoney_tsla/
│
├── .env                   ← la tua chiave OpenAI qui
├── main.py                ← script principale
├── requirements.txt       ← librerie Python richieste
├── README.md              ← questo file
└── utils/
    ├── scraper.py         ← scraping dei dati opzioni da Barchart
    └── gpt_analysis.py    ← analisi dei flussi con OpenAI
```

---

## ✅ Esempio di output

```
📡 Cercando opzioni sospette su titoli principali...

📈 Ordine sospetto su TSLA (Call 350 @ Jul 19, 2025)
💰 Premio: $2,200,000 | Vol: 2,396 | OI: 1,391
⚡ Tipo: Sweep

🧠 Analisi AI:
Questo ordine è molto probabilmente attribuibile a uno smart money trader...
--------------------------------------------------
```

---

## 📌 Personalizzazioni future (facoltative)

* Esportazione CSV
* Notifiche via Telegram o email
* Interfaccia Web con Dash
* Filtro per titoli o settori specifici

---

## ❓ Domande frequenti

**🟠 Non vedo dati?**
Il sito pubblico potrebbe non avere sweep rilevanti nel momento della richiesta. Riprova più tardi.

**🔴 Errore da OpenAI?**
Verifica che la chiave `.env` sia corretta e attiva. Puoi anche testare la tua API qui: [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)

---

## 👨‍💻 Autore

Script generato con ❤️ da \[Antonio Trento] — Open Source Intelligence applicata al flusso opzioni.

---

Fammi sapere se vuoi che ti impacchetti tutto in uno zip oppure in un repo GitHub pubblicabile.
