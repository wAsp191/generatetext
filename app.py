import streamlit as st
from deep_translator import GoogleTranslator

# Configurazione Pagina
st.set_page_config(page_title="Technical Description Generator v3.0", layout="wide")

# =========================================================
# DATABASE AGGIORNATO DAL FILE EXCEL
# =========================================================
DATABASE = {
    "1. Sheet Metal": {
        "macro_en": "SHEET METAL",
        "Particolari": {
            "Ante scorrevoli": ["SLIDING DOOR", {}, "DOOR"],
            "Cesto in filo": ["WIRE BASKET", {}, "BASKET"],
            "Chiusura": ["TOP COVER", {"Con scasso": "WITH RECESS"}, "COVER"],
            "Cielino": ["CANOPY", {}, "CANOPY"],
            "Coprifessura": ["JOINT COVER", {"Standard": "STANDARD", "A scatto": "SNAP-ON"}, "ACCESSORY"],
            "Copripiede": ["FOOT COVER", {"H90": "WITH H90 FOOT", "H100": "WITH H100 FOOT", "H150": "WITH H150 FOOT"}, "COVER"],
            "Corrente": ["BEAM", {"Rinforzato": "REINFORCED", "Senza ganci": "WITHOUT HOOKS"}, "BEAM"],
            "Diagonale": ["DIAGONAL", {}, "BRACING"],
            "Distanziali": ["SPACER", {}, "ACCESSORY"],
            "Divisori": ["DIVIDER", {}, "DIVIDER"],
            "Fiancata laterale": ["SIDE PANEL", {"Portante": "LOAD-BEARING", "Non portante": "NON LOAD-BEARING", "H90": "H90", "H100": "H100"}, "PANEL"],
            "Ganci": ["HOOK", {}, "ACCESSORY"],
            "Mensola": ["BRACKET", {}, "BRACKET"],
            "Montante": ["UPRIGHT", {
                "70x30": "70X30", "90x30": "90X30", "Monoasolato": "WITH SLOTS ON ONE SIDE",
                "Biasolato": "WITH SLOTS ON TWO SIDE", "Con rinforzo": "WITH REINFORCEMENT", "Estensione": "EXTENSION", "Minirack": "MINIRACK"
            }, "UPRIGHT"],
            "Pannello rivestimento": ["BACK PANEL", {
                "Scantonato": "NOTCHED", "Forato euro": "EURO PERFORATED", "Forato a rombo": "RUMBLE PERFORATED",
                "Forato asolato": "SLOTTED PERFORATED", "Multilame": "MULTISTRIP", "Multibarra": "MULTIBAR",
                "Con foro passacavi": "WITH CABLE-COVER HOLE", "Con 1 foro WLD": "WITH 1 WLD'S HOLE", "Con 2 fori WLD": "WITH 2 WLD'S HOLES"
            }, "PANEL"],
            "Pannello di rivestimento centrale": ["CENTRAL PANEL", {}, "PANEL"],
            "Piede di base": ["BASE FOOT", {
                "H90": "H90", "H100": "H100", "H150": "H150", 
                "Con piedino regolabile": "WITH ADJUSTABLE FOOT", "Estensione": "EXTENSION"
            }, "FOOT"],
            "Profilo": ["PROFILE", {}, "PROFILE"],
            "Rinforzo": ["STIFFENER", {}, "STIFFENER"],
            "Ripiano": ["SHELF", {
                "H30": "H30", "H20": "H20", "Liscio": "PLAIN",
                "Forato": "PERFORATED", "Con rinforzo": "WITH REINFORCEMENT"
            }, "SHELF"],
            "Staffa": ["PLATE", {}, "PLATE"],
            "Zoccolatura": ["PLINTH", {
                "H90": "H90", "H100": "H100", "H150": "H150", "Liscia": "PLAIN", 
                "Angolo aperto": "EXTERNAL CORNER", "Angolo chiuso": "INNER CORNER", 
                "Inclinata": "INCLINATED", "Forata": "PERFORATED", "Stondata": "ROUNDED"
            }, "PLINTH"]
        }
    },
    "2. Assembly": {
        "macro_en": "ASSEMBLY",
        "Particolari": {
            "Assieme Mobile": ["CABINET ASSEMBLY", {"Pre-montato": "PRE-ASSEMBLED"}, "ASSEMBLY"],
            "Assieme generale": ["GENERAL ASSEMBLY", {}, "ASSEMBLY"]
        }
    },
    "3. Weldcomp": {
        "macro_en": "WELDCOMP",
        "Particolari": {
            "Componente saldato": ["WELDED COMPONENT", {}, "WELDED"],
            "Telaio saldato": ["WELDED FRAME", {"Saldatura robot": "ROBOTIC WELDING"}, "WELDED"]
        }
    },
    "4. Plastic Comp": { "macro_en": "PLASTIC COMPONENT", "Particolari": { "Plastica": ["PLASTIC PART", {}, "PLASTIC"] } },
    "5. Glass Comp": { "macro_en": "GLASS COMPONENT", "Particolari": { "Vetro": ["GLASS", {}, "GLASS"] } },
    "6. Wood Comp": { "macro_en": "WOOD COMPONENT", "Particolari": { "Legno": ["WOOD", {}, "WOOD"] } },
    "7. Fastener": { "macro_en": "FASTENER", "Particolari": { "Viti": ["SCREWS", {}, "FASTENER"] } }
}

OPZIONI_COMPATIBILITA = ["F25", "F25 BESPOKE", "F50", "F50 BESPOKE", "UNIVERSAL", "FORTISSIMO"]
EXTRA_COMUNI = {"Certificato CE": "CE CERTIFIED", "Ignifugo": "FIRE RETARDANT"}

# =========================================================
# FUNZIONI
# =========================================================
def reset_all():
    st.session_state["dim_val"] = ""
    st.session_state["extra_text"] = ""
    st.session_state["extra_tags"] = []
    st.session_state["comp_tags"] = []

# =========================================================
# INTERFACCIA
# =========================================================
st.title("⚙️ Technical Generator & Classification")

col_t, col_btn = st.columns([4, 1])
with col_btn:
    st.button("🔄 AZZERA TUTTO", on_click=reset_all, use_container_width=True)

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
    scelta_part_it = st.radio("Seleziona dettaglio:", options=nomi_it_ordinati, horizontal=True)
    
    part_en = part_dict[scelta_part_it][0]
    extra_dedicati_dict = part_dict[scelta_part_it][1]
    tag_suggerimento = part_dict[scelta_part_it][2]

    st.markdown("---")
    
    # 4. EXTRA (SPOSTATO PRIMA DELLE DIMENSIONI)
    st.subheader(f"✨ 3. Extra per {scelta_part_it}")
    col_ex1, col_ex2 = st.columns([2, 1])
    with col_ex1:
        opzioni_extra_visibili = {**EXTRA_COMUNI, **extra_dedicati_dict}
        extra_selezionati = st.multiselect("Opzioni:", options=list(opzioni_extra_visibili.keys()), key="extra_tags")
    with col_ex2:
        extra_libero = st.text_input("Note libere (Traduzione IT->EN):", key="extra_text").strip()

    # 3. DIMENSIONI
    st.subheader("📏 4. Dimensioni")
    dim_input = st.text_input("Misure (es. 1000X500):", key="dim_val").strip().upper()

    # 5. COMPATIBILITÀ
    st.subheader("🔗 5. Compatibilità")
    comp_selezionate = st.multiselect("Modelli:", options=OPZIONI_COMPATIBILITA, key="comp_tags")

# =========================================================
# GENERAZIONE
# =========================================================
st.divider()

if st.button("🚀 GENERA STRINGA FINALE", use_container_width=True):
    # Traduzione extra
    extra_final_list = [opzioni_extra_visibili[ex] for ex in extra_selezionati]
    if extra_libero:
        try:
            extra_tradotto = GoogleTranslator(source='it', target='en').translate(extra_libero).upper()
            extra_final_list.append(extra_tradotto)
        except:
            extra_final_list.append(extra_libero.upper())
    
    extra_str = ", ".join(extra_final_list) if extra_final_list else "NONE"
    comp_str = ", ".join(comp_selezionate) if comp_selezionate else "UNIVERSAL"
    dim_final = dim_input if dim_input else "N/A"
    
    # COSTRUZIONE STRINGA CON VIRGOLA (SOSTITUITO IL TRATTINO)
    # Formato: MACRO, PARTICOLARE, DIMENSIONI, EXTRA, COMPATIBILITÀ
    res = f"{macro_en}, {part_en}, {dim_final}, {extra_str}, {comp_str}".upper()

    st.success("Stringa tecnica generata correttamente!")
    st.code(res, language=None)

    st.markdown("### 💡 Suggerimento per la classificazione")
    st.info(f"**TAG SUGGERITI:** {tag_suggerimento.upper()}")

st.markdown("<style>.stRadio > div { flex-wrap: wrap; display: flex; gap: 10px; }</style>", unsafe_allow_html=True)
