import pandas as pd
import numpy as np


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


def improve_data(df):
    # remove duplicates, if any
    df= df.loc[~df.index.duplicated(keep='first')]

    # sistema il problema delle scadenze negative
    df.loc[df['anni_scadenza'] < 0, 'anni_scadenza'] += 100
    
    new_columns_order = ['median_monthly_volume_million', 'ratings', 'Prezzo ufficiale',
                         'Rendimento effettivo a scadenza lordo', 'anni_scadenza', 'Scadenza',
                         'Numero Contratti', 'Volume Ultimo', 'Volume totale',
                         'Rendimento effettivo a scadenza netto', 'Duration modificata',
                         'min_monthly_volume_million', 'max_monthly_volume_million']
    
    df = df.loc[:, new_columns_order]
    df = df.rename(columns={'median_monthly_volume_million': 'volume mensile mediano (M)',
                            'ratings': 'percentili volume',
                            'Rendimento effettivo a scadenza lordo': 'rendimento lordo',
                            'Volume Ultimo': 'volume ultimo scambio',
                            'Volume totale': 'Volume ultimo giorno',
                            'min_monthly_volume_million': 'volume mensile minimo',
                            'max_monthly_volume_million': 'Volume mensile massimo'})
    
    return df

# Funzione per colorare le celle in base al rating con trasparenza
def color_by_rating(val):
    if val >= 75:
        color = 'background-color: rgba(0, 128, 0, 0.2)'  # verde chiaro con trasparenza
    elif val >= 50:
        color = 'background-color: rgba(255, 255, 0, 0.3)'  # giallo chiaro con trasparenza
    elif val >= 25:
        color = 'background-color: rgba(255, 165, 0, 0.3)'  # arancione chiaro con trasparenza
    else:
        color = 'background-color: rgba(255, 0, 0, 0.4)'  # rosso chiaro con trasparenza
    return color