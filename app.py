import streamlit as st
from deep_translator import GoogleTranslator
import datetime

# =========================================================
# 0. CONFIGURAZIONE E STILE
# =========================================================
st.set_page_config(page_title="Technical Generator v7.8", layout="wide")

st.markdown("""
    <style>
        div[data-testid="stWidgetLabel"] { margin-bottom: 5px !important; }
        .stRadio div[role="radiogroup"] { gap: 5px !important; }
        .stRadio label p, .stPills label p { font-size: 1.0rem !important; font-weight: 450 !important; }
        h3 { font-size: 2.0rem !important; margin-top: 25px !important; }
        [data-testid="column"] { padding: 10px !important; }
        .stButton button { border-radius: 20px; font-weight: bold; background-color: #f0f2f6; }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 1. FUNZIONE DI RESET UNIVERSALE
# =========================================================
def reset_all():
    """Cancella assolutamente ogni traccia nel session_state"""
    for key in list(st.session_state.keys()):
        if isinstance(st.session_state[key], list):
            st.session_state[key] = []
        elif isinstance(st.session_state[key], bool):
            st.session_state[key] = False
        else:
            st.session_state[key] = ""
    st.rerun()

# =========================================================
# 2. DATABASE E CONFIGURAZIONI (Versione Integrale)
# =========================================================
GLOSSARIO_TECNICO = {"mensola": "BRACKET", "gondola": "GONDOLA", "spalla": "FRAME", "innesto": "COUPLING"}

SUB_OPTIONS_CONFIG = {
    "VPA": {"Serie S": "S SERIES", "Serie SS": "SS SERIES", "Serie M": "M SERIES", "Serie L": "L SERIES"},
    "Con distanziale": {"L100": "L100", "L150": "L150", "L200": "L200", "L250": "L250"},
    "Numero diagonali": {"2": "2 DIAGONALS", "3": "3 DIAGONALS", "4": "4 DIAGONALS"},
    "Sezione": {"L55": "L55", "L80 Z/S": "L80 Z/S", "L80 Z/M": "L80 Z/M", "L100 Z/S": "L100 Z/S", "L100 Z/M": "L100 Z/M", "L120 Z/S": "L120 Z/S", "70X30": "70X30", "90X30": "90X30"}
}

MATERIALI_CONFIG = {
    "METAL COMP": {"METAL": "METAL", "ZINCATO": "GALVANIZED", "INOX": "STAINLESS STEEL", "ALLUMINIO": "ALUMINIUM"},
    "WOOD COMP": {"LAMINATO": "LAMINATED", "NOBILITATO": "MELAMINE", "TRUCIOLARE": "OSB"},
    "PLASTIC COMP": {"POLICARBONATO": "POLYCARBONATE", "PVC": "PVC", "GOMMA": "RUBBER"},
    "GLASS COMP": {"VETRO TEMPRATO": "TEMPERED GLASS", "VETRO SATINATO": "SATIN GLASS"},
    "FASTENER": {"ZINCATO": "GALVANIZED", "BRUNITO": "BURNISHED", "NERO": "BLACK"}
}

DATABASE = {
    "METAL COMP": {
        "Particolari": {
            "Piede di base": ["BASE FOOT", {"H90": "H90", "H100": "H100", "H150": "H150", "Antisismico": "SEISMIC", "Statico": "STATIC", "Regolabile": "ADJUSTABLE", "Prolunga": "- EXTENSION", "Per montante L80": "FOR L80 UPRIGHT", "Per montante L100/120": "FOR L100/L120 UPRIGHT"}, "FOOT"],
            "Zoccolatura": ["PLINTH", {"H90": "FOR H90 BASE FOOT", "H100": "FOR BASE FOOT H100", "H150": "FOR BASE FOOT H150", "Liscia": "PLAIN", "Angolo aperto": "EXTERNAL CORNER", "Angolo chiuso": "INNER CORNER", "Inclinata": "INCLINATED", "Forata": "PERFORATED", "Stondata": "ROUNDED", "Completa di paracolpo ABS": "WITH ABS BUFFER"}, "PLINTH"],
            "Pannello rivestimento": ["BACK PANEL", {"Scantonato": "NOTCHED", "Forato": "PERFORATED", "Multibarra": "MULTIBAR", "Multilame": "MULTISTRIP", "In rete": "MESH", "Forato rombo": "RUMBLE PERFORATED", "Nervato": "RIBBED", "Attacco montante": "HOOK ONTO UPRIGHT"}, "PANEL"],
            "Copripiede": ["FOOT COVER", {"H90": "FOR H90 FOOT", "H100": "FOR H100 FOOT", "H150": "FOR H150 FOOT"}, "COVER"],
            "Chiusura": ["COVER", {"Superiore": "TOP", "Tra ripiani di base": "INTER-BASE SHELF", "Con scasso": "WITH RECESS"}, "COVER"],
            "Fiancata laterale": ["SIDE PANEL", {"Portante": "LOAD-BEARING", "Non portante": "NON LOAD-BEARING", "Stondata": "ROUNDED", "Trapezoidale": "SLOPING", "Sagomata": "SHAPED"}, "SIDE-PANEL"],
            "Mensola": ["BRACKET", {"SX": "LEFT", "DX": "RIGHT", "Rinforzata": "REINFORCED", "Nervata": "RIBBED", "Per ripiano in vetro": "FOR GLASS SHELF", "Per ripiano in legno": "FOR WOODEN SHELF", "A pinza": "GRIPPED", "Minirack": "FOR MINIRACK", "1 Posizione": "ONE POSIION", "2 Posizioni": "TWO POSITION"}, "BRACKET"],
            "Ripiano": ["SHELF", {"Liscio": "PLAIN", "Forato": "PERFORATED", "Stondato": "ROUNDED", "In filo": "WIRE", "Semicircolare": "SEMICIRCULAR", "Con rinforzo": "REINFORCED", "Con inserti filettati": "WITH RIVET", "Con portaprezzo": "WITH TICKET-HOLDER", "Scantonato": "NOTCHED"}, "SHELF"],
            "Montante": ["UPRIGHT", {"Sezione": "SECTION", "Statico": "STATIC", "Antisismico": "ANTI-SEISMIC", "Regolabile": "ADJUSTABLE"}, "UPRIGHT"]
        }
    },
    "WOOD COMP": {
        "Particolari": {
            "Ripiano Legno": ["WOODEN SHELF", {"Con mensole": "WITH BRACKET", "Con lati bordati": "WITH EDGED SIDES", "Con zoccolatura": "WITH PLINTH", "Con viteria": "WITH SCREWS", "Fresata": "MILLING"}, "SHELF"],
            "Fiancata": ["WOODEN SIDE PANEL", {"Con mensole": "WITH BRACKET", "Sagomata": "SHAPED", "Con lati bordati": "WITH EDGED SIDES"}, "SIDE PANEL"]
        }
    },
    "PLASTIC COMP": {
        "Particolari": {
            "Portaprezzo": ["TICKET-HOLDER", {"Trasparente": "TRASPARENT", "Colorato": "COLOURED", "Adesivo": "ADHESIVE"}, "TICKET-HOLDER"],
            "Tappo": ["PLASTIC CAP", {}, "CAP"]
        }
    },
    "GLASS COMP": {
        "Particolari": {
            "Ripiano": ["GLASS SHELF", {}, "SHELF"],
            "Anta": ["GLASS DOOR", {"SX": "LEFT", "DX": "RIGHT", "Scorrevole": "SLIDING"}, "DOOR"]
        }
    },
    "FASTENER": {
        "Particolari": {
            "Vite": ["SCREW", {"Autoperforanti": "SELF-DRILLING", "Testa svasata": "COUNTERSUCK HEAD", "Testa esagonale": "HEX HEAD"}, "SCREW"],
            "Dado": ["NUT", {"Autobloccante": "SELF-LOCKING", "Flangiato": "FLANGED"}, "NUT"]
        }
    },
    "ASSEMBLY": {
        "Particolari": {
            "Vetrina": ["SHOWCASE", {"Terminale": "END", "Centrale": "CENTRAL", "Con illuminazione": "WITH LIGHTING"}, "SHOWCASE"],
            "Spalla": ["FRAME", {"Antisismico": "SEISMIC-RESISTANT", "L100 Z/M": "L100 Z/M", "ZINCATO": "GALVANIZED"}, "FRAME"]
        }
    }
}

TERMINI_ANTICIPATI = ["CENTRAL", "LEFT", "RIGHT", "REINFORCED", "INTERNAL", "EXTERNAL", "UPPER", "LOWER", "STATIC", "ADJUSTABLE", "SEISMIC", "TOP", "ROUNDED", "SLOPING", "SHAPED", "WIRE", "SLIDING", "CURVED", "STRAIGHT"]
OPZIONI_COMPATIBILITA = ["", "F25", "F25 BESPOKE", "F25 READY", "F50", "F50 BESPOKE", "F50 READY", "UNIVERSAL", "FORTISSIMO"]

# =========================================================
# 3. INTERFACCIA UTENTE
# =========================================================

st.title("⚙️ REG - Title Generator & Classification")

# --- BOTTONE AZZERA SUPERIORE ---
c1, c2, c3 = st.columns([2, 1, 2])
with c2:
    st.button("🔄 AZZERA TUTTO", on_click=reset_all, use_container_width=True, key="btn_top")

st.markdown("---")

col_macro, col_workarea = st.columns([1, 3], gap="large")

with col_macro:
    st.subheader("📂 1. Categoria")
    macro_it = st.radio("Scegli categoria:", options=list(DATABASE.keys()), key="macro_sel")
    
    st.markdown("---")
    st.subheader("🔗 Compatibilità")
    pills_comp = [o for o in OPZIONI_COMPATIBILITA if o]
    comp_sel = st.pills("Modelli:", options=pills_comp, selection_mode="multi", key="comp_tags")

with col_workarea:
    st.subheader("🛠️ 2. Dettagli Elemento")
    
    # Materiale
    mat_en = ""
    if macro_it != "ASSEMBLY":
        mats = MATERIALI_CONFIG.get(macro_it, {})
        if mats:
            mat_it = st.radio("Materiale:", options=list(mats.keys()), horizontal=True, key="mat_sel")
            mat_en = mats[mat_it]
    else:
        st.checkbox("ASSEMBLATA", key="check_assembled")

    # Particolare
    part_dict = DATABASE[macro_it]["Particolari"]
    scelta_it = st.radio("Dettaglio:", options=sorted(list(part_dict.keys())), horizontal=True, key="part_sel")
    part_en, extra_dict, tag_suggerito = part_dict[scelta_it]

    st.markdown("---")
    st.subheader("✨ 3. Opzioni Extra")
    extra_tags = st.pills("Opzioni:", options=list(extra_dict.keys()), selection_mode="multi", key="extra_tags")
    
    # Gestione varianti dinamiche (Sub-options)
    for ex in (extra_tags or []):
        if ex in SUB_OPTIONS_CONFIG:
            st.selectbox(f"↳ Variante per {ex}:", options=list(SUB_OPTIONS_CONFIG[ex].keys()), key=f"sub_{ex}")

    extra_libero = st.text_input("Note libere (IT):", key="extra_text")

    st.markdown("---")
    st.subheader("📏 4. Dimensioni")
    d_col1, d_col2 = st.columns([2, 1])
    with d_col1:
        c_l, c_p, c_h = st.columns(3)
        with c_l: st.text_input("L (mm)", key="dim_l")
        with c_p: st.text_input("P (mm)", key="dim_p")
        with c_h: st.text_input("H (mm)", key="dim_h")
        st.selectbox("Spessore (S)", options=["", "0.6", "0.8", "1", "1.2", "1.5", "2", "3"], key="dim_s")
    with d_col2:
        st.image("https://raw.githubusercontent.com/wAsp191/generatetext/main/Gemini_Generated_Image_rtac8jrtac8jrtac%20(1).png", width=150)

# =========================================================
# 4. GENERAZIONE E OUTPUT
# =========================================================
st.divider()

if st.button("🚀 GENERA STRINGA FINALE", use_container_width=True):
    # Logica dimensioni
    dims = [f"{k}{st.session_state[f'dim_{k.lower()}']}" for k in ["L", "P", "H"] if st.session_state.get(f"dim_{k.lower()}")]
    dim_str = "X".join(dims)
    if st.session_state.get("dim_s"): dim_str += f" S{st.session_state['dim_s']}"

    # Logica Extra
    extra_list = []
    for ex in (extra_tags or []):
        base = extra_dict.get(ex, ex.upper())
        sub = st.session_state.get(f"sub_{ex}", "")
        if sub: extra_list.append(f"{base} {SUB_OPTIONS_CONFIG[ex].get(sub, sub)}")
        else: extra_list.append(base)

    # Traduzione note veloci
    note_en = ""
    if extra_libero:
        try: note_en = GoogleTranslator(source='it', target='en').translate(extra_libero).upper()
        except: note_en = extra_libero.upper()

    # Ordinamento Prefissi/Suffissi
    pref = [e for e in extra_list if any(p in e for p in TERMINI_ANTICIPATI) and "FOR" not in e]
    suff = [e for e in extra_list if e not in pref]

    # Costruzione stringa
    core = f"{mat_en} {' '.join(pref)} {part_en} {dim_str}".strip().upper()
    parts = [core]
    if suff: parts.append(", ".join(suff).upper())
    if note_en: parts.append(note_en)
    if comp_sel: parts.append(", ".join(comp_sel))
    
    res = " - ".join(parts).replace("  ", " ")
    if st.session_state.get("check_assembled"): res = f"ASSEMBLED - {res}"
    
    st.session_state["final_res"] = res

if st.session_state.get("final_res"):
    st.subheader("📋 Risultato")
    st.code(st.session_state["final_res"])
    lunghezza = len(st.session_state["final_res"])
    if lunghezza > 99: st.error(f"Caratteri: {lunghezza} (LIMITE SUPERATO!)")
    else: st.success(f"Caratteri: {lunghezza} (OK)")

# --- BOTTONE AZZERA INFERIORE ---
st.markdown("<br>", unsafe_allow_html=True)
b_left, b_mid, b_right = st.columns([2, 1, 2])
with b_mid:
    st.button("🔄 AZZERA TUTTO", on_click=reset_all, use_container_width=True, key="btn_bottom")
