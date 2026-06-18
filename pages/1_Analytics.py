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
            pills_series = df["Pills_Selezionati"].dropna().astype(str)
            
            all_pills = []
            for item in pills_series:
                parts = [p.strip() for p in item.split(",") if p.strip()]
                all_pills.extend(parts)
            
            if all_pills:
                pills_counts = pd.Series(all_pills).value_counts().reset_index()
                pills_counts.columns = ["Opzione Extra (Pill)", "Numero di Utilizzi"]
                
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
        ultimi_log = df.tail(20).sort_index(ascending=False)
        st.dataframe(ultimi_log, use_container_width=True)
        
        st.divider()

       st.divider()

        # --- ELENCO NOTE LIBERE CON MOLTIPLIPICATORE ---
        st.subheader("📝 Classifica Note Libere più Utilizzate")
        
        if "Note_Libere" in df.columns:
            # Filtriamo via i valori nulli, vuoti o spazi bianchi
            df_note = df[df["Note_Libere"].notna() & (df["Note_Libere"].astype(str).str.strip() != "")].copy()
            
            if not df_note.empty:
                # Standardizziamo in maiuscolo per evitare che "Trial" e "trial" vengano contati come diversi
                df_note["Nota_Pulita"] = df_note["Note_Libere"].astype(str).str.strip().str.upper()
                
                # Raggruppiamo per nota e contiamo le ripetizioni
                classifica_note = df_note["Nota_Pulita"].value_counts().reset_index()
                classifica_note.columns = ["Nota Libera Digitata", "Numero di Ripetizioni"]
                
                # Aggiungiamo un tocco visivo: se è ripetuta più di una volta mettiamo un badge
                def aggiungi_moltiplicatore(row):
                    if row["Numero di Ripetizioni"] > 1:
                        return f"🔥 {row['Numero di Ripetizioni']} Volte"
                    return "1 Volta"
                
                classifica_note["Frequenza"] = classifica_note.apply(aggiungi_moltiplicatore, axis=1)
                
                # Selezioniamo le colonne da mostrare in modo pulito
                df_visualizzazione = classifica_note[["Nota Libera Digitata", "Frequenza"]]
                
                # Mostriamo la tabella con il moltiplicatore
                st.dataframe(df_visualizzazione, use_container_width=True, hide_index=True)
            else:
                st.info("Nessuna nota libera è stata ancora inserita nei log.")
        else:
            st.warning("Colonna 'Note_Libere' non trovata nel database.")

except Exception as e:
    st.error(f"Errore nel caricamento dei dati: {e}")
