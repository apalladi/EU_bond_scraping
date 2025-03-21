import requests
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import time
import concurrent.futures
from datetime import datetime
from tqdm import tqdm
from bs4 import BeautifulSoup


def extract_value_after_keyword(keyword, html_text):
    """Funzione per estrarre il valore che segue una stringa"""
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


def compute_avg_monthly_volume(ISIN, avg=True, verbose=False):

    # Cookies che hai estratto dal browser
    cookies = {
        "_ga": "GA1.1.353865695.1741296987",
        "CookieControlTC": "CQN2GpmQN2GpmEDAJBITBfFgAAAAAEPgABCYK5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFcmr_jf_try3_L979P2yPMav--w992IYgwtk2fcC5l3rfk4L77CdmiZ9W1MFTIkAXbpgkIG2jkxqIqhQtUQK1ph2NCZKUJ2lE_AyRDmIsbOsBC43zcWxvIBM831_-6u87I_W9u1_bu55Zcwz37te__JarExOlMPWjv3-tonN_fkfe_4_f8X8fm90ibfvJa2_2rX297-_eW3_-__--_99_v______7__fr__v______2AA",
        "CookieControlAC": "",
        "CookieControl": '{"necessaryCookies":["JSESSIONID","cf_clearance","wt3_eid","wt3_sid","wt_rla","AWSELB","AWSELBCORS","_ga_LVDQM0FBJC","_ga"],"iabConsent":"","statement":{},"consentDate":1741296988620,"consentExpiry":364,"interactedWith":true,"user":"7C529F91-E3C0-4F34-B8E4-72B0185608AE"}',
        "_ga_LVDQM0FBJC": "GS1.1.1741556156.4.1.1741557154.0.0.0",
    }

    # Headers per la richiesta
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

    # Dati della richiesta (payload)
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

    # Effettua la richiesta POST
    response = requests.post(
        "https://charts.borsaitaliana.it/charts/services/ChartWService.asmx/GetCvals",
        cookies=cookies,
        headers=headers,
        json=json_data,
    )

    # Verifica la risposta
    if response.status_code == 200:
        if verbose:
            print("Dati ricevuti con successo!")
            print(response.json())  # Qui vedrai i dati JSON ricevuti
    else:
        if verbose:
            print(f"Errore nel recupero dei dati: {response.status_code}")
            print(response.text)

    data = pd.DataFrame(json.loads(response.text)["d"], columns=["timestamp", "volume"])

    if avg:
        median_monthly_volume_million = round(data["volume"].median() / 10 ** 6, 2)
        min_monthly_volume_million = round(data["volume"].min() / 10 ** 6, 2)
        max_monthly_volume_million = round(data["volume"].max() / 10 ** 6, 2)
        return (
            median_monthly_volume_million,
            min_monthly_volume_million,
            max_monthly_volume_million,
        )

    else:
        avg_monthly_volume_million = data["volume"] / 10 ** 6
        return avg_monthly_volume_million


def extract_single_ISIN(ISIN, verbose=False):
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
    response = requests.get(url, headers=headers)

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
        ]

        keywords_list = []
        values_list = []

        for i, keyword in enumerate(keywords):
            value = extract_value_after_keyword(keyword, html_text)
            if value:
                # Rimuovi eventuali caratteri di separazione e formatta correttamente il numero
                value = value.replace(".", "").replace(",", ".")
                # value = float(value)
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
    anni_scadenza = (pd.Timestamp(df["Scadenza"].iloc[0]) - today).days / 365
    df["anni_scadenza"] = round(anni_scadenza, 2)

    # calcola mediana, min e max dei volumi di scambio mensili degli ultimi 12 mesi
    median, min, max = compute_avg_monthly_volume(ISIN)
    df["median_monthly_volume_million"] = median
    df["min_monthly_volume_million"] = min
    df["max_monthly_volume_million"] = max

    return df


def compute_ratings_volume_new(df2):
    df = df2.copy(deep=True)
    df.fillna(0, inplace=True)

    df_null = df[df["median_monthly_volume_million"] == 0]
    df_null["ratings"] = 0

    # Calcolo dei quantili
    df_others = df[df["median_monthly_volume_million"] != 0]
    quantiles = np.percentile(
        df_others["median_monthly_volume_million"], np.arange(1, 100, 1)
    )
    # Assegna i rating usando np.digitize
    df_others["ratings"] = np.digitize(
        df_others["median_monthly_volume_million"], quantiles, right=True
    )
    df_others["ratings"] = df_others["ratings"] + 1

    df2 = pd.concat([df_null, df_others])

    return df2


def extract_multiple_ISIN(list_ISIN):
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


def extract_multiple_ISIN_parallel(list_ISIN):
    list_results = []

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=5
    ) as executor:  # Limita il numero di richieste simultanee
        futures = {
            executor.submit(extract_single_ISIN, ISIN): ISIN for ISIN in list_ISIN
        }

        for future in tqdm(
            concurrent.futures.as_completed(futures),
            total=len(futures),
            desc="Processing ISINs",
        ):
            ISIN = futures[future]  # Recupera l'ISIN corrispondente
            try:
                result = future.result()
                if result is not None:
                    list_results.append(result)
            except Exception as e:
                print(f"Could not extract ISIN {ISIN}: {e}")

            time.sleep(0.5)  # Aspetta 0.5 secondi per evitare errori 429

    if list_results:
        return pd.concat(list_results)
    else:
        print("No valid ISINs were extracted.")
        return None


def filter_df(
    df2,
    anni_scadenza_min,
    anni_scadenza_max,
    prezzo_max,
    ncontratti_min,
    sort_by="Volume totale",
    escludi_BTP=False,
    escludi_romania=True,
):

    df = df2.copy(deep=True)
    df.fillna(0, inplace=True)

    mask = (
        (df["anni_scadenza"] <= anni_scadenza_max)
        & (df["anni_scadenza"] >= anni_scadenza_min)
        & (df["Prezzo ufficiale"] <= prezzo_max)
        & (df["Numero Contratti"] >= ncontratti_min)
    )

    sub_df = df.loc[mask, :]

    if escludi_BTP:
        # select non italian bond
        selected_index = []
        for idx in sub_df.index:
            if idx[0:2] != "IT":
                selected_index.append(idx)
        sub_df = sub_df.loc[selected_index, :]

    if escludi_romania:
        # select non romanian bond
        selected_index = []
        for idx in sub_df.index:
            if idx[0:2] != "XS":
                selected_index.append(idx)
        sub_df = sub_df.loc[selected_index, :]

    sub_df.sort_values(sort_by, ascending=False, inplace=True)

    return sub_df


if __name__ == "__main__":
    path = "https://www.simpletoolsforinvestors.eu/data/listino/listino.csv"
    data = pd.read_csv(path, sep=";")
    data = data[data["Currency"] == "EUR"]
    list_ISIN = np.array(data["ISIN Code"])
    list_ISIN = list_ISIN[0:100]
    print("Number of ISIN", len(list_ISIN))
    
    df = extract_multiple_ISIN(list_ISIN)
    
    os.makedirs("results", exist_ok=True)
    df.to_csv("results/bond_info_extracted.csv")
