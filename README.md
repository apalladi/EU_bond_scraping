# EU_bond_scraping

## 1. Descrizione
Questo repository è pensato per eseguire **web scraping** dalla Borsa Italiana, raccogliendo informazioni su oltre **2000 bond europei**, sia **governativi** che **societari**.  
A differenza di altri pacchetti simili, **EU Bond Scraping** include anche i dati relativi ai **volumi mensili degli ultimi 12 mesi**, permettendo di individuare i titoli più **liquidi** (che tipicamente presentano spread bid-ask più bassi).

## 2. Installazione
Per iniziare, segui questi passaggi:

1. **Clona il repository**:
```
git clone git@github.com:apalladi/EU_bond_scraping.git
cd EU_bond_scraping
```

2. Crea l'ambiente virtuale e installa le dipendenze:
```   
python -m venv venv
source venv/bin/activate  # Su macOS/Linux
venv\Scripts\activate      # Su Windows
```
seguito da:
```
pip install -r requirements.txt
```

## 3. Utilizzo
Puoi avviare lo scraping manualmente con:
```
python web_scraping.py
```
La lista degli ISIN viene scaricata dal seguente [sito](https://www.simpletoolsforinvestors.eu/data/listino/listino.csv](sito).

Tuttavia, questa operazione non è necessaria. I risultati vengono aggiornati automaticamente ogni giorno tramite una GitHub Action e salvati nella cartella results.
In alternativa, puoi utilizzare la interfaccia grafica costruita con **Streamlit** per esplorare i dati in modo più intuitivo.

## Autore
Sviluppato da Andrea Palladino. Feedback e contributi sono sempre benvenuti! 

