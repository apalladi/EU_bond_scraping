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

df_results = load_data()

# Sidebar per i filtri
with st.sidebar:
    st.header("🔍 Filtri di ricerca")
    
    anni_scadenza_min, anni_scadenza_max = st.slider(
        "Seleziona il range di scadenza (anni)",
        min_value=0, max_value=100, value=(2, 7)
    )

    prezzo_max = st.number_input("💰 Prezzo massimo", min_value=0, max_value=999, value=100)

    escludi_BTP = st.checkbox("Escludi BTP", value=True)
    escludi_romania = st.checkbox("Escludi bond XS", value=True)

    sort_by = st.selectbox("📊 Ordina per:", 
                           ["volume mensile mediano (M)", "anni_scadenza", "Prezzo ufficiale", "rendimento lordo"],
                           index=0)

    # Aggiungi il credito nella sidebar prima della data
    st.markdown("### Credit: Andrea Palladino")

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

# Verifica che l'indice sia unico
if sub_df.index.duplicated().any():
    st.warning("L'indice contiene duplicati. Potrebbero esserci conflitti nella visualizzazione.")

# Applica il colore alla colonna 'percentili volume' per lo styling
styled_df = sub_df.style.applymap(color_by_rating, subset=['percentili volume'])

# Selezionare solo le colonne con valori numerici float
float_columns = df_results.select_dtypes(include=['float64']).columns
# Applicare il formato a due decimali solo alle colonne float
styled_df = styled_df.format({col: "{:.2f}" for col in float_columns})

# Mostra i risultati con il DataFrame stilizzato
st.write(f"### 📋 Risultati filtrati ({len(sub_df)} bond trovati)")

# Usa `st.write()` per visualizzare il DataFrame stilizzato
st.write(styled_df)

# Badge con data ultimo aggiornamento
st.sidebar.markdown(
    f"📅 Ultimo aggiornamento dati: **{pd.to_datetime('today').strftime('%d-%m-%Y')}**"
)
