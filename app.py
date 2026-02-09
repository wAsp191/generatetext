import streamlit as st
from deep_translator import GoogleTranslator

# Configurazione Pagina
st.set_page_config(page_title="Technical Description Generator", layout="wide")

# =========================================================
# DATABASE (Modifica qui per aggiungere/togliere)
# =========================================================
DATABASE = {
    "1. Sheet Metal": {
        "macro_en": "SHEET METAL",
        "Particolari": {
            "Pannello di rivestimento": "BACK PANEL",
            "Pannello di rivestimento centrale": "CENTRAL PANEL",
            "Corrente": "BEAM",
            "Montante": "UPRIGHT",
            "Ripiano": "SHELF",
            "Cesto in filo": "WIRE BASKET",
            "Mensola": "BRACKET",
            "Cielino": "CANOPY",
            "Chiusura": "TOP COVER",
            "Diagonale": "DIAGONAL",
            "Divisori": "DIVIDER",
            "Ante scorrevoli": "SLIDING DOOR",
            "Piede di base": "BASE FOOT",
            "Ganci": "HOOK",
            "Staffa": "PLATE",
            "Zoccolatura": "PLINTH",
            "Profilo": "PROFILE",
            "Distanziali": "SPACER",
            "Rinforzo": "STIFFENER"
        }
    },
    "2. Plastic Comp": {
        "macro_en": "PLASTIC COMPONENT",
        "Particolari": {
            "Esempio Plastica": "PLASTIC EXAMPLE"
        }
    },
    "3. Glass Comp": {
        "macro_en": "GLASS COMPONENT",
        "Particolari": {
            "Esempio Vetro": "GLASS EXAMPLE"
        }
    },
    "4. Wood Comp": {
        "macro_en": "WOOD COMPONENT",
        "Particolari": {
            "Esempio Legno": "WOOD EXAMPLE"
        }
    },
    "5. Electric Comp": {
        "macro_en": "ELECTRIC COMPONENT",
        "Particolari": {
            "Esempio Elettrico": "ELECTRIC EXAMPLE"
        }
    },
    "6. Fastener": {
        "macro_en": "FASTENER",
        "Particolari": {
            "Viti": "SCREWS",
            "Bulloni": "BOLTS"
        }
    },
    "7. Other": {
        "macro_en": "OTHER",
        "Particolari": {
            "Accessorio": "ACCESSORY"
        }
    }
}

OPZIONI_COMPATIBILITA = ["F25", "F25 BESPOKE", "F50", "F50 BESPOKE", "UNIVERSAL", "FORTISSIMO"]
EXTRA_FISSI = {"Certificato CE": "CE CERTIFIED", "Ignifugo": "FIRE RETARDANT", "Idrorepellente": "WATER REPELLENT"}

# =========================================================
# FUNZIONI DI SUPPORTO
# =========================================================
def reset_all():
    st.session_state["dim_val"] = ""
    st.session_state["extra_text"] = ""
    st.session_state["extra_tags"] = []
    st.session_state["comp_tags"] = []

# =========================================================
# LOGICA INTERFACCIA
# =========================================================

st.title("🛠️ Universal Description Generator")

# Bottone Reset
col_t, col_btn = st.columns([4, 1])
with col_btn:
    if st.button("🔄 AZZERA TUTTO", on_click=reset_all, use_container_width=True):
        st.rerun()

st.markdown("---")

col_macro, col_workarea = st.columns([1, 3], gap="large")

with col_macro:
    st.subheader("📂 1. Macro Categoria")
    macro_it = st.radio("Seleziona categoria:", options=list(DATABASE.keys()))
    macro_en = DATABASE[macro_it]["macro_en"]

with col_workarea:
    # 2. PARTICOLARE (Esploso orizzontale e alfabetico)
    st.subheader("🔍 2. Particolare")
    part_dict = DATABASE[macro_it]["Particolari"]
    nomi_it_ordinati = sorted(list(part_dict.keys()))
    scelta_part_it = st.radio("Seleziona dettaglio tecnico:", options=nomi_it_ordinati, horizontal=True)
    part_en = part_dict[scelta_part_it]

    st.markdown("---")
    
    # 3. DIMENSIONI
    st.subheader("📏 3. Dimensioni")
    dim_input = st.text_input("Inserisci misure (es. 500X200 MM):", key="dim_val").strip().upper()

    # 4. EXTRA
    st.subheader("✨ 4. Extra")
    col_ex1, col_ex2 = st.columns([2, 1])
    with col_ex1:
        extra_selezionati = st.multiselect("Seleziona opzioni extra predefinite:", options=list(EXTRA_FISSI.keys()), key="extra_tags")
    with col_ex2:
        extra_libero = st.text_input("Note aggiuntive (Traduzione Automatica):", key="extra_text").strip()

    # 5. COMPATIBILITÀ
    st.subheader("🔗 5. Compatibilità")
    comp_selezionate = st.multiselect("Seleziona modelli (Scelta multipla):", options=OPZIONI_COMPATIBILITA, key="comp_tags")

# =========================================================
# GENERAZIONE RISULTATO
# =========================================================
st.divider()

if st.button("🚀 GENERA STRINGA FINALE", use_container_width=True):
    # Traduzione e unione Extra
    extra_final_list = [EXTRA_FISSI[ex] for ex in extra_selezionati]
    if extra_libero:
        try:
            # Traduzione IT -> EN
            extra_tradotto = GoogleTranslator(source='it', target='en').translate(extra_libero).upper()
            extra_final_list.append(extra_tradotto)
        except:
            # Se la traduzione fallisce (es. no internet), usa il testo originale in maiuscolo
            extra_final_list.append(extra_libero.upper())
    
    extra_str = ", ".join(extra_final_list) if extra_final_list else "NONE"
    
    # Unione Compatibilità
    comp_str = ", ".join(comp_selezionate) if comp_selezionate else "UNIVERSAL"
    
    # Gestione Dimensioni vuote
    dim_final = dim_input if dim_input else "N/A"
    
    # COSTRUZIONE FINALE: MACRO - PARTICOLARE - DIMENSIONI - EXTRA - COMPATIBILITÀ
    res = f"{macro_en} - {part_en} - {dim_final} - {extra_str} - {comp_str}"
    res = res.upper()

    st.success("Stringa tecnica generata!")
    st.code(res, language=None)
    st.text_area("Copia rapida:", value=res, height=70)

# CSS per layout orizzontale e responsive
st.markdown("""
<style>
    .stRadio > div { flex-wrap: wrap; display: flex; gap: 10px; }
</style>
""", unsafe_allow_html=True)
