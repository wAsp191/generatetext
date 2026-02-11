import streamlit as st
from deep_translator import GoogleTranslator

# =========================================================
# CONFIGURAZIONE PAGINA
# =========================================================
st.set_page_config(page_title="Technical Generator v7.7", layout="wide")

# CSS Minimo solo per l'estetica del layout (no colori widget)
st.markdown("""
    <style>
        .block-container { padding-top: 1rem !important; }
        div[data-testid="stVerticalBlock"] > div { margin-bottom: -5px !important; }
        .stRadio > div { flex-wrap: wrap; display: flex; gap: 10px; }
        header, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# DATABASE E CONFIGURAZIONI
# =========================================================
MATERIALI_CONFIG = {
    "METAL COMP": {"FERRO": "IRON", "ZINCATO": "GALVANIZED", "INOX": "STAINLESS STEEL", "ALLUMINIO": "ALUMINIUM"},
    "WOOD COMP": {"LAMINATO": "LAMINATED", "NOBILITATO": "MELAMINE", "TRUCIOLARE": "OSB"},
    "PLASTIC COMP": {"POLICARBONATO": "POLYCARBONATE", "PVC": "PVC", "GOMMA": "RUBBER"},
    "GLASS COMP": {"VETRO TEMPRATO": "TEMPERED GLASS", "VETRO SATINATO": "SATIN GLASS"},
    "FASTENER": {"ZINCATO": "GALVANIZED", "BRUNITO": "BURNISHED", "NERO": "BLACK"},
    "ASSEMBLY": {"MONTATO": "ASSEMBLED", "NON MONTATO": "NOT-ASSEMBLED"}
}

DATABASE = {
    "METAL COMP": {
        "Particolari": {
            "Piede di base": ["BASE FOOT", {"H90": "H90", "H100": "H100", "H150": "H150", "Con piedino regolabile": "WITH ADJUSTABLE FOOT", "Estensione": "-EXTENSION", "Innesto montante": "UPRIGHT GRAFT"}, "FOOT"],
            "Zoccolatura": ["PLINTH", {"H90": "FOR H90 BASE FOOT", "H100": "FOR BASE FOOT H100", "H150": "FOR BASE FOOT H150", "Liscia": "PLAIN", "Angolo aperto": "EXTERNAL CORNER", "Angolo chiuso": "INNER CORNER", "Inclinata": "INCLINATED", "Forata": "PERFORATED", "Stondata": "ROUNDED", "Completa di paracolpo ABS": "WITH ABS BUFFER"}, "PLINTH"],
            "Pannello rivestimento": ["BACK PANEL", {"Scantonato": "NOTCHED", "Forato euro": "EURO PERFORATED", "Multibarra": "MULTIBAR", "Multilame": "MULTISTRIP", "In rete": "MESH", "Forato rombo": "RUMBLE PERFORATED", "Nervato": "RIBBED", "Attacco montante": "HOOK ONTO UPRIGHT"}, "PANEL"],
            "Copripiede": ["FOOT COVER", {"H90": "FOR H90 FOOT", "H100": "FOR H100 FOOT", "H150": "FOR H150 FOOT"}, "COVER"],
            "Chiusura": ["COVER", {"Superiore": "TOP", "Tra ripiani di base": "INTER-BASE SHELF", "Con scasso": "WITH RECESS"}, "COVER"],
            "Fiancata laterale": ["SIDE PANEL", {"Portante": "LOAD-BEARING", "Non portante": "NON LOAD-BEARING", "Stondata": "ROUNDED", "Trapezoidale": "SLOPING", "Sagomata": "SHAPED"}, "SIDE-PANEL"],
            "Mensola": ["BRACKET", {"SX": "LEFT", "DX": "RIGHT", "Rinforzata": "REINFORCED", "Nervata": "RIBBED", "Per ripiano in vetro": "FOR GLASS SHELF", "Per ripiano in legno": "FOR WOODEN SHELF", "A pinza": "GRIPPED", "Minirack": "MINIRACK"}, "BRACKET"],
            "Ripiano": ["SHELF", {"Liscio": "PLAIN", "Forato": "PERFORATED", "Stondato": "ROUNDED", "In filo": "WIRE", "Semicircolare": "SEMICIRCULAR", "Con rinforzo": "REINFORCED", "Con inserti filettati": "WITH RIVET"}, "SHELF"],
            "Cesto in filo": ["WIRE BASKET", {"Per attacco montante": "FOR UPRIGHT", "Impilabile": "STACKABLE"}, "BASKET"],
            "Cielino": ["CANOPY", {"Dritto": "STRAIGHT", "Inclinato": "SLOPING", "Stondato": "CURVED", "Con illuminazione": "WITH LIGHTING"}, "CANOPY"],
            "Ganci": ["HOOK", {"Singolo": "SINGLE", "Doppio": "DOUBLE", "Attacco barra": "HOOK FOR BAR", "Attacco pannello forato": "HOOK FOR SLOTTED PANEL"}, "HOOK"],
            "Profilo": ["PROFILE", {"Profilo a L": "L-SHAPED", "Profilo a U": "U-SHAPED"}, "PROFILE"],
            "Ante": ["SHEET METAL DOOR", {"Scorrevoli": "SLIDING", "Con foro serratura": "WITH LOCK HOLE"}, "DOOR"],
            "Piastra di fissaggio": ["FIXING PLATE", {"Con viti": "COMPLETE WITH SCREW"}, "PLATE"],
            "Cassetto estraibile": ["PULL-OUT DRAWER", {"Su ruote": "ON WHEELS", "Con serratura": "WITH LOCK"}, "DRAWER"],
            "Divisorio": ["DIVIDER", {"In filo": "WIRE", "Trapezoidale": "SLOPING"}, "DIVIDER"],
            "Frontalino": ["RISER", {"In filo": "WIRE", "Cromato": "CHROMED", "Verniciato": "PAINTED"}, "RISER"],
            "Spalla": ["FRAME", {"L100 Z/M": "L100 Z/M", "L100 Z/S": "L100 Z/S", "L120 Z/M": "L120 Z/M", "L120 Z/S": "L120 Z/S", "ZINCATO": "GALVANIZED"}, "FRAME"],
        }
    },
    "WOOD COMP": {
        "Particolari": {
            "Ripiano Legno": ["WOODEN SHELF", {"Con mensole": "WITH BRACKET", "Con lati bordati": "WITH EDGED SIDES", "Fresata": "MILLING"}, "SHELF"],
            "Schienale Legno": ["WOODEN BACK", {"Con mensole": "WITH BRACKET", "Con lati bordati": "WITH EDGED SIDES"}, "PANEL"],
            "Cielino": ["WOODEN CANOPY", {"Dritto": "STRAIGHT", "Inclinato": "SLOPING", "Con illuminazione": "WITH LIGHTING"}, "CANOPY"],
            "Zoccolatura": ["WOODEN PLINTH", {"H100": "H100", "H150": "H150", "Con lati bordati": "WITH EDGED SIDES"}, "PLINTH"],
            "Fiancata": ["WOODEN SIDE PANEL", {"Sagomata": "SHAPED", "Fresata": "MILLING"}, "SIDE PANEL"],
        }
    },
    "FASTENER": {
        "Particolari": {
            "Vite": ["SCREW", {"Autoperforanti": "SELF-DRILLING", "Testa svasata": "COUNTERSUCK HEAD", "Testa esagonale": "HEX HEAD"}, "FASTENER"],
            "Bullone": ["BOLT", {}, "FASTENER"],
            "Rondella": ["WASHER", {"Dentellata": "SERRATED LOCK"}, "FASTENER"],
            "Dado": ["NUT", {}, "FASTENER"],
        }
    }
}

OPZIONI_COMPATIBILITA = ["F25", "F25 BESPOKE", "F50", "F50 BESPOKE", "UNIVERSAL", "FORTISSIMO"]
TERMINI_ANTICIPATI = ["CENTRAL", "LEFT", "RIGHT", "REINFORCED", "INTERNAL", "EXTERNAL", "UPPER", "LOWER", "TOP", "ROUNDED", "SLOPING", "SHAPED", "WIRE", "CHROMED", "PAINTED", "SLIDING", "CURVED", "STRAIGHT", "SINGLE", "DOUBLE", "L-SHAPED", "U-SHAPED"]

# =========================================================
# LOGICA AZZERA
# =========================================================
def reset_all():
    for k in ["dim_l", "dim_p", "dim_h", "dim_s", "dim_dia", "extra_text", "extra_tags", "comp_tags"]:
        if k in st.session_state: st.session_state[k] = [] if "tags" in k else ""

# =========================================================
# UI PRINCIPALE
# =========================================================
st.title("⚙️ Technical Generator")

col_t, col_btn = st.columns([4, 1])
with col_btn: st.button("🔄 AZZERA TUTTO", on_click=reset_all, use_container_width=True)

st.divider()
col_macro, col_workarea = st.columns([1, 3], gap="large")

with col_macro:
    st.subheader("📂 1. Categoria")
    macro_it = st.radio("Seleziona categoria:", options=list(DATABASE.keys()))
    
    if macro_it != "FASTENER":
        st.markdown("---")
        st.subheader("🔗 Compatibilità")
        comp_selezionate = st.pills("Modelli:", options=OPZIONI_COMPATIBILITA, selection_mode="multi", key="comp_tags")
    else: comp_selezionate = []

with col_workarea:
    st.subheader("🛠️ 2. Dettagli")
    materiali = MATERIALI_CONFIG.get(macro_it, {})
    mat_en = ""
    if materiali:
        mat_it = st.radio("Materiale:", options=list(materiali.keys()), horizontal=True)
        mat_en = materiali[mat_it]
    
    part_dict = DATABASE[macro_it]["Particolari"]
    scelta_part_it = st.radio("Elemento:", options=sorted(list(part_dict.keys())), horizontal=True)
    part_en, extra_dict, tag_sugg = part_dict[scelta_part_it]

    st.markdown("---")
    st.subheader("✨ 3. Opzioni Extra")
    extra_selezionati = st.pills("Extra:", options=list(extra_dict.keys()), selection_mode="multi", key="extra_tags")
    extra_libero = st.text_input("Note libere (IT):", key="extra_text")

    st.subheader("📏 4. Dimensioni")
    if macro_it == "FASTENER":
        c1, c2 = st.columns(2)
        with c1: dim_l = st.text_input("Lunghezza (L)", key="dim_l")
        with c2: dim_dia = st.text_input("Diametro (D)", key="dim_dia")
        dim_p, dim_h, dim_s = "", "", ""
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1: dim_l = st.text_input("L", key="dim_l")
        with c2: dim_p = st.text_input("P", key="dim_p")
        with c3: dim_h = st.text_input("H", key="dim_h")
        with c4: dim_s = st.text_input("S", key="dim_s")
        dim_dia = ""

# =========================================================
# GENERAZIONE
# =========================================================
st.divider()
if 'stringa_editabile' not in st.session_state: st.session_state['stringa_editabile'] = ""

if st.button("🚀 GENERA STRINGA", use_container_width=True):
    # Dimensioni
    parts = []
    if macro_it == "FASTENER":
        if dim_dia: parts.append(f"{'D' if not dim_dia.upper().startswith('M') else ''}{dim_dia.upper()}")
        if dim_l: parts.append(f"L{dim_l.upper()}")
    else:
        if dim_l: parts.append(f"L{dim_l.upper()}")
        if dim_p: parts.append(f"P{dim_p.upper()}")
        if dim_h: parts.append(f"H{dim_h.upper()}")
    
    dim_str = "X".join(parts)
    if not macro_it == "FASTENER" and dim_s: dim_str += f" S{dim_s.upper()}"

    # Traduzione extra
    extra_en = [extra_dict[ex] for ex in extra_selezionati]
    if extra_libero:
        try: extra_en.append(GoogleTranslator(source='it', target='en').translate(extra_libero).upper())
        except: extra_en.append(extra_libero.upper())

    pref = [e for e in extra_en if e in TERMINI_ANTICIPATI]
    suff = [e for e in extra_en if e not in TERMINI_ANTICIPATI]
    
    desc = f"{mat_en} {' '.join(pref)} {part_en} {dim_str}".strip().replace("  ", " ")
    res = [desc.upper()]
    if suff: res.append(", ".join(suff).upper())
    if comp_selezionate: res.append(", ".join(comp_selezionate))
    
    st.session_state['stringa_editabile'] = " - ".join(res)

if st.session_state['stringa_editabile']:
    st.code(st.session_state['stringa_editabile'])
    st.text_input("Modifica manuale:", key='stringa_editabile')
    st.info(f"Tag: {tag_sugg.upper()}")
