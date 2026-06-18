import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configurazione della pagina
st.set_page_config(page_title="Analytics Dashboard", page_icon="📊", layout="wide")

st.title("📊 Dashboard Analytics")
st.markdown("Monitoraggio in tempo reale delle stringhe tecniche generate.")
st.divider()

# 2. Connessione sicura a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Lettura dati con cache a 10 secondi
    df = conn.read(ttl=10)
    
    # Pulizia righe completamente vuote
    df = df.dropna(how="all")
    
    if df.empty:
        st.info("Nessun dato ancora registrato nel database Analytics.")
    else:
        # Controllo e conversione Timestamp
        if "Timestamp" in df.columns:
            df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors='coerce')
        
        # --- METRICHE PRINCIPALI ---
        st.subheader("💡 Metriche Chiave")
        col1, col2, col3 = st.columns(3)
        
        totale_generazioni = len(df)
        
        if "Macro_Categoria" in df.columns and not df["Macro_Categoria"].dropna().empty:
            top_macro = df["Macro_Categoria"].value_counts().idxmax()
        else:
            top_macro = "N/A"
            
        if "Particolare" in df.columns and not df["Particolare"].dropna().empty:
            top_particolare = df["Particolare"].value_counts().idxmax()
        else:
            top_particolare = "N/A"
        
        col1.metric("Totale Stringhe Generate", totale_generazioni)
        col2.metric("Macro Categoria più usata", str(top_macro))
        col3.metric("Particolare più richiesto", str(top_particolare))
        
        st.divider()
        
        # --- ANALISI PILLS (TAG EXTRA) ---
        st.subheader("🏷️ Utilizzo delle Opzioni Extra (Pills)")
        
        if "Pills_Selezionati" in df.columns:
            # Prendiamo tutti i pills, rimuoviamo i valori vuoti e separiamo le stringhe con la virgola
            pills_series = df["Pills_Selezionati"].dropna().astype(str)
            
            all_pills = []
            for item in pills_series:
                # Separiamo se ci sono più elementi (es: "Scorrevoli, Con Foro") e puliamo gli spazi bianchi
                parts = [p.strip() for p in item.split(",") if p.strip()]
                all_pills.extend(parts)
            
            if all_pills:
                # Creiamo un DataFrame con il conteggio di ogni singolo Pills
                pills_counts = pd.Series(all_pills).value_counts().reset_index()
                pills_counts.columns = ["Opzione Extra (Pill)", "Numero di Utilizzi"]
                
                # Mostriamo i dati affiancando un grafico e una tabella
                col_pills_grafico, col_pills_tabella = st.columns([2, 1])
                
                with col_pills_grafico:
                    st.bar_chart(data=pills_counts, x="Opzione Extra (Pill)", y="Numero di Utilizzi")
                
                with col_pills_tabella:
                    st.dataframe(pills_counts, use_container_width=True, hide_index=True)
            else:
                st.info("Nessuna opzione extra (Pills) ancora registrata nei log.")
        else:
            st.warning("Colonna 'Pills_Selezionati' non trovata nel database.")
            
        st.divider()
        
        # --- GRAFICI DI CATEGORIA ---
        col_grafico1, col_grafico2 = st.columns(2)
        
        with col_grafico1:
            st.subheader("Generazioni per Macro Categoria")
            if "Macro_Categoria" in df.columns:
                macro_counts = df["Macro_Categoria"].value_counts()
                st.bar_chart(macro_counts)
            
        with col_grafico2:
            st.subheader("Top 5 Particolari")
            if "Particolare" in df.columns:
                part_counts = df["Particolare"].value_counts().head(5)
                st.bar_chart(part_counts)
            
        st.divider()
        
        # --- TABELLA ULTIMI DATI (AUMENTATA A 20) ---
        st.subheader("📋 Ultimi 20 Log Registrati")
        # Estraiamo gli ultimi 20 elementi salvati e li ordiniamo dal più recente al più vecchio
        ultimi_log = df.tail(20).sort_index(ascending=False)
        st.dataframe(ultimi_log, use_container_width=True)

except Exception as e:
    st.error(f"Errore nel caricamento dei dati: {e}")
