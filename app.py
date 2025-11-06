import streamlit as st
import pandas as pd
from src.analysis import filter_df, improve_data, color_by_rating

# Layout migliorato
st.set_page_config(page_title="Cerca Bond Europei", layout="wide")

# URL del file CSV nel repository GitHub
CSV_URL = 'results/bond_info_extracted.csv'

# Caricamento dati
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL, index_col=0)
    return df
    
df_results = load_data()
df_results = improve_data(df_results)

# Sidebar per i filtri
with st.sidebar:
    st.header("🔍 Filtri di ricerca")
    
    anni_scadenza_min, anni_scadenza_max = st.slider(
        "Seleziona il range di scadenza (anni)",
        min_value=0, max_value=100, value=(2, 7)
    )

    prezzo_max = st.number_input(
        "💰 Prezzo massimo",
        min_value=0, max_value=999, value=100
    )

    # ✅ Nuovo filtro: volume minimo (percentile)
    volume_min = st.slider(
        "📈 Percentile volume minimo",
        min_value=0, max_value=100, value=75
    )

    escludi_BTP = st.checkbox("Escludi BTP", value=True)
    escludi_XS = st.checkbox("Escludi bond XS", value=True)

    isin_prefix = st.text_input(
        "Filtra per prime lettere ISIN (es. IT, FR, ES, DE)",
        value=""
    ).strip().upper()

    sort_by = st.selectbox(
        "📊 Ordina per:", 
        [
            "volume mensile mediano (M)",
            "anni_scadenza",
            "Prezzo ufficiale",
            "rendimento lordo"
        ],
        index=0
    )

    st.markdown("### Credit: Andrea Palladino")

# Filtra automaticamente i dati
sub_df = filter_df(
    df_results,
    anni_scadenza_min=anni_scadenza_min,
    anni_scadenza_max=anni_scadenza_max,
    prezzo_max=prezzo_max,
    sort_by=sort_by,
    escludi_BTP=escludi_BTP,
    escludi_XS=escludi_XS
)

# ✅ Filtro aggiuntivo: volume minimo
sub_df = sub_df[sub_df['percentili volume'] >= volume_min]

# Filtro ISIN se specificato
if isin_prefix:
    sub_df = sub_df[sub_df.index.str.startswith(isin_prefix)]

# Verifica indice
if sub_df.index.duplicated().any():
    st.warning("L'indice contiene duplicati. Potrebbero esserci conflitti nella visualizzazione.")

# Styling colonna percentili volume
styled_df = sub_df.style.applymap(
    color_by_rating, subset=['percentili volume']
)

# Formatta le colonne float
float_columns = df_results.select_dtypes(include=['float64']).columns
styled_df = styled_df.format({col: "{:.2f}" for col in float_columns})

# Mostra i risultati
st.write(f"### 📋 Risultati filtrati ({len(sub_df)} bond trovati)")
st.write(styled_df)

# Badge aggiornamento dati
st.sidebar.markdown(
    f"📅 Ultimo aggiornamento dati: **{pd.to_datetime('today').strftime('%d-%m-%Y')}**"
)
