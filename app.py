import streamlit as st

st.set_page_config(page_title="Configuratore Prodotti Aziendale", layout="wide")

# --- DATABASE SOTTOASSIEMI ---
# Qui puoi aggiungere o modificare le opzioni per ogni categoria
database = {
    "Plastic Component": {
        "Particolari": ["Stampaggio a iniezione", "Termoformato", "Resistente UV", "Tecnopolimero rinforzato"],
        "Compatibilità": ["Aggancio a scatto", "Saldatura a ultrasuoni", "Sede per vite autofilettante"]
    },
    "Glass Component": {
        "Particolari": ["Vetro Temprato", "Vetro Stratificato", "Finitura Acidata", "Bordo filo lucido"],
        "Compatibilità": ["Supporti a pinza", "Incollaggio UV", "Guarnizioni in silicone"]
    },
    "Wood Component": {
        "Particolari": ["Essenza Rovere", "Multistrato pioppo", "Finitura naturale", "Trattamento ignifugo"],
        "Compatibilità": ["Incastro a coda di rondine", "Ferramenta standard", "Fissaggio a scomparsa"]
    },
    "Electric Component": {
        "Particolari": ["Cablaggio UL/CSA", "Grado IP65", "Protezione termica", "Contatti dorati"],
        "Compatibilità": ["Tensione 220V", "Attacco DIN", "Segnale 4-20mA"]
    },
    "Fastner": {
        "Particolari": ["Acciaio Zincato", "Classe 8.8", "Testa esagonale", "Filettatura parziale"],
        "Compatibilità": ["Foro pre-filettato", "Chiave fissa/bussola", "Rosetta piana"]
    },
    "Fitting": {
        "Particolari": ["Ottone nichelato", "Innesto rapido", "Tenuta o-ring", "Filetto gas"],
        "Compatibilità": ["Tubi flessibili Rilsan", "Pressione max 10 bar", "Fluidi oleodinamici"]
    }
}

# --- INTERFACCIA APP ---
st.title("🛠️ Generatore Descrizioni Universali")
st.info("Seleziona la Macro categoria per visualizzare le opzioni specifiche.")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📌 Configurazione")
    
    # 1. MACRO
    macro = st.selectbox("Seleziona Macro Categoria:", list(database.keys()))
    
    # 2. PARTICOLARE (Dinamico)
    particolare = st.selectbox("Seleziona Particolare:", database[macro]["Particolari"])
    
    # 5. COMPATIBILITÀ (Dinamico)
    compatibilita = st.selectbox("Seleziona Compatibilità:", database[macro]["Compatibilità"])

with col2:
    st.subheader("📏 Dati Variabili")
    
    # 3. DIMENSIONI (Libero)
    dimensioni = st.text_input("Inserisci Dimensioni:", placeholder="es. Ø 20mm, L: 500mm")
    
    # 4. EXTRA (Libero)
    extra = st.text_area("Inserisci Note Extra:", placeholder="es. Lotto minimo 100pz, Certificato ISO...")

# --- GENERAZIONE RISULTATO ---
st.divider()

if st.button("✨ GENERA DESCRIZIONE FINALE", use_container_width=True):
    descrizione_finale = f"""**IDENTIFICATIVO PRODOTTO: {macro.upper()}**

**1. MACRO**
Categoria di riferimento: {macro}

**2. PARTICOLARE**
Caratteristica costruttiva: {particolare}

**3. DIMENSIONI**
Dati dimensionali: {dimensioni if dimensioni else "Vedi disegno tecnico allegato"}

**4. EXTRA**
Note e Certificazioni: {extra if extra else "Nessuna nota aggiuntiva"}

**5. COMPATIBILITÀ**
Interfacce e accoppiamenti: {compatibilita}
"""

    st.subheader("📋 Copia la descrizione:")
    st.text_area("Testo pronto per il catalogo:", value=descrizione_finale, height=350)
    st.success("Testo generato correttamente!")
