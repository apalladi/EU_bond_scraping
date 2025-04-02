# pylint: disable=C0301

"""
Modulo per il recupero e l'analisi dei dati di obbligazioni da Borsa Italiana.

Contiene funzioni per estrarre valori numerici da pagine HTML, effettuare richieste HTTP per ottenere dati di volume,
calcolare volumi medi mensili e altre statistiche, e creare DataFrame contenenti informazioni relative a obbligazioni
basate su ISIN. Include anche la possibilità di estrarre dati per singoli ISIN o per una lista di ISIN.

Funzioni principali:
- `extract_value_after_keyword`: Estrae valori numerici da testo HTML dopo una parola chiave.
- `fetch_data`: Esegue una richiesta HTTP POST per ottenere dati da Borsa Italiana.
- `compute_avg_monthly_volume`: Calcola volumi medi mensili, minimi e massimi per un ISIN.
- `extract_single_ISIN`: Estrae informazioni per un singolo ISIN da una pagina web di Borsa Italiana.
- `extract_multiple_ISIN`: Estrae informazioni per più ISIN e le restituisce in un DataFrame ordinato.
"""

from datetime import datetime
import requests
import pandas as pd
import numpy as np
from tqdm import tqdm
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from src.analysis import compute_ratings_volume_new


def extract_value_after_keyword(keyword, html_text):
    """
    Estrae il valore numerico che segue un determinato 'keyword' all'interno di un testo HTML.

    Questa funzione cerca una parola chiave (keyword) all'interno di una stringa di testo HTML, quindi estrae il valore numerico
    che si trova subito dopo il tag <span> con la classe 't-text -right', che si suppone contenga il valore desiderato.

    Parametri:
    - keyword (str): La stringa da cercare all'interno del testo HTML.
    - html_text (str): Il testo HTML nel quale effettuare la ricerca.

    Restituisce:
    - str: Il valore numerico (come stringa) che segue la parola chiave all'interno del tag <span>, se trovato.
    - None: Se la parola chiave o il valore numerico non vengono trovati.

    Note:
    - La funzione cerca la parola chiave nel testo HTML, quindi cerca un tag <span> con la classe 't-text -right' dopo di essa.
    - Se il valore numerico viene trovato, viene estratto e restituito come stringa, rimuovendo gli spazi bianchi circostanti.
    """

    start_index = html_text.find(keyword)
    if start_index != -1:
        # Trova il tag <span> che contiene il valore numerico
        span_start = html_text.find('<span class="t-text -right">', start_index)
        if span_start != -1:
            # Estrai il valore numerico
            span_end = html_text.find("</span>", span_start)
            value = html_text[
                span_start + len('<span class="t-text -right">') : span_end
            ].strip()
            return value
    return None


def fetch_data(cookies, headers, json_data):
    """
    Effettua una richiesta HTTP POST al servizio di Borsa Italiana per ottenere i dati di volume.

    Parametri:
    - cookies (dict): Un dizionario contenente i cookie necessari per la richiesta HTTP.
    - headers (dict): Un dizionario contenente le intestazioni HTTP da includere nella richiesta.
    - json_data (dict): Un dizionario contenente i dati JSON necessari per la richiesta, che includono
      parametri come il tipo di dati richiesti, la lingua, ecc.

    Restituisce:
    - dict: Un dizionario contenente i dati JSON ricevuti dalla risposta se la richiesta è riuscita,
      altrimenti `None` in caso di errore nella richiesta.

    Eccezioni:
    - RequestException: Se si verifica un errore durante l'esecuzione della richiesta HTTP (ad esempio timeout o errore di connessione),
      la funzione cattura l'eccezione e restituisce `None`.

    Note:
    - La funzione imposta un timeout di 10 secondi per evitare che la richiesta resti bloccata troppo a lungo.
    """

    try:
        response = requests.post(
            "https://charts.borsaitaliana.it/charts/services/ChartWService.asmx/GetCvals",
            cookies=cookies,
            headers=headers,
            json=json_data,
            timeout=10,  # Timeout di 10 secondi per evitare richieste troppo lunghe
        )
        response.raise_for_status()  # Solleva un'eccezione se la risposta non è 200
        return response.json()
    except RequestException as e:
        print(f"Errore nella richiesta: {e}")
        return None


def compute_avg_monthly_volume(ISIN, avg=True, verbose=False):
    """
    Calcola il volume mensile medio, minimo e massimo per un determinato ISIN, utilizzando i dati di Borsa Italiana.

    La funzione invia una richiesta HTTP al servizio di Borsa Italiana per ottenere i dati di volume per l'ISIN specificato.
    In seguito, calcola i volumi mensili in base alle opzioni richieste: la mediana, il minimo e il massimo, oppure restituisce i singoli valori di volume.

    Parametri:
    - ISIN (str): Il codice ISIN del titolo per il quale calcolare i volumi mensili.
    - avg (bool): Se True, calcola la mediana, il minimo e il massimo del volume mensile in milioni; se False, restituisce la lista di volumi mensili.
    - verbose (bool): Se True, stampa i risultati dei calcoli o dei dati estratti.

    Restituisce:
    - dict: Un dizionario con la mediana, il minimo e il massimo dei volumi mensili in milioni se `avg=True`.
    - pandas.Series: Una serie di volumi mensili in milioni se `avg=False`.
    - None: Se si verificano errori durante il recupero o il processamento dei dati.

    Eccezioni:
    - La funzione restituisce None se non è possibile ottenere i dati o se il formato dei dati ricevuti non è corretto.

    Note:
    - La funzione effettua una richiesta HTTP POST al servizio di Borsa Italiana per ottenere i dati dei volumi.
    - I volumi sono restituiti in milioni di unità (valori divisi per 10^6).
    - Se `verbose` è True, vengono stampati i risultati dei calcoli o i dati grezzi ricevuti.
    """

    cookies = {
        "_ga": "GA1.1.353865695.1741296987",
        "CookieControlTC": "CQN2GpmQN2GpmEDAJBITBfFgAAAAAEPgABCYK5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFcmr_jf_try3_L979P2yPMav--w992IYgwtk2fcC5l3rfk4L77CdmiZ9W1MFTIkAXbpgkIG2jkxqIqhQtUQK1ph2NCZKUJ2lE_AyRDmIsbOsBC43zcWxvIBM831_-6u87I_W9u1_bu55Zcwz37te__JarExOlMPWjv3-tonN_fkfe_4_f8X8fm90ibfvJa2_2rX297-_eW3_-__--_99_v______7__fr__v______2AA",
        "CookieControlAC": "",
        "CookieControl": '{"necessaryCookies":["JSESSIONID","cf_clearance","wt3_eid","wt3_sid","wt_rla","AWSELB","AWSELBCORS","_ga_LVDQM0FBJC","_ga"],"iabConsent":"","statement":{},"consentDate":1741296988620,"consentExpiry":364,"interactedWith":true,"user":"7C529F91-E3C0-4F34-B8E4-72B0185608AE"}',
        "_ga_LVDQM0FBJC": "GS1.1.1741556156.4.1.1741557154.0.0.0",
    }

    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "it,en;q=0.9",
        "content-type": "application/json; charset=UTF-8",
        "origin": "https://charts.borsaitaliana.it",
        "priority": "u=1, i",
        "referer": "https://charts.borsaitaliana.it/charts/Bit/NVTChart.aspx?code=FR001400HI98&lang=it",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    json_data = {
        "request": {
            "SampleTime": "1m",
            "TimeFrame": "1y",
            "RequestedDataSetType": "cvals",
            "ChartPriceType": "price",
            "Key": ISIN + ".MOT",
            "OffSet": 0,
            "FromDate": None,
            "ToDate": None,
            "KeyType": "Topic",
            "KeyType2": "Topic",
            "Language": "it-IT",
        },
    }

    # Recupera i dati
    data_json = fetch_data(cookies, headers, json_data)

    if not data_json:
        return None

    # Estrai e processa i dati
    try:
        data = pd.DataFrame(data_json["d"], columns=["timestamp", "volume"])
    except KeyError:
        print("Dati JSON non validi.")
        return None

    # Calcola i volumi medi mensili
    if avg:
        median_monthly_volume_million = round(data["volume"].median() / 10**6, 2)
        min_monthly_volume_million = round(data["volume"].min() / 10**6, 2)
        max_monthly_volume_million = round(data["volume"].max() / 10**6, 2)
        result = (
            median_monthly_volume_million,
            min_monthly_volume_million,
            max_monthly_volume_million,
        )
    else:
        result = data["volume"] / 10**6

    if verbose:
        print(result)

    return result


def extract_single_ISIN(ISIN, verbose=False):
    """
    Estrae informazioni relative a un'obbligazione da una pagina web di Borsa Italiana, utilizzando il codice ISIN.

    La funzione effettua una richiesta HTTP GET alla pagina web specifica per l'ISIN fornito, estrae valori associati a determinate
    parole chiave (ad esempio, "Volume Ultimo", "Prezzo ufficiale", "Rendimento effettivo a scadenza netto"),
    e calcola informazioni aggiuntive come la durata e il volume mensile medio di scambio. I risultati sono restituiti in un DataFrame.

    Parametri:
    - ISIN (str): Il codice ISIN dell'obbligazione per la quale estrarre i dati.
    - verbose (bool): Se True, stampa i valori estratti per ciascuna parola chiave. Il default è False.

    Restituisce:
    - pd.DataFrame: Un DataFrame contenente i dati estratti per l'ISIN fornito, con informazioni come volume, rendimento e scadenza.

    Funzionalità:
    - Recupera i dati dalla pagina web di Borsa Italiana per un determinato ISIN.
    - Estrae i valori associati a parole chiave predefinite (come volume, rendimento, scadenza).
    - Calcola e aggiunge la durata residua dell'obbligazione (anni alla scadenza).
    - Calcola i volumi medi, minimi e massimi di scambio mensile degli ultimi 12 mesi per l'ISIN.

    Eccezioni:
    - La funzione gestisce gli errori nella richiesta HTTP e stampa un messaggio se la pagina non viene recuperata correttamente.
    """

    # URL della pagina
    url = (
        "https://www.borsaitaliana.it/borsa/obbligazioni/mot/euro-obbligazioni/scheda/"
        + ISIN
        + ".html"
    )

    # Simuliamo un browser con User-Agent
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Effettua la richiesta HTTP
    response = requests.get(url, headers=headers, timeout=20)

    # Controlla se la richiesta ha avuto successo
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Converte il contenuto di soup in stringa per la ricerca manuale
        html_text = str(soup)

        # Estrai i valori per le parole chiave richieste
        keywords = [
            "Numero Contratti",
            "Volume Ultimo",
            "Volume totale",
            "Prezzo ufficiale",
            "Rendimento effettivo a scadenza netto",
            "Rendimento effettivo a scadenza lordo",
            "Duration modificata",
            "Scadenza",
            "Tasso Cedola su base Annua",
        ]

        keywords_list = []
        values_list = []

        for _, keyword in enumerate(keywords):
            value = extract_value_after_keyword(keyword, html_text)
            if value:
                # Rimuovi eventuali caratteri di separazione e formatta correttamente il numero
                value = value.replace(".", "").replace(",", ".")
            else:
                value = np.nan
            keywords_list.append(keyword)
            values_list.append(value)  # Converto in int per i valori interi

            if verbose:
                print(f"{keyword}: {value}")

    else:
        print("Errore nel recupero della pagina:", response.status_code)

    # Crea un DataFrame con i valori estratti
    df = pd.DataFrame(values_list, index=keywords_list, columns=[ISIN])

    # Crea la trasposizione del DataFrame
    df = df.transpose()  # Facciamo la trasposizione per avere ISIN come colonna

    # aggiungi anni scadenza (diverso da modified duration)
    today = pd.Timestamp(datetime.today())
    df["Scadenza"] = pd.to_datetime(df["Scadenza"], dayfirst=True)
    anni_scadenza = (pd.Timestamp(df["Scadenza"].iloc[0]) - today).days / 365
    df["anni_scadenza"] = round(anni_scadenza, 2)
    df["Scadenza"] = df["Scadenza"].dt.date

    # calcola mediana, min e max dei volumi di scambio mensili degli ultimi 12 mesi
    median_volume, min_volume, max_volume = compute_avg_monthly_volume(ISIN)
    df["median_monthly_volume_million"] = median_volume
    df["min_monthly_volume_million"] = min_volume
    df["max_monthly_volume_million"] = max_volume

    return df


def extract_multiple_ISIN(list_ISIN):
    """
    Estrae informazioni relative a più obbligazioni da Borsa Italiana utilizzando i codici ISIN forniti in una lista.

    La funzione itera su una lista di codici ISIN, estrae i dati relativi a ciascun ISIN utilizzando la funzione `extract_single_ISIN`,
    e restituisce un DataFrame con tutte le informazioni estratte. I dati vengono poi ordinati per volume medio mensile.

    Parametri:
    - list_ISIN (list): Una lista di codici ISIN per i quali estrarre le informazioni dalle pagine web di Borsa Italiana.

    Restituisce:
    - pd.DataFrame: Un DataFrame contenente i dati estratti per tutti gli ISIN nella lista, con informazioni come volume, rendimento e scadenza,
      ordinato in base al volume medio mensile.

    Funzionalità:
    - Per ogni ISIN nella lista, la funzione esegue l'estrazione dei dati tramite la funzione `extract_single_ISIN`.
    - Gestisce gli errori di estrazione, stampando un messaggio nel caso in cui non sia possibile estrarre i dati per un ISIN.
    - Combina i risultati estratti in un unico DataFrame.
    - Converte i valori numerici (eccetto la colonna "Scadenza") in tipo `float`.
    - Calcola nuove metriche di rating e volume tramite la funzione `compute_ratings_volume_new`.
    - Ordina i dati in base al volume medio mensile, in ordine decrescente.

    Eccezioni:
    - La funzione gestisce gli errori di estrazione per ciascun ISIN individuale e stampa un messaggio se non riesce a estrarre i dati.
    """

    list_results = []
    for i in tqdm(range(len(list_ISIN))):
        try:
            list_results.append(extract_single_ISIN(ISIN=list_ISIN[i]))
        except:
            print("Could not extract ISIN:", list_ISIN[i])

    df = pd.concat(list_results)

    c_names = df.columns

    for name in c_names:
        if name != "Scadenza":
            df[name] = df[name].astype(float)

    df2 = compute_ratings_volume_new(df)
    df2.sort_values("median_monthly_volume_million", ascending=False, inplace=True)

    return df2
