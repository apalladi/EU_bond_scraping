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

# Sidebar per i filtri (prima parte)
with st.sidebar:
    st.header("🔍 Filtri di ricerca")
    
    anni_scadenza_min, anni_scadenza_max = st.slider(
        "Seleziona il range di scadenza (anni)",
        min_value=0, max_value=100, value=(2, 7)
    )

    prezzo_max = st.number_input(
        "💰 Prezzo massimo",
        min_value=0, max_value=999,
        value=100
    )

    # ✅ Default percentile volume = 75
    volume_min = st.slider(
        "📈 Percentile volume minimo",
        min_value=0, max_value=100,
        value=75
    )

    escludi_BTP = st.checkbox("Escludi BTP", value=True)
    escludi_XS = st.checkbox("Escludi bond XS", value=True)

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

# ---------------------------------------------------
# ✅ Applica tutti i filtri tranne ISIN
# ---------------------------------------------------

sub_df = filter_df(
    df_results,
    anni_scadenza_min=anni_scadenza_min,
    anni_scadenza_max=anni_scadenza_max,
    prezzo_max=prezzo_max,
    sort_by=sort_by,
    escludi_BTP=escludi_BTP,
    escludi_XS=escludi_XS
)

sub_df = sub_df[sub_df['percentili volume'] >= volume_min]

# ---------------------------------------------------
# ✅ Prefissi disponibili DOPO i filtri
# ---------------------------------------------------

unique_prefixes = sorted({idx[:2] for idx in sub_df.index if isinstance(idx, str)})

# ---------------------------------------------------
# ✅ Sidebar: prefissi cliccabili in 4 colonne + RESET
# ---------------------------------------------------

with st.sidebar:

    st.markdown("**Prefissi ISIN disponibili (clicca per filtrare):**")

    # Recupera selezione precedente
    selected_prefix = st.session_state.get("selected_prefix", None)

    # ✅ 4 colonne per riga
    cols = st.columns(4)
    i = 0

    for p in unique_prefixes:
        if cols[i].button(p, key=f"prefix_{p}"):
            st.session_state["selected_prefix"] = p
            selected_prefix = p
        i = (i + 1) % 4

    # ✅ Bottone per resettare il filtro Paese
    if st.button("Mostra tutti"):
        st.session_state["selected_prefix"] = None
        selected_prefix = None

# ---------------------------------------------------
# ✅ Applica filtro ISIN se selezionato
# ---------------------------------------------------

if selected_prefix:
    sub_df = sub_df[sub_df.index.str.startswith(selected_prefix)]

# Verifica duplicati
if sub_df.index.duplicated().any():
    st.warning("L'indice contiene duplicati. Potrebbero esserci conflitti nella visualizzazione.")

# Stile colonna percentili volume
styled_df = sub_df.style.applymap(
    color_by_rating, subset=['percentili volume']
)

# Formattazione colonne float
float_columns = df_results.select_dtypes(include=['float64']).columns
styled_df = styled_df.format({col: "{:.2f}" for col in float_columns})

# Output
st.write(f"### 📋 Risultati filtrati ({len(sub_df)} bond trovati)")
st.write(styled_df)

st.sidebar.markdown("### Credit: Andrea Palladino")

# Badge aggiornamento dati
st.sidebar.markdown(
    f"📅 Ultimo aggiornamento dati: **{pd.to_datetime('today').strftime('%d-%m-%Y')}**"
)
