# pylint: disable=C0301

"""
Modulo di analisi per il trattamento e la gestione dei dati delle obbligazioni.

Questo modulo contiene diverse funzioni per analizzare e manipolare i dati relativi alle obbligazioni, tra cui:
- Calcolo dei rating basati sul volume medio mensile di scambio.
- Filtraggio dei dati delle obbligazioni secondo criteri specifici (ad esempio, durata, prezzo, numero di contratti).
- Pulizia e riorganizzazione dei dati, rimuovendo duplicati e correggendo valori errati.
- Assegnazione di colori in base ai rating per visualizzare graficamente i valori.
"""

import pandas as pd
import numpy as np


def compute_ratings_volume_new(df2):
    """
    Calcola i rating per ciascuna obbligazione in base al volume medio mensile di scambio.

    La funzione assegna un rating a ciascuna obbligazione nel DataFrame in base al volume medio mensile di scambio. Le obbligazioni con
    volume pari a zero ricevono un rating di 0. Le obbligazioni con volume diverso da zero sono classificate in base ai quantili del volume.

    Parametri:
    - df2 (pd.DataFrame): Un DataFrame che contiene una colonna "median_monthly_volume_million" che rappresenta il volume medio mensile in milioni.

    Restituisce:
    - pd.DataFrame: Un DataFrame con i rating assegnati per ciascuna obbligazione. La colonna "ratings" contiene il rating calcolato per ogni obbligazione,
      in base al volume medio mensile.

    Dettagli operativi:
    - Le obbligazioni con volume pari a zero (nessun scambio) vengono assegnate un rating di 0.
    - Le obbligazioni con volume diverso da zero sono classificate utilizzando i quantili del volume medio mensile.
    - I rating sono assegnati usando `np.digitize` che posiziona ciascun valore nel corrispondente intervallo di quantili. Il valore di `ratings` è incrementato di 1.
    """

    df = df2.copy()
    df["median_monthly_volume_million"] = df["median_monthly_volume_million"].fillna(0)
    #df.fillna(0, inplace=True)

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


def filter_df(
    df2,
    anni_scadenza_min,
    anni_scadenza_max,
    prezzo_max,
    ncontratti_min,
    sort_by="Volume totale",
    escludi_BTP=False,
    escludi_XS=False,
):
    """
    Filtra un DataFrame di obbligazioni in base a criteri specificati e restituisce un DataFrame ordinato.

    La funzione applica filtri sul DataFrame delle obbligazioni per includere solo quelle che soddisfano
    determinate condizioni, come la durata alla scadenza, il prezzo massimo e il numero minimo di contratti.
    È anche possibile escludere i bond italiani (BTP) o quelli con codici ISIN che iniziano con "XS".

    Parametri:
    - df2 (pd.DataFrame): Il DataFrame contenente i dati delle obbligazioni, con colonne come "anni_scadenza",
      "Prezzo ufficiale", "Numero Contratti" e altri dati pertinenti.
    - anni_scadenza_min (float): Il numero minimo di anni alla scadenza per includere l'obbligazione.
    - anni_scadenza_max (float): Il numero massimo di anni alla scadenza per includere l'obbligazione.
    - prezzo_max (float): Il prezzo massimo per includere l'obbligazione.
    - ncontratti_min (int): Il numero minimo di contratti per includere l'obbligazione.
    - sort_by (str, opzionale): Il campo per ordinare il DataFrame. Il valore predefinito è "Volume totale".
    - escludi_BTP (bool, opzionale): Se True, esclude i bond italiani (BTP) (codice ISIN che inizia con "IT").
      Il valore predefinito è False.
    - escludi_XS (bool, opzionale): Se True, esclude i bond con codice ISIN che inizia con "XS".
      Il valore predefinito è False.

    Restituisce:
    - pd.DataFrame: Un DataFrame filtrato e ordinato in base ai criteri specificati.

    Dettagli operativi:
    - Filtra le obbligazioni in base alla durata (anni di scadenza), al prezzo e al numero di contratti.
    - Se `escludi_BTP` è True, vengono esclusi i bond italiani (codici ISIN che iniziano con "IT").
    - Se `escludi_XS` è True, vengono esclusi i bond con codici ISIN che iniziano con "XS".
    - Il DataFrame risultante è ordinato in base al campo `sort_by` in ordine decrescente.
    """

    df = df2.copy()
    #df.fillna(0, inplace=True)

    mask = (
        (df["anni_scadenza"] <= anni_scadenza_max)
        & (df["anni_scadenza"] >= anni_scadenza_min)
        & (df["Prezzo ufficiale"] <= prezzo_max)
        & (df["Numero Contratti"] >= ncontratti_min)
    )

    sub_df = df.loc[mask, :]

    if escludi_BTP:
        sub_df = sub_df[~sub_df.index.str.startswith("IT")]

    if escludi_XS:
        sub_df = sub_df[~sub_df.index.str.startswith("XS")]

    sub_df.sort_values(sort_by, ascending=False, inplace=True)

    return sub_df


def improve_data(df):
    """
    Pulisce e riorganizza i dati delle obbligazioni nel DataFrame.

    Questa funzione esegue diverse operazioni di pulizia e riorganizzazione sui dati di un DataFrame
    che contiene informazioni sulle obbligazioni. Le operazioni includono la rimozione dei duplicati,
    la correzione delle scadenze negative, la riorganizzazione delle colonne e la rinomina di alcune colonne
    per migliorarne la comprensibilità.

    Parametri:
    - df (pd.DataFrame): Il DataFrame contenente i dati delle obbligazioni. Il DataFrame deve avere
      colonne come 'anni_scadenza', 'Volume Ultimo', 'Volume totale', 'Scadenza' e altre informazioni
      relative alle obbligazioni.

    Restituisce:
    - pd.DataFrame: Un DataFrame riorganizzato, senza duplicati, con le scadenze corrette e le colonne rinominate.

    Operazioni effettuate:
    - Rimozione dei duplicati nel DataFrame, mantenendo solo il primo valore per ogni indice duplicato.
    - Correzione delle scadenze negative, aggiungendo 100 anni alle scadenze con valore inferiore a 0.
    - Riorganizzazione delle colonne secondo un ordine predefinito.
    - Rinomina di alcune colonne per una maggiore chiarezza, ad esempio:
      - 'median_monthly_volume_million' diventa 'volume mensile mediano (M)',
      - 'Volume Ultimo' diventa 'volume ultimo scambio',
      - 'Volume totale' diventa 'Volume ultimo giorno', e altre.

    Esempio:
    df = improve_data(df)
    """

    # remove duplicates, if any
    df = df.loc[~df.index.duplicated(keep="first")]

    # sistema il problema delle scadenze negative
    df.loc[df["anni_scadenza"] < 0, "anni_scadenza"] += 100

    new_columns_order = [
        "median_monthly_volume_million",
        "ratings",
        "Tasso Cedola su base Annua",
        "Prezzo ufficiale",
        "Rendimento effettivo a scadenza lordo",
        "anni_scadenza",
        "Scadenza",
        "Numero Contratti",
        "Volume Ultimo",
        "Volume totale",
        "Rendimento effettivo a scadenza netto",
        "Duration modificata",
        "min_monthly_volume_million",
        "max_monthly_volume_million",
    ]

    df = df.loc[:, new_columns_order]
    df = df.rename(
        columns={
            "median_monthly_volume_million": "volume mensile mediano (M)",
            "ratings": "percentili volume",
            "Rendimento effettivo a scadenza lordo": "rendimento lordo",
            "Volume Ultimo": "volume ultimo scambio",
            "Volume totale": "Volume ultimo giorno",
            "min_monthly_volume_million": "volume mensile minimo",
            "max_monthly_volume_million": "Volume mensile massimo",
            "Tasso Cedola su base Annua": "Cedola",
        }
    )

    return df


def color_by_rating(val):
    """
    Restituisce una stringa di stile CSS per colorare un valore in base al suo rating.

    La funzione assegna un colore di sfondo (in formato rgba) a un valore numerico
    in base alla sua classificazione. I valori più alti ricevono colori più favorevoli
    (verde), mentre i valori più bassi ricevono colori meno favorevoli (rosso).

    Parametri:
    - val (float): Il valore del rating da colorare. Si aspetta un valore numerico
      compreso tra 0 e 100.

    Restituisce:
    - str: Una stringa contenente il codice di stile CSS per il colore di sfondo
      associato al valore. I colori restituiti sono:
      - Verde chiaro per valori >= 75,
      - Giallo chiaro per valori >= 50,
      - Arancione chiaro per valori >= 25,
      - Rosso chiaro per valori < 25.

    Esempio:
    color = color_by_rating(80)
    # Restituisce: 'background-color: rgba(0, 128, 0, 0.2)' (verde chiaro)

    color = color_by_rating(60)
    # Restituisce: 'background-color: rgba(255, 255, 0, 0.3)' (giallo chiaro)
    """

    if val >= 75:
        color = "background-color: rgba(0, 128, 0, 0.2)"  # verde chiaro con trasparenza
    elif val >= 50:
        color = (
            "background-color: rgba(255, 255, 0, 0.3)"  # giallo chiaro con trasparenza
        )
    elif val >= 25:
        color = "background-color: rgba(255, 165, 0, 0.3)"  # arancione chiaro con trasparenza
    else:
        color = "background-color: rgba(255, 0, 0, 0.4)"  # rosso chiaro con trasparenza
    return color
