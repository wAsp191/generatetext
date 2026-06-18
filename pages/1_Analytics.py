import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# =========================================================
# CONFIGURAZIONE PAGINA
# =========================================================
st.set_page_config(page_title="Analytics Dashboard", page_icon="📊", layout="wide")

st.title("📊 Dashboard Analytics")
st.markdown("Monitoraggio in tempo reale delle stringhe tecniche generate.")
st.divider()

# =========================================================
# CONNESSIONE E CARICAMENTO DATI
# =========================================================
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Leggiamo i dati (ttl=10 significa che ricarica i dati nuovi ogni 10 secondi)
    df = conn.read(ttl=10)
    
    # Pulizia base: eliminiamo eventuali righe vuote lette per errore dal foglio
    df = df.dropna(how="all")
    
    if df.empty:
        st.info("Nessun dato ancora registrato nel database Analytics.")
    else:
        # Assicuriamoci che il Timestamp sia letto correttamente come data
        if "Timestamp" in df.columns:
            df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors='coerce')
        
        # =========================================================
        # SEZIONE 1: KPI PRINCIPALI
        # =========================================================
        st.subheader("💡 Metriche Chiave")
        col1, col2, col3 = st.columns(3)
        
        totale_generazioni = len(df)
        top_macro = df["Macro_Categoria"].value_counts().idxmax() if not df["Macro_Categoria"].dropna().empty else "N/A"
        top_particolare = df["Particolare"].value_counts().idxmax() if not df["Particolare"].dropna().empty else "N/A"
        
        col1.metric("Totale Stringhe Generate", totale_generazioni)
        col2.metric("Macro Categoria più usata", top_macro)
        col3.metric("Particolare più richiesto", top_particolare)
        
        st.divider()
        
        # =========================================================
        # SEZIONE 2: GRAFICI
        # =========================================================
        col_grafico1, col_grafico2 = st.columns(2)
        
        with col_grafico1:
            st.subheader("Generazioni per Macro Categoria")
            macro_counts = df["Macro_Categoria"].value_counts()
            st.bar_chart(macro_counts)
            
        with col_grafico2:
            st.subheader("Top 5 Particolari")
            part_counts = df["Particolare"].value_counts().head(5)
            st.bar_chart(part_counts)
            
        st.divider()
        
        # =========================================================
        # SEZIONE 3: DATI GREZZI RECENTI
        # =========================================================
        st.subheader("📋 Ultimi 10 Log Generati")
        # Mostriamo solo le ultime 10 righe, ordinate dalla più recente
        ultimi_log = df.tail(10).sort_index(ascending=False)
        st.dataframe(ultimi_
