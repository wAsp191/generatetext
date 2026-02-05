import streamlit as st

st.set_page_config(page_title="Generatore Descrizioni", layout="centered")

st.title("✍️ Generatore di Descrizioni Universali")
st.subheader("Configura le caratteristiche del prodotto")

# --- INPUT COLLABORATORE ---
col1, col2 = st.columns(2)

with col1:
    prodotto = st.text_input("Nome Prodotto", placeholder="es. Tavolo Wood")
    materiale = st.selectbox("Materiale", ["Legno Massiccio", "Acciaio Inox", "Plastica Riciclata", "Vetro Temprato"])
    stile = st.radio("Stile", ["Moderno", "Classico", "Minimalista", "Industriale"])

with col2:
    target = st.select_slider("Tono di voce", options=["Tecnico", "Formale", "Emozionale"])
    uso = st.multiselect("Destinazione d'uso", ["Interno", "Esterno", "Ufficio", "Residenziale"])

# --- LOGICA DI GENERAZIONE ---
def genera_descrizione(nome, mat, stl, tg, us):
    # Esempio di blocchi di testo dinamici
    intro = f"Il nostro {nome} rappresenta l'eccellenza del design {stl.lower()}."
    corpo = f"Realizzato interamente in {mat}, è progettato per durare nel tempo."
    
    if tg == "Emozionale":
        conclusione = f"Perfetto per chi cerca un tocco unico nei propri ambienti di tipo {', '.join(us).lower()}."
    elif tg == "Tecnico":
        conclusione = f"Specifiche ottimizzate per installazioni in ambito {', '.join(us).lower()}."
    else:
        conclusione = f"Una soluzione versatile per contesti {', '.join(us).lower()}."

    return f"{intro} {corpo} {conclusione}"

# --- OUTPUT ---
st.divider()

if st.button("Genera Descrizione Universale"):
    if prodotto:
        risultato = genera_descrizione(prodotto, materiale, stile, target, uso)
        st.success("Descrizione Generata!")
        st.text_area("Copia il testo:", risultato, height=150)
        st.button("📋 Copia negli appunti (simulato)")
    else:
        st.error("Per favore, inserisci almeno il nome del prodotto.")
