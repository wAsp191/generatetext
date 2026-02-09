import streamlit as st
from deep_translator import GoogleTranslator

# Configurazione Pagina
st.set_page_config(page_title="Technical Generator v6.0", layout="wide")

# =========================================================
# DATABASE ESTRATTO INTEGRALMENTE DAL FILE EXCEL
# =========================================================
DATABASE = {
    "1. Sheet Metal": {
        "macro_en": "SHEET METAL",
        "Particolari": {
            "Montante": ["UPRIGHT", {
                "70x30": "70X30", "90x30": "90X30", "Monoasolato": "WITH SLOTS ON ONE SIDE",
                "Biasolato": "WITH SLOTS ON TWO SIDE", "Con rinforzo": "WITH REINFORCEMENT", 
                "Estensione": "EXTENSION", "Minirack": "MINIRACK"
            }, "UPRIGHT"],
            "Piede di base": ["BASE FOOT", {
                "H90": "H90", "H100": "H100", "H150": "H150", 
                "Con piedino regolabile": "WITH ADJUSTABLE FOOT", "Estensione": "EXTENSION"
            }, "FOOT"],
            "Zoccolatura": ["PLINTH", {
                "H90": "H90", "H100": "H100", "H150": "H150", "Liscia": "PLAIN", 
                "Angolo aperto": "EXTERNAL CORNER", "Angolo chiuso": "INNER CORNER", 
                "Inclinata": "INCLINATED", "Forata": "PERFORATED", "Stondata": "ROUNDED"
            }, "PLINTH"],
            "Pannello rivestimento": ["BACK PANEL", {
                "Scantonato": "NOTCHED", "Forato euro": "EURO PERFORATED", "Forato a rombo": "RUMBLE PERFORATED",
                "Forato asolato": "SLOTTED PERFORATED", "Multilame": "MULTISTRIP", "Multibarra": "MULTIBAR",
                "Con foro passacavi": "WITH CABLE-COVER HOLE", "Con 1 foro WLD": "WITH 1 WLD'S HOLE", "Con 2 fori WLD": "WITH 2 WLD'S HOLES"
            }, "PANEL"],
            "Copripiede": ["FOOT COVER", {
                "H90": "WITH H90 FOOT", "H100": "WITH H100 FOOT", "H150": "WITH H150 FOOT"
            }, "COVER"],
            "Chiusura": ["TOP COVER", {"Con scasso": "WITH RECESS"}, "COVER"],
            "Fiancata laterale": ["SIDE PANEL", {
                "Portante": "LOAD-BEARING", "Non portante": "NON LOAD-BEARING", 
                "H90": "H90", "H100": "H100"
            }, "PANEL"],
            "Mensola": ["BRACKET", {
                "H30": "H30", "H20": "H20", "Slim": "SLIM VERSION", 
                "Sinistra": "LEFT", "Destra": "RIGHT", "Rinforzata": "REINFORCED"
            }, "BRACKET"],
            "Coprifessura": ["JOINT COVER", {"Standard": "STANDARD", "A scatto": "SNAP-ON"}, "ACCESSORY"],
            "Ripiano": ["SHELF", {
                "H30": "H30", "H20": "H20", "Liscio": "PLAIN",
                "Forato": "PERFORATED", "Con rinforzo": "WITH REINFORCEMENT"
            }, "SHELF"],
            "Cesto in filo": ["WIRE BASKET", {}, "BASKET"],
            "Cielino": ["CANOPY", {}, "CANOPY"],
            "Corrente": ["BEAM", {"Rinforzato": "REINFORCED", "Senza ganci": "WITHOUT HOOKS"}, "BEAM"],
            "Diagonale": ["DIAGONAL", {}, "BRACING"],
            "Distanziali": ["SPACER", {}, "ACCESSORY"],
            "Divisori": ["DIVIDER", {}, "DIVIDER"],
            "Ganci": ["HOOK", {}, "ACCESSORY"],
            "Pannello di rivestimento centrale": ["CENTRAL PANEL", {}, "PANEL"],
            "Profilo": ["PROFILE", {}, "PROFILE"],
            "Rinforzo": ["STIFFENER", {}, "STIFFENER"],
            "Staffa": ["PLATE", {}, "PLATE"],
            "Ante scorrevoli": ["SLIDING DOOR", {}, "DOOR"]
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
            "Telaio saldato": ["WELDED FRAME", {"Saldatura robot": "ROBOTIC WELDING"}, "WELDED"],
            "Componente saldato": ["WELDED COMPONENT", {}, "WELDED"]
        }
    }
}

OPZIONI_COMPATIBILITA = ["F25", "F25 BESPOKE", "F50", "F50 BESPOKE", "UNIVERSAL", "FORTISSIMO"]
EXTRA_COMUNI = {"Certificato CE": "CE CERTIFIED", "Ignifugo": "FIRE RETARDANT"}
OPZIONI_SPESSORE = ["", "5/10", "6/10", "8/10", "10/10", "12/10", "15/10", "20/10", "25/10", "30/10", "35/10", "40/10", "45/10", "50/10"]
OPZIONI_MATERIALE = ["IRON", "GALVANIZED", "INOX", "ALUMINIUM"]

# =========================================================
# FUNZIONI
# =========================================================
def reset_all():
    st.session_state["dim_l"] = ""
    st.session_state["dim_p"] = ""
    st.session_state["dim_h"] = ""
    st.session_state["dim_s"] = ""
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
    # MATERIALE (PRIMA DEL PARTICOLARE)
    st.subheader("🛠️ 2. Materiale e Particolare")
    mat_selezionato = st.radio("Seleziona Materiale:", options=OPZIONI_MATERIALE, horizontal=True)
    
    st.write("") # Spaziatore
    
    part_dict = DATABASE[macro_it]["Particolari"]
    nomi_it_ordinati = sorted(list(part_dict.keys()))
    scelta_part_it = st.radio("Seleziona dettaglio:", options=nomi_it_ordinati, horizontal=True)
    
    part_en = part_dict[scelta_part_it][0]
    extra_dedicati_dict = part_dict[scelta_part_it][1]
    tag_suggerimento = part_dict[scelta_part_it][2]

    st.markdown("---")
    
    # EXTRA (PUNTO 3)
    st.subheader(f"✨ 3. Extra per {scelta_part_it}")
    col_ex1, col_ex2 = st.columns([2, 1])
    with col_ex1:
        opzioni_extra_visibili = {**EXTRA_COMUNI, **extra_dedicati_dict}
        extra_selezionati = st.multiselect("Opzioni:", options=list(opzioni_extra_visibili.keys()), key="extra_tags")
    with col_ex2:
        extra_libero = st.text_input("Note libere (IT):", key="extra_text").strip()

    # DIMENSIONI (PUNTO 4)
    st.subheader("📏 4. Dimensioni (mm)")
    c1, c2, c3, c4 = st.columns(4)
    with c1: dim_l = st.text_input("Lunghezza", key="dim_l")
    with c2: dim_p = st.text_input("Profondità", key="dim_p")
    with c3: dim_h = st.text_input("Altezza", key="dim_h")
    with c4: dim_s = st.selectbox("Spessore", options=OPZIONI_SPESSORE, key="dim_s")

    # COMPATIBILITÀ (PUNTO 5)
    st.subheader("🔗 5. Compatibilità")
    comp_selezionate = st.multiselect("Modelli:", options=OPZIONI_COMPATIBILITA, key="comp_tags")

# =========================================================
# GENERAZIONE STRINGA
# =========================================================
st.divider()

if st.button("🚀 GENERA STRINGA FINALE", use_container_width=True):
    # Gestione Dimensioni: unisce con X solo i campi compilati
    dims_list = [d.strip().upper() for d in [dim_l, dim_p, dim_h, dim_s] if d.strip()]
    dim_final = "X".join(dims_list) if dims_list else ""
    
    # Elaborazione Extra
    extra_final_list = [opzioni_extra_visibili[ex] for ex in extra_selezionati]
    if extra_libero:
        try:
            extra_tradotto = GoogleTranslator(source='it', target='en').translate(extra_libero).upper()
            extra_final_list.append(extra_tradotto)
        except:
            extra_final_list.append(extra_libero.upper())
    
    extra_str = ", ".join(extra_final_list) if extra_final_list else "NONE"
    comp_str = ", ".join(comp_selezionate) if comp_selezionate else "UNIVERSAL"
    
    # FORMATO: MACRO - MATERIALE PARTICOLARE DIMENSIONI, EXTRA - COMPATIBILITÀ
    # Inseriamo il materiale prima del nome del particolare
    descrizione_centrale = f"{mat_selezionato} {part_en} {dim_final}".strip()
    res = f"{macro_en} - {descrizione_centrale}, {extra_str} - {comp_str}".upper()

    st.success("Stringa tecnica generata!")
    st.code(res, language=None)

    # Suggerimenti Tag (inclusa compatibilità)
    st.markdown("### 💡 Suggerimenti per la classificazione")
    all_tags = [tag_suggerimento.upper()] + [c.upper() for c in comp_selezionate]
    st.info(f"**TAGS:** {' | '.join(all_tags)}")

st.markdown("<style>.stRadio > div { flex-wrap: wrap; display: flex; gap: 10px; }</style>", unsafe_allow_html=True)
