import streamlit as st

st.set_page_config(page_title="Generatore Descrizioni Professionali", layout="wide")

st.title("✍️ Configurazione Descrizione Universale")

# --- DATABASE DEI SOTTOASSIEMI (Modifica qui per aggiornare i testi) ---
# Puoi aggiungere o cambiare queste voci facilmente
dati_prodotti = {
    "Elettronica": {
        "Particolari": ["Chipset ad alta velocità", "Display LED antiriflesso", "Batteria a lunga durata"],
        "Compatibilità": ["Standard USB-C", "Windows/Mac/Linux", "Protocollo Zigbee"]
    },
    "Meccanica": {
        "Particolari": ["Acciaio inossidabile 316L", "Ingranaggi a taglio laser", "Guarnizioni in Viton"],
        "Compatibilità": ["Flangia ISO 5211", "Attacco rapido 1/4", "Standard DIN 2576"]
    },
    "Arredamento": {
        "Particolari": ["Finitura a cera naturale", "Cerniere ammortizzate", "Tessuto idrorepellente"],
        "Compatibilità": ["Montaggio a parete", "Sistemi modulari serie X", "Standard ambientali Classe A"]
    }
}

# --- INTERFACCIA ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Selezione Guidata")
    # 1. MACRO (A tendina)
    macro_scelta = st.selectbox("1. MACRO (Categoria)", list(dati_prodotti.keys()))
    
    # 2. PARTICOLARE (A tendina basata sulla Macro)
    opzioni_particolare = dati_prodotti[macro_scelta]["Particolari"]
    particolare_scelto = st.selectbox("2. PARTICOLARE (Dettaglio)", opzioni_particolare)
    
    # 5. COMPATIBILITÀ (A tendina basata sulla Macro)
    opzioni_comp = dati_prodotti[macro_scelta]["Compatibilità"]
    compatibilita_scelta = st.selectbox("5. COMPATIBILITÀ", opzioni_comp)

with col2:
    st.subheader("Dati Variabili")
    # 3. DIMENSIONI (Compilabile)
    dimensioni = st.text_input("3. DIMENSIONI", placeholder="es. 120x60x10 cm")
    
    # 4. EXTRA (Compilabile)
    extra = st.text_area("4. EXTRA", placeholder="es. Certificazione CE, Garanzia estesa...")

# --- GENERAZIONE TESTO ---
st.divider()

if st.button("🚀 GENERA DESCRIZIONE"):
    testo_finale = f"""**SCHEDA TECNICA UNIVERSALE**

**1. MACRO**
Ambito: {macro_scelta}

**2. PARTICOLARE**
Dettaglio tecnico: {particolare_scelto}

**3. DIMENSIONI**
Ingombro: {dimensioni if dimensioni else "Vedere allegato tecnico"}

**4. EXTRA**
Note aggiuntive: {extra if extra else "Nessun extra specificato"}

**5. COMPATIBILITÀ**
Requisiti: {compatibilita_scelta}
"""

    st.subheader("Testo Pronto:")
    st.text_area("Copia da qui:", value=testo_finale, height=350)
    
    with st.expander("Anteprima visiva"):
        st.markdown(testo_finale)

# Istruzioni per il collaboratore
st.sidebar.markdown("""
### Come usare l'app:
1. Seleziona la **Macro** categoria.
2. I campi **Particolare** e **Compatibilità** si aggiorneranno da soli.
3. Inserisci manualmente le **Dimensioni** e gli **Extra**.
4. Clicca su **Genera** e copia il risultato.
""")
