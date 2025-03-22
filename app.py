import streamlit as st
import pandas as pd
from web_scraping import filter_df

# Layout migliorato
st.set_page_config(page_title="Cerca Bond Europei", layout="wide")

# URL del file CSV nel repository GitHub
CSV_URL = 'results/bond_info_extracted.csv'

# Caricamento dati
@st.cache_data

def load_data():
    df = pd.read_csv(CSV_URL, index_col=0)
    new_columns_order = ['median_monthly_volume_million', 'ratings', 'Prezzo ufficiale',
                         'Rendimento effettivo a scadenza lordo', 'anni_scadenza', 'Scadenza',
                         'Numero Contratti', 'Volume Ultimo', 'Volume totale',
                         'Rendimento effettivo a scadenza netto', 'Duration modificata',
                         'min_monthly_volume_million', 'max_monthly_volume_million']
    
    df = df.loc[:, new_columns_order]
    df = df.rename(columns={'median_monthly_volume_million': 'volume mensile mediano',
                            'ratings': 'percentili volume',
                            'Rendimento effettivo a scadenza lordo': 'rendimento lordo',
                            'Volume Ultimo': 'volume ultimo scambio',
                            'Volume totale': 'Volume ultimo giorno',
                            'min_monthly_volume_million': 'volume mensile minimo',
                            'max_monthly_volume_million': 'Volume mensile massimo'})
    
    return df

df_results = load_data()

st.title("📈 Cerca Bond Europei")
st.markdown("Filtra e trova i bond più adatti alle tue esigenze.")

# Sidebar per i filtri
with st.sidebar:
    st.header("🔍 Filtri di ricerca")
    
    anni_scadenza_min, anni_scadenza_max = st.slider(
        "Seleziona il range di scadenza (anni)",
        min_value=0, max_value=100, value=(2, 7)
    )

    prezzo_max = st.number_input("💰 Prezzo massimo", min_value=0, max_value=200, value=100)

    escludi_BTP = st.checkbox("Escludi BTP", value=True)
    escludi_romania = st.checkbox("Escludi bond Romania", value=True)

    sort_by = st.selectbox("📊 Ordina per:", 
                           ["volume mensile mediano", "anni_scadenza", "Prezzo ufficiale"],
                           index=0)

# Filtra automaticamente i dati ogni volta che l'utente modifica un filtro
sub_df = filter_df(
    df_results,
    anni_scadenza_min=anni_scadenza_min,
    anni_scadenza_max=anni_scadenza_max,
    prezzo_max=prezzo_max,
    ncontratti_min=0,
    sort_by=sort_by,
    escludi_BTP=escludi_BTP,
    escludi_romania=escludi_romania
)

# Mostra i risultati
st.write(f"### 📋 Risultati filtrati ({len(sub_df)} bond trovati)")
st.dataframe(sub_df)

# Badge con data ultimo aggiornamento
st.sidebar.markdown(
    f"📅 Ultimo aggiornamento dati: **{pd.to_datetime('today').strftime('%d-%m-%Y')}**"
)
