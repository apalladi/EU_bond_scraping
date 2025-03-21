import streamlit as st
import pandas as pd
from web_scraping import filter_df

# URL del file CSV nel repository GitHub
CSV_URL = 'results/bond_info_extracted.csv'

# Caricamento dati
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL, index_col=0)
    return df

df_results = load_data()

# Interfaccia Streamlit
st.title("Cerca Bond Europei")

# Slider per la scadenza minima e massima
anni_scadenza_min = st.slider("Scadenza minima (anni)", min_value=0, max_value=100, value=2)
anni_scadenza_max = st.slider("Scadenza massima (anni)", min_value=0, max_value=100, value=7)

# Input per il prezzo massimo
prezzo_max = st.number_input("Prezzo massimo", min_value=0, max_value=200, value=100)

# Checkbox per escludere BTP e bond rumeni
escludi_BTP = st.checkbox("Escludi BTP", value=True)
escludi_romania = st.checkbox("Escludi bond Romania", value=True)

# Applica il filtro
sub_df = filter_df(df_results,
                   anni_scadenza_min=anni_scadenza_min,
                   anni_scadenza_max=anni_scadenza_max,
                   prezzo_max=prezzo_max,
                   ncontratti_min=0,  # Default
                   sort_by="median_monthly_volume_million",  # Default
                   escludi_BTP=escludi_BTP,
                   escludi_romania=escludi_romania)

# Mostra i risultati
st.write(f"### Risultati filtrati ({len(sub_df)} bond trovati)")
st.dataframe(sub_df)