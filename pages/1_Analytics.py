import streamlit as st
import pandas as pd
import plotly.express as px
# from streamlit_gsheets import GSheetsConnection

# 1. Configurazione della pagina
st.set_page_config(page_title="Analytics Dashboard", page_icon="📊", layout="wide")

st.title("📊 Dashboard Analytics")
st.markdown("Monitoraggio interattivo delle stringhe tecniche generate.")
st.divider()

# 2. Connessione e Lettura dati
conn = st.connection("gsheets", type="gsheets")
df = conn.read(ttl=60)

try:
    df = conn.read(ttl=60) # Aumentato ttl per performance
    df = df.dropna(how="all")
    
    if df.empty:
        st.info("Nessun dato ancora registrato.")
    else:
        # Conversione Timestamp
        if "Timestamp" in df.columns:
            df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors='coerce')
        
        # --- SIDEBAR: FILTRI TEMPORALI ---
        st.sidebar.header("⚙️ Filtri")
        if "Timestamp" in df.columns:
            data_min = df["Timestamp"].min().date()
            data_max = df["Timestamp"].max().date()
            
            intervallo = st.sidebar.date_input(
                "Seleziona periodo:",
                value=(data_min, data_max),
                min_value=data_min,
                max_value=data_max
            )
            
            # Filtro effettivo
            if len(intervallo) == 2:
                start_date, end_date = intervallo
                mask = (df["Timestamp"].dt.date >= start_date) & (df["Timestamp"].dt.date <= end_date)
                df = df.loc[mask]
        
        # --- METRICHE PRINCIPALI ---
        st.subheader("💡 Metriche Chiave")
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Totale Stringhe", len(df))
        top_macro = df["Macro_Categoria"].mode()[0] if not df["Macro_Categoria"].dropna().empty else "N/A"
        col2.metric("Macro Categoria Top", str(top_macro))
        top_part = df["Particolare"].mode()[0] if not df["Particolare"].dropna().empty else "N/A"
        col3.metric("Particolare Top", str(top_part))
        
        st.divider()
        
        # --- GRAFICI PLOTLY ---
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.subheader("Distribuzione per Categoria")
            fig1 = px.pie(df, names="Macro_Categoria", hole=0.4, template="plotly_white")
            st.plotly_chart(fig1, use_container_width=True)
            
        with col_g2:
            st.subheader("Volume nel Tempo")
            df_temp = df.groupby(df["Timestamp"].dt.date).size().reset_index(name="Conteggio")
            fig2 = px.line(df_temp, x="index", y="Conteggio", template="plotly_white", markers=True)
            st.plotly_chart(fig2, use_container_width=True)
            
        st.divider()
        
        # --- ANALISI PILLS (BAR CHART PLOTLY) ---
        if "Pills_Selezionati" in df.columns:
            all_pills = [p.strip() for item in df["Pills_Selezionati"].dropna().astype(str) for p in item.split(",") if p.strip()]
            if all_pills:
                pills_counts = pd.Series(all_pills).value_counts().reset_index()
                pills_counts.columns = ["Opzione", "Conteggio"]
                
                st.subheader("🏷️ Utilizzo Opzioni Extra")
                fig3 = px.bar(pills_counts, x="Conteggio", y="Opzione", orientation='h', color="Conteggio", template="plotly_white")
                st.plotly_chart(fig3, use_container_width=True)

        st.divider()
        
        # --- TABELLA LOG ---
        st.subheader("📋 Ultimi Log")
        st.dataframe(df.tail(20).sort_index(ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Errore: {e}")
