import streamlit as st

st.set_page_config(page_title="Generatore Descrizioni v2", layout="wide")

st.title("✍️ Generatore di Descrizioni Prodotto")
st.markdown("Strumento per la creazione di testi universali standardizzati.")

# --- INPUT DATI ---
with st.container():
    nome_prodotto = st.text_input("📦 NOME PRODOTTO", placeholder="Inserisci il nome commerciale...")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Contesto e Dettagli")
        macro = st.text_area("1. MACRO (Funzione principale)", help="Cosa fa il prodotto in generale?")
        particolare = st.text_area("2. PARTICOLARE (Specifiche uniche)", help="Dettagli tecnici, materiali o finiture.")
    
    with col2:
        st.subheader("Logistica e Fitting")
        dimensioni = st.text_input("3. DIMENSIONI", placeholder="es. 100x50x20 cm / 5kg")
        extra = st.text_area("4. EXTRA", placeholder="Garanzie, certificazioni, accessori inclusi...")
        compatibilita = st.text_area("5. COMPATIBILITÀ", placeholder="Modelli supportati, sistemi operativi o attacchi.")

st.divider()

# --- LOGICA DI GENERAZIONE ---
if st.button("🚀 GENERA DESCRIZIONE UNIVERSALE"):
    if not nome_prodotto:
        st.error("Inserisci il nome del prodotto per continuare.")
    else:
        # Costruzione del testo finale
        testo_formattato = f"""**SCHEDA PRODOTTO: {nome_prodotto.upper()}**

---
**1. MACRO**
{macro if macro else "Dato non inserito."}

**2. PARTICOLARE**
{particolare if particolare else "Dato non inserito."}

**3. DIMENSIONI**
• {dimensioni if dimensioni else "Vedi scheda tecnica."}

**4. EXTRA**
{extra if extra else "Nessuna nota aggiuntiva."}

**5. COMPATIBILITÀ**
• {compatibilita if compatibilita else "Universale o da verificare."}
"""

        # Visualizzazione Output
        st.subheader("✅ Risultato Generato")
        st.text_area("Copia il testo da qui:", value=testo_formattato, height=450)
        
        # Anteprima estetica
        with st.expander("👁️ Anteprima Formattata"):
            st.markdown(testo_formattato)

# --- PIÈ DI PAGINA ---
st.sidebar.info("Modifica i campi e clicca su Genera. Il testo è ottimizzato per essere incollato su cataloghi, siti web o preventivi.")
