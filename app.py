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
            "Alesatura": "BORING", "Calandratura": "ROLLING", "Piegatura CNC": "CNC BENDING",
            "Punzonatura": "PUNCHING", "Satinatura": "SATIN FINISH", "Saldatura TIG": "TIG WELDING",
            "Taglio Laser": "LASER CUT", "Zincatura a caldo": "HOT-DIP GALVANIZED"
        }
    },
    "2. Plastic Comp": {
        "macro_en": "PLASTIC COMPONENT",
        "Particolari": {
            "Estruso": "EXTRUDED", "Finitura opaca": "MATTE FINISH", "Polimero rinforzato": "REINFORCED POLYMER",
            "Resistente UV": "UV RESISTANT", "Stampaggio a iniezione": "INJECTION MOLDED", "Termoformato": "THERMOFORMED"
        }
    },
    "3. Glass Comp": {
        "macro_en": "GLASS COMPONENT",
        "Particolari": {
            "Bordo filo lucido": "POLISHED EDGE", "Colorazione in pasta": "COLORED GLASS",
            "Finitura acidata": "ACID-ETCHED FINISH", "Vetro Satinato": "SATIN GLASS",
            "Vetro stratificato": "LAMINATED GLASS", "Vetro temprato": "TEMPERED GLASS"
        }
    },
    "4. Wood Comp": {
        "macro_en": "WOOD COMPONENT",
        "Particolari": {
            "Abete": "FIR WOOD", "Finitura naturale": "NATURAL FINISH", "Legno di Rovere": "OAK WOOD",
            "Multistrato": "PLYWOOD", "Noce Canaletto": "WALNUT WOOD", "Verniciatura opaca": "MATTE PAINTING"
        }
    },
    "5. Electric Comp": {
        "macro_en": "ELECTRIC COMPONENT",
        "Particolari": {
            "Alimentatore": "POWER SUPPLY", "Cablaggio standard": "STANDARD WIRING",
            "Grado IP65": "IP65 RATING", "Interruttore": "SWITCH", "Modulo LED": "LED MODULE",
            "Protezione termica": "THERMAL PROTECTION"
        }
    },
    "6. Fastener": {
        "macro_en": "FASTENER",
        "Particolari": {
            "Acciaio Inox A2": "STAINLESS STEEL A2", "Acciaio zincato": "ZINC PLATED STEEL",
            "Bullone": "BOLT", "Classe 8.8": "8.8 GRADE", "Dado": "NUT", "Filettatura metrica": "METRIC THREAD"
        }
    },
    "7. Other": {
        "macro_en": "OTHER",
        "Particolari": {
            "Accessorio": "ACCESSORY", "Materiale misto": "MIXED MATERIAL", "Specifica custom": "CUSTOM SPECIFICATION"
        }
    }
}

OPZIONI_COMPATIBILITA = ["F25", "F25 BESPOKE", "F50", "F50 BESPOKE", "UNIVERSAL", "FORTISSIMO"]
EXTRA_FISSI = {"Certificato CE": "CE CERTIFIED", "Ignifugo": "FIRE RETARDANT", "Idrorepellente": "WATER REPELLENT", "Lotto Minimo": "MOQ APPLIED"}

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

# Bottone Reset in alto a destra
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
    # 2. PARTICOLARE
    st.subheader("🔍 2. Particolare")
    part_dict = DATABASE[macro_it]["Particolari"]
    nomi_it_ordinati = sorted(list(part_dict.keys()))
    scelta_part_it = st.radio("Seleziona dettaglio tecnico:", options=nomi_it_ordinati, horizontal=True)
    part_en = part_dict[scelta_part_it]

    st.markdown("---")
    
    # 3. DIMENSIONI (Input manuale)
    st.subheader("📏 3. Dimensioni")
    dim_input = st.text_input("Inserisci misure (es. 500X200 MM):", key="dim_val").strip().upper()

    # 4. EXTRA (Multiselezione esplosa + Testo)
    st.subheader("✨ 4. Extra")
    col_ex1, col_ex2 = st.columns([2, 1])
    with col_ex1:
        extra_selezionati = st.multiselect("Seleziona opzioni extra (anche multiple):", 
                                           options=list(EXTRA_FISSI.keys()), key="extra_tags")
    with col_ex2:
        extra_libero = st.text_input("Note aggiuntive (IT):", key="extra_text").strip()

    # 5. COMPATIBILITÀ (Multiselezione esplosa)
    st.subheader("🔗 5. Compatibilità")
    comp_selezionate = st.multiselect("Seleziona compatibilità (anche multiple):", 
                                      options=OPZIONI_COMPATIBILITA, key="comp_tags")

# =========================================================
# GENERAZIONE RISULTATO
# =========================================================
st.divider()

if st.button("🚀 GENERA STRINGA FINALE", use_container_width=True):
    # Traduzione e unione Extra
    extra_final_list = [EXTRA_FISSI[ex] for ex in extra_selezionati]
    if extra_libero:
        try:
            extra_tradotto = GoogleTranslator(source='it', target='en').translate(extra_libero).upper()
            extra_final_list.append(extra_tradotto)
        except:
            extra_final_list.append(extra_libero.upper())
    
    extra_str = ", ".join(extra_final_list) if extra_final_list else "NONE"
    
    # Unione Compatibilità
    comp_str = ", ".join(comp_selezionate) if comp_selezionate else "UNIVERSAL"
    
    dim_final = dim_input if dim_input else "N/A"
    
    # COSTRUZIONE: MACRO - PARTICOLARE - DIMENSIONI - EXTRA - COMPATIBILITÀ
    res = f"{macro_en} - {part_en} - {dim_final} - {extra_str} - {comp_str}"
    res = res.upper()

    st.success("Stringa tecnica generata!")
    st.code(res, language=None)
    st.text_area("Copia rapida:", value=res, height=70)

# CSS per layout orizzontale e stile
st.markdown("""
<style>
    .stMultiSelect div div { background-color: #f0f2f6; }
    .stRadio > div { flex-wrap: wrap; display: flex; gap: 10px; }
</style>
""", unsafe_allow_html=True)
