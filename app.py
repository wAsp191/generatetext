import streamlit as st
from deep_translator import GoogleTranslator

# Configurazione Pagina
st.set_page_config(page_title="Technical Generator v7.1", layout="wide")

# =========================================================
# 1. CONFIGURAZIONE MATERIALI PER OGNI NUOVA MACRO
# =========================================================
MATERIALI_CONFIG = {
    "METAL COMP": {
        "FERRO": "IRON",
        "ZINCATO": "GALVANIZED",
        "INOX": "STAINLESS STEEL",
        "ALLUMINIO": "ALUMINIUM"
    },
    "WOOD COMP": {
        "LAMINATO": "LAMINATED",
        "NOBILITATO": "MELAMINE",
        "TRUCIOLARE": "OSB"
    },
    "PLASTIC COMP": {
        "POLICARBONATO": "POLYCARBONATE",
        "PVC": "PVC",
        "GOMMA": "RUBBER"
    },
    "GLASS COMP": {
        "VETRO TEMPRATO": "TEMPERED GLASS"
    },
    "FASTENER": {}, 
    "ASSEMBLY": {}
}

# =========================================================
# 2. DATABASE INTEGRALE (Tutte le voci del tuo file Excel)
# =========================================================
DATABASE = {
    "METAL COMP": {
        "macro_en": "METAL COMPONENT",
        "Particolari": {
            "Montante": ["UPRIGHT", {"70x30": "70X30", "90x30": "90X30", "Monoasolato": "WITH SLOTS ON ONE SIDE", "Biasolato": "WITH SLOTS ON TWO SIDE", "Con rinforzo": "WITH REINFORCEMENT", "Estensione": "EXTENSION", "Minirack": "MINIRACK"}, "UPRIGHT"],
            "Piede di base": ["BASE FOOT", {"H90": "H90", "H100": "H100", "H150": "H150", "Con piedino regolabile": "WITH ADJUSTABLE FOOT", "Estensione": "EXTENSION"}, "FOOT"],
            "Zoccolatura": ["PLINTH", {"H90": "FOR H90 BASE FOOT", "H100": "FOR BASE FOOT H100", "H150": "FOR BASE FOOT H150", "Liscia": "PLAIN", "Angolo aperto": "EXTERNAL CORNER", "Angolo chiuso": "INNER CORNER", "Inclinata": "INCLINATED", "Forata": "PERFORATED", "Stondata": "ROUNDED"}, "PLINTH"],
            "Pannello rivestimento": ["BACK PANEL", {"Scantonato": "NOTCHED", "Forato euro": "EURO PERFORATED", "Forato a rombo": "RUMBLE PERFORATED", "Forato asolato": "SLOTTED PERFORATED", "Multilame": "MULTISTRIP", "Multibarra": "MULTIBAR", "Con foro passacavi": "WITH CABLE-COVER HOLE", "Con 1 foro WLD": "WITH 1 WLD'S HOLE", "Con 2 fori WLD": "WITH 2 WLD'S HOLES"}, "PANEL"],
            "Copripiede": ["FOOT COVER", {"H90": "FOR H90 FOOT", "H100": "FOR H100 FOOT", "H150": "FOR H150 FOOT"}, "COVER"],
            "Chiusura": ["TOP COVER", {"Con scasso": "WITH RECESS"}, "COVER"],
            "Fiancata laterale": ["SIDE PANEL", {"Portante": "LOAD-BEARING", "Non portante": "NON LOAD-BEARING", "H90": "FOR BASE FOOT H90", "H100": "FOR BASE FOOT H100", "H150": "FOR BASE FOOT H150"}, "SIDE-PANEL"],
            "Mensola": ["BRACKET", {"SX": "LEFT", "DX": "RIGHT", "Rinforzata": "REINFORCED", "Nervata": "RIBBED", "1 Posizione": "1 POSITION", "2 Posizioni": "2 POSITIONS", "Attacco montante": "HOOKS ONTO UPRIGHT", "Attacco multibarra": "FOR MULTIBAR", "Attacco multilame": "FOR MUTISTRIP"}, "BRACKET"],
            "Ripiano": ["SHELF", {"Liscio": "PLAIN", "Forato": "PERFORATED", "Con rinforzo": "WITH REINFORCEMENT", "Con boccole": "WITH RIVET"}, "SHELF"],
            "Cesto in filo": ["WIRE BASKET", {}, "BASKET"],
            "Cielino": ["CANOPY", {}, "CANOPY"],
            "Corrente": ["BEAM", {"Rinforzato": "REINFORCED", "Senza ganci": "WITHOUT HOOKS"}, "BEAM"],
            "Diagonale": ["DIAGONAL", {"Forata": "PERFORETED"}, "DIAGONAL"],
            "Distanziali": ["SPACER", {}, "SPACER"],
            "Divisori": ["DIVIDER", {}, "DIVIDER"],
            "Ganci": ["HOOK", {}, "HOOK"],
            "Pannello di rivestimento centrale": ["CENTRAL PANEL", {}, "PANEL"],
            "Profilo": ["PROFILE", {}, "PROFILE"],
            "Rinforzo": ["STIFFENER", {}, "STIFFENER"],
            "Staffa": ["PLATE", {}, "PLATE"],
            "Ante scorrevoli": ["SLIDING DOOR", {}, "DOOR"]
        }
    },
    "WOOD COMP": {
        "macro_en": "WOOD COMPONENT",
        "Particolari": {
            "Ripiano Legno": ["WOODEN SHELF", {}, "SHELF"],
            "Schienale Legno": ["WOODEN BACK", {}, "PANEL"]
            "Cielino": "CANOPY"
        }
    },
    "PLASTIC COMP": {
        "macro_en": "PLASTIC COMPONENT",
        "Particolari": {
            "Tappo": ["PLASTIC CAP", {}, "CAP"],
            "Guarnizione": ["GASKET", {}, "ACCESSORY"]
        }
    },
    "GLASS COMP": {
        "macro_en": "GLASS COMPONENT",
        "Particolari": {
            "Ripiano": ["GLASS SHELF", {}, "SHELF"]
        }
    },
    "FASTENER": {
        "macro_en": "FASTENER",
        "Particolari": {
            "Vite": ["SCREW", {}, "FASTENER", "SCREW"],
            "Bullone": ["BOLT", {}, "FASTENER"]
            "Rondella": ["WASHER", {}, "FASTENER", "WASHER"]
            "Dado": ["NUT", {}, "FASTENER", "NUT"]
            "Inserti filettati": ["RIVET", {}, "FASTENER", "RIVET"]
            "Tasselli": ["ANCHOR", {}, "FASTENER", "ANCHOR"]
        }
    },
    "ASSEMBLY": {
        "macro_en": "ASSEMBLY",
        "Particolari": {
            "Assieme Mobile": ["CABINET ASSEMBLY", {"Pre-montato": "PRE-ASSEMBLED"}, "ASSEMBLY"],
            "Assieme generale": ["GENERAL ASSEMBLY", {}, "ASSEMBLY"]
        }
    }
}

OPZIONI_COMPATIBILITA = ["F25", "F25 BESPOKE", "F50", "F50 BESPOKE", "UNIVERSAL", "FORTISSIMO"]
EXTRA_COMUNI = {"Certificato CE": "CE CERTIFIED", "Ignifugo": "FIRE RETARDANT"}
OPZIONI_SPESSORE = ["", "5/10", "6/10", "8/10", "10/10", "12/10", "15/10", "20/10", "25/10", "30/10", "35/10", "40/10", "45/10", "50/10"]

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

with col_workarea:
    st.subheader("🛠️ 2. Materiale e Particolare")
    materiali_disponibili = MATERIALI_CONFIG.get(macro_it, {})
    
    mat_en = ""
    if materiali_disponibili:
        mat_it = st.radio(f"Seleziona Materiale per {macro_it}:", options=list(materiali_disponibili.keys()), horizontal=True)
        mat_en = materiali_disponibili[mat_it]
    
    st.write("") 
    
    part_dict = DATABASE[macro_it]["Particolari"]
    nomi_it_ordinati = sorted(list(part_dict.keys()))
    scelta_part_it = st.radio("Seleziona dettaglio:", options=nomi_it_ordinati, horizontal=True)
    
    part_en = part_dict[scelta_part_it][0]
    extra_dedicati_dict = part_dict[scelta_part_it][1]
    tag_suggerimento = part_dict[scelta_part_it][2]

    st.markdown("---")
    
    st.subheader(f"✨ 3. Extra per {scelta_part_it}")
    col_ex1, col_ex2 = st.columns([2, 1])
    with col_ex1:
        opzioni_extra_visibili = {**EXTRA_COMUNI, **extra_dedicati_dict}
        extra_selezionati = st.multiselect("Opzioni:", options=list(opzioni_extra_visibili.keys()), key="extra_tags")
    with col_ex2:
        extra_libero = st.text_input("Note libere (IT):", key="extra_text").strip()

    st.subheader("📏 4. Dimensioni (mm)")
    c1, c2, c3, c4 = st.columns(4)
    with c1: dim_l = st.text_input("Lunghezza", key="dim_l")
    with c2: dim_p = st.text_input("Profondità", key="dim_p")
    with c3: dim_h = st.text_input("Altezza", key="dim_h")
    with c4: dim_s = st.selectbox("Spessore", options=OPZIONI_SPESSORE, key="dim_s")

    st.subheader("🔗 5. Compatibilità")
    comp_selezionate = st.multiselect("Modelli:", options=OPZIONI_COMPATIBILITA, key="comp_tags")

# =========================================================
# GENERAZIONE STRINGA
# =========================================================
st.divider()

if st.button("🚀 GENERA STRINGA FINALE", use_container_width=True):
    # Logica Dimensioni modificata: L, P, H con X | Spessore con Spazio
    lph_list = [d.strip().upper() for d in [dim_l, dim_p, dim_h] if d.strip()]
    lph_str = "X".join(lph_list)
    
    s_val = dim_s.strip()
    
    # Costruzione stringa dimensioni finale
    if lph_str and s_val:
        dim_final = f"{lph_str} {s_val}"
    else:
        dim_final = lph_str if lph_str else s_val

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
    
    descrizione_centrale = f"{mat_en} {part_en} {dim_final}".strip().replace("  ", " ")
    res = f"{macro_it} - {descrizione_centrale}, {extra_str} - {comp_str}".upper()

    st.success("Stringa tecnica generata!")
    st.code(res, language=None)

    st.markdown("### 💡 Suggerimenti per la classificazione")
    all_tags = [tag_suggerimento.upper()] + [c.upper() for c in comp_selezionate]
    st.info(f"**TAGS:** {' | '.join(all_tags)}")

st.markdown("<style>.stRadio > div { flex-wrap: wrap; display: flex; gap: 10px; }</style>", unsafe_allow_html=True)
