import streamlit as st
from deep_translator import GoogleTranslator
import datetime

# =========================================================
# 0. CONFIGURAZIONE PAGINA E LOGICA RESET
# =========================================================
st.set_page_config(page_title="Technical Generator v7.8", layout="wide")

# Logica di Reset corretta (fuori dal callback)
if "trigger_reset" in st.session_state and st.session_state.trigger_reset:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def activate_reset():
    st.session_state.trigger_reset = True

st.markdown("""
    <style>
        div[data-testid="stWidgetLabel"] { margin-bottom: 5px !important; }
        .stRadio div[role="radiogroup"] { gap: 5px !important; }
        .stRadio label p, .stPills label p { font-size: 1.0rem !important; font-weight: 450 !important; }
        h3 { font-size: 2.0rem !important; margin-top: 25px !important; margin-bottom: 20px !important; }
        [data-testid="column"] { padding: 15px !important; }
        .stRadio > div { flex-wrap: wrap; display: flex; gap: 10px; }
        .stButton button { border-radius: 20px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 1. DIZIONARI E DATABASE
# =========================================================

GLOSSARIO_TECNICO = {
    "mensola": "BRACKET",
    "gondola": "GONDOLA",
    "spalla": "FRAME",
    "innesto": "COUPLING"
}

SUB_OPTIONS_CONFIG = {
    "VPA": {
        "Serie S": "S SERIES",
        "Serie SS": "SS SERIES",
        "Serie M": "M SERIES",
        "Serie L": "L SERIES"
    },
    "Con distanziale": {
        "L100": "L100", "L150": "L150", "L200": "L200", "L250": "L250"
    },
    "Numero diagonali": {
        "2": "2 DIAGONALS", "3": "3 DIAGONALS", "4": "4 DIAGONALS"
    },
    "Sezione": {
        "L55": "L55", "L80 Z/S": "L80 Z/S", "L80 Z/M": "L80 Z/M", "L100 Z/S": "L100 Z/S", "L100 Z/M": "L100 Z/M", "L120 Z/S": "L120 Z/S", "70X30": "70X30", "90X30": "90X30"
    },
    "Tipologia di mensola": {
        "Mensola saldata a filo superiore": "UPPER BRACKET", "Mensola saldata a filo inferiore": "LOWER BRACKET"
    }
}

EXTRA_CON_INPUT_MANUALE = ["Sezione circolare", "Sezione quadrata"]

MATERIALI_CONFIG = {
    "METAL COMP": {"METAL": "METAL", "ZINCATO": "GALVANIZED", "INOX": "STAINLESS STEEL", "ALLUMINIO": "ALUMINIUM"},
    "WOOD COMP": {"LAMINATO": "LAMINATED", "NOBILITATO": "MELAMINE", "TRUCIOLARE": "OSB"},
    "PLASTIC COMP": {"POLICARBONATO": "POLYCARBONATE", "PVC": "PVC", "GOMMA": "RUBBER"},
    "GLASS COMP": {"VETRO TEMPRATO": "TEMPERED GLASS", "VETRO SATINATO": "SATIN GLASS"},
    "FASTENER": {"ZINCATO": "GALVANIZED", "BRUNITO": "BURNISHED", "NERO": "BLACK"}
}

DATABASE = {
    "METAL COMP": {
        "macro_en": "METAL COMPONENT",
        "Particolari": {
            "Piede di base": ["BASE FOOT", {"H90": "H90", "H100": "H100", "H150": "H150", "Antisismico": "SEISMIC", "Statico": "STATIC", "Regolabile": "ADJUSTABLE", "Prolunga": "- EXTENSION", "Per montante L80": "FOR L80 UPRIGHT", "Per montante L100/120": "FOR L100/L120 UPRIGHT"}, "FOOT"],
            "Zoccolatura": ["PLINTH", {"H90": "FOR H90 BASE FOOT", "H100": "FOR BASE FOOT H100", "H150": "FOR BASE FOOT H150", "Liscia": "PLAIN", "Angolo aperto": "EXTERNAL CORNER", "Angolo chiuso": "INNER CORNER", "Inclinata": "INCLINATED", "Forata": "PERFORATED", "Stondata": "ROUNDED", "Completa di paracolpo ABS": "WITH ABS BUFFER"}, "PLINTH"],
            "Pannello rivestimento": ["BACK PANEL", {"Scantonato": "NOTCHED", "Forato": "PERFORATED", "Multibarra": "MULTIBAR", "Multilame": "MULTISTRIP", "In rete": "MESH", "Forato rombo": "RUMBLE PERFORATED", "Nervato": "RIBBED", "Attacco montante": "HOOK ONTO UPRIGHT"}, "PANEL"],
            "Copripiede": ["FOOT COVER", {"H90": "FOR H90 FOOT", "H100": "FOR H100 FOOT", "H150": "FOR H150 FOOT"}, "COVER"],
            "Chiusura": ["COVER", {"Superiore": "TOP", "Tra ripiani di base": "INTER-BASE SHELF", "Con scasso": "WITH RECESS"}, "COVER"],
            "Fiancata laterale": ["SIDE PANEL", {"Portante": "LOAD-BEARING", "Non portante": "NON LOAD-BEARING", "Stondata": "ROUNDED", "Trapezoidale": "SLOPING", "Sagomata": "SHAPED"}, "SIDE-PANEL"],
            "Mensola": ["BRACKET", {"SX": "LEFT", "DX": "RIGHT", "Rinforzata": "REINFORCED", "Nervata": "RIBBED", "Per ripiano in vetro": "FOR GLASS SHELF", "Per ripiano in legno": "FOR WOODEN SHELF", "A pinza": "GRIPPED", "Minirack": "FOR MINIRACK", "1 Posizione": "ONE POSIION", "2 Posizioni": "TWO POSITION"}, "BRACKET"],
            "Ripiano": ["SHELF", {"Liscio": "PLAIN", "Forato": "PERFORATED", "Stondato": "ROUNDED", "In filo": "WIRE", "Semicircolare": "SEMICIRCULAR", "Con rinforzo": "REINFORCED", "Con inserti filettati": "WITH RIVET", "Con portaprezzo": "WITH TICKET-HOLDER", "Scantonato": "NOTCHED"}, "SHELF"],
            "Cesto in filo": ["WIRE-BASKET", {"Per attacco montante": "HOOK ONTO UPRIGHT", "Per attacco fiancata": "HOOK ONTO SIDE-PANEL", "Impilabile": "STACKABLE", "Con mensole saldate": "WITH WELDED BRACKET"}, "BASKET"],
            "Cielino": ["CANOPY", {"Dritto": "STRAIGHT", "Inclinato": "SLOPING", "Con finestra": "WITH WINDOW", "Stondato": "CURVED", "Centrale": "CENTRAL", "Frontale in lamiera": "SHEET METAL FASCIA", "Con illuminazione": "WITH LIGHTING"}, "CANOPY"],
            "Corrente": ["BEAM", {"A seggiola": "L-SHAPED PROFILE", "VPA": "VPA", "Tipologia di mensola": ""}, "BEAM"],
            "Diagonale": ["DIAGONAL", {"Forata": "PERFORATED", "Per crociera verticale": "FOR VERTICAL CROSS-WALL"}, "DIAGONAL"],
            "Distanziale": ["SPACER", {"Per controventatura": "FOR CROSS-WALL"}, "SPACER"],
            "Gancio": ["HOOK", {"Singolo": "SINGLE", "Predisposto per portaprezzo": "ACCEPTS TICKET-HOLDER", "Doppio": "DOUBLE", "Rovescio": "REVERSE", "Attacco barra": "HOOK FOR BAR", "Attacco multilame": "HOOK FOR MULTISTRIP", "Attacco pannello forato": "HOOK FOR SLOTTED PANEL"}, "HOOK"],
            "Profilo": ["PROFILE", {"Profilo a L": "L-SHAPED", "Profilo a U": "U-SHAPED"}, "PROFILE"],
            "Rinforzo": ["STIFFENER", {"Asolato": "SLOTTED", "Per ripiano di base": "FOR BASE SHELF", "Per fiancata": "FOR SIDE PANEL"}, "STIFFENER"],
            "Staffa": ["PLATE", {"Con viteria": "WITH SCREWS", "Di collegamento": "CONNECTING"}, "PLATE"],
            "Anta/sportello": ["DOOR", {"Scorrevoli": "SLIDING", "Con foro serratura": "WITH LOCK HOLE", "A saracinesca": "SHUTTER", "Forata": "PERFORATED"}, "DOOR"],
            "Piastra di fissaggio": ["FIXING PLATE", {"Con viti": "COMPLETE WITH SCREW"}, "PLATE"],
            "Cassetto estraibile": ["PULL-OUT DRAWER", {"Su ruote": "ON WHEELS", "Per piede H100": "FOR BASE FOOT H100", "Per piede H150": "FOR BASE FOOT H150", "Con serratura": "WITH LOCK", "Senza serratura": "WITHOUT LOCK"}, "DRAWER"],
            "Coprimontante": ["UPRIGHT-COVER", {"Per montante H70": "FOR H70 UPRIGHT", "Per montante H90": "FOR H90 UPRIGHT"}, "COVER"],
            "Pedana di base": ["BASE PLATFORM", {"Con rinforzi": "WITH REINFORCEMENT"}, "BASE"],
            "Divisorio": ["DIVIDER", {"In filo": "WIRE", "Trapezoidale": "SLOPING", "Per ripiano": "FOR SHELF"}, "DIVIDER"],
            "Frontalino": ["RISER", {"In filo": "WIRE", "Per ripiano": "FOR SHELF", "Cromato": "CHROMED", "Verniciato": "PAINTED"}, "RISER"],
            "Compensazione": ["FILLER PIECE", {"Per piede di base": "FOR BASE FOOT", "Per spalle L100/L120": "FOR L100/L120 FRAME"}, "SPACER"],
            "Controventatura": ["BRACING", {"Per montante": "FOR UPRIGHT", "Con mensole saldate": "WITH WELDING BRACKET", "Passo 25": "PITCH 25", "Passo 50": "PITCH 50"}, "BRACING"],
            "Traversino": ["CROSS BAR", {"Forato": "PERFORATED", "Con mensole saldate": "WITH WELDING BRACKET", "Con viteria": "WITH SCREWS"}, "CROSS BAR"],
            "Tubolare": ["TUBULAR", {"Con componente saldato": "WITH WELDED ELEMENT", "Sezione quadrata": "SQUARE SECTION", "Sezione circolare": "CIRCULAR SECTION", "Piegato-saldato": "BENT AND WELDED", "Con mensole saldate": "WITH WELDING BRACKET", "Con viteria": "WITH SCREWS"}, "BAR"],
            "Filo": ["WIRE", {"Piegato": "BENT", "Piegato-saldato": "BENT AND WELDED", "Con viteria saldata": "WITH WELDING SCREWS"}, "WIRE"],
            "Montante": ["UPRIGHT", {"Sezione": "", "Statico": "STATIC", "Antisismico": "ANTI-SEISMIC", "Regolabile": "ADJUSTABLE"}, "UPRIGHT"],
            "Lamiera generica": ["SHEET METAL", {"Forata": "PERFORATED", "Piegata": "BENT", "Saldata": "WELDED"}, "GENERIC SHEET METAL"]
        }
    },
    "WOOD COMP": {
        "macro_en": "WOOD COMPONENT",
        "Particolari": {
            "Ripiano Legno": ["WOODEN SHELF", {"Con mensole": "WITH BRACKET", "Con lati bordati": "WITH EDGED SIDES", "Con zoccolatura": "WITH PLINTH", "Con viteria": "WITH SCREWS", "Fresata": "MILLING"}, "SHELF"],
            "Schienale Legno": ["WOODEN BACK", {"Con mensole": "WITH BRACKET", "Con viteria": "WITH SCREWS", "Con lati bordati": "WITH EDGED SIDES"}, "PANEL"],
            "Cielino": ["WOODEN CANOPY", {"Con mensole": "WITH BRACKET", "Con viteria": "WITH SCREWS", "Dritto": "STRAIGHT", "Inclinato": "SLOPING", "Con finestra": "WITH WINDOW", "Stondato": "CURVED", "Centrale": "CENTRAL", "Con illuminazione": "WITH LIGHTING", "Con lati bordati": "WITH EDGED SIDES"}, "CANOPY"],
            "Zoccolatura": ["WOODEN PLINTH", {"H100": "H100", "H150": "H150", "Con lati bordati": "WITH EDGED SIDES", "Con viteria": "WITH SCREWS"}, "PLINTH"],
            "Fiancata": ["WOODEN SIDE PANEL", {"Con mensole": "WITH BRACKET", "Sagomata": "SHAPED", "Con lati bordati": "WITH EDGED SIDES", "Con viteria": "WITH SCREWS", "Fresata": "MILLING"}, "SIDE PANEL"],
            "Copripiede": ["WOODEN FOOT-COVER", {"H100": "FOR H100 BASE FOOT", "H150": "FOR H150 BASE FOOT", "Con lati bordati": "WITH EDGED SIDES", "Con viteria": "WITH SCREWS"}, "COVER"],
            "Coprimontante": ["WOODEN UPRIGHT-COVER", {"Minirack": "MINIRACK", "Con lati bordati": "WITH EDGED SIDES", "Con viteria": "WITH SCREWS"}, "COVER"],
            "Compensazione": ["WOODEN FILLER PIECE", {"Per Top legno": "FOR TOP SHELF"}, "SPACER"]
        }
    },
    "PLASTIC COMP": {
        "macro_en": "PLASTIC COMPONENT",
        "Particolari": {
            "Tappo": ["PLASTIC CAP", {}, "CAP"],
            "Guarnizione": ["GASKET", {}, "ACCESSORY"],
            "Divisorio": ["DIVIDER", {"Sloping": "SLOPING", "Per ripiano": "FOR SHELF"}, "DIVIDER"],
            "Frontalino": ["RISER", {"Per ripiano": "FOR SHELF", "Trasparente": "TRASPARENT"}, "RISER"],
            "Portaprezzo": ["TICKET-HOLDER", {"Trasparente": "TRASPARENT", "Colorato": "COLOURED", "Con tasca oscillante": "WITH LIFT-UP POCKET", "Adesivo": "ADHESIVE", "Con asola centrale": "WITH CENTRAL SLOT"}, "TICKET-HOLDER"]
        }
    },
    "GLASS COMP": {
        "macro_en": "GLASS COMPONENT",
        "Particolari": {
            "Ripiano": ["GLASS SHELF", {}, "SHELF"],
            "Anta": ["GLASS DOOR", {"SX": "LEFT", "DX": "RIGHT", "Con foro serratura": "WITH LOCK HOLE", "Scorrevole": "SLIDING"}, "DOOR"],
            "Cancelletto": ["GLASS ARM", {"SX": "LEFT", "DX": "RIGHT", "Illuminato": "ILLUMINATED"}, "ARM"],
        }
    },
    "FASTENER": {
        "macro_en": "FASTENER",
        "Particolari": {
            "Vite": ["SCREW", {"Autoperforanti": "SELF-DRILLING", "Testa svasata": "COUNTERSUCK HEAD", "Testa esagonale": "HEX HEAD", "Testa a croce": "CROSS HEAD", "Testa esagono incassato": "HEXAGON SOCKET HEAD", "Testa Bombata": "T-BOM"}, "SCREW"],
            "Bullone": ["BOLT", {}, "FASTENER"],
            "Rondella": ["WASHER", {"Dentellata": "SERRATED LOCK", "Fascia Larga": "WIDE BEND", "Elastica": "GROWER"}, "WASHER"],
            "Dado": ["NUT", {"Autobloccante": "SELF-LOCKING", "Flangiato": "FLANGED"}, "NUT"],
            "Inserti filettati": ["RIVET", {"Con testa": "WITH HEAD", "Senza testa": "WITHOUT HEAD"}, "RIVET"]
        }
    },
    "ASSEMBLY": {
        "macro_en": "ASSEMBLY",
        "Particolari": {
            "Vetrina": ["SHOWCASE", {"Terminale": "END", "Centrale": "CENTRAL", "Con illuminazione": "WITH LIGHTING", "Con ante scorrevoli": "WITH SLIDING DOOR"}, "SHOWCASE"],
            "Espositore": ["DISPLAY", {"Mobile": "MOBILE", "Per alimenti": "FOR FOOD"}, "DISPLAY"],
            "Totem": ["TOTEM", {"Mobile": "MOBILE", "Girevole": "SWIVEL", "Per casse automatiche": "FOR SELF PAY"}, "DISPLAY"],
            "Spalla": ["FRAME", {"Antisismico": "SEISMIC-RESISTANT", "L100 Z/M": "L100 Z/M", "L100 Z/S": "L100 Z/S", "L120 Z/M": "L120 Z/M", "L120 Z/S": "L120 Z/S", "L80 Z/M": "L80 Z/M", "L80 Z/S": "L80 Z/S", "L55": "L55", "ZINCATO": "GALVANIZED"}, "FRAME"],
            "Controventatura": ["CROSS-BRACING", {"Gondola": "GONDOLA", "Sezione L120": "L120", "Sezione L100": "L100", "Sezione L80": "L80", "Su due livelli": "TWO LEVELS", "Numero diagonali": "WITH", "Con distanziale": "WITH SPACER"}, "CROSS-BRACING"],
            "Banco espositore di legno": ["WOODEN DESK", {"Con cassetto": "WITH DRAWER", "Con ruote": "WITH WHEELS"}, "DESK"],
            "Avancassa": ["IMPULSE UNIT", {"Con ripiani": "WITH SHELF", "Con ripiani inclinati": "WITH INCLINATED SHELF", "Con rete divisoria": "WITH DIVIDING NET", "Con ruote": "WITH WHEELS", "Con ganci": "WITH HOOKS", "Con batticarrello": "WITH TROLLEY BEATER"}, "DISPLAY"],
        }
    }
}

OPZIONI_COMPATIBILITA = ["", "F25", "F25 BESPOKE", "F25 READY", "F50", "F50 BESPOKE", "F50 READY", "UNIVERSAL", "FORTISSIMO", "MINIRACK"]

MAPPA_NORMATIVE_FASTENER = {
    "Vite": {
        "": "",
        "DIN 912 - Brugola testa cilindrica": "DIN 912",
        "DIN 933 - Esagonale filetto totale": "DIN 933",
        "DIN 931 - Esagonale filetto parziale": "DIN 931",
        "DIN 7991 - Testa svasata esagono incassato": "DIN 7991",
        "ISO 7380 - Testa bombata esagono incassato": "ISO 7380",
        "DIN 571 - Tirafondo per legno": "DIN 571",
        "DIN 7504-K - Autoperforante Esagonale": "DIN 7504-K",
        "DIN 7504-N - Autoperforante Bombata": "DIN 7504-N",
        "DIN 7504-P - Autoperforante Svasata": "DIN 7504-P"
    },
    "Dado": {
        "": "",
        "DIN 934 - Esagonale standard": "DIN 934",
        "DIN 985 - Autobloccante nylon": "DIN 985",
        "DIN 6923 - Flangiato zigrinato": "DIN 6923"
    },
    "Rondella": {
        "": "",
        "DIN 125 - Piana standard": "DIN 125",
        "DIN 9021 - Fascia larga": "DIN 9021",
        "DIN 6798 - Dentellata": "DIN 6798",
        "DIN 127 - Grower (elastica)": "DIN 127"
    },
    "Bullone": { "": "" },
    "Inserti filettati": { "": "" }
}

OPZIONI_SPESSORE_STD = ["", "0.5", "0.6", "0.75", "0.8", "1", "1.2", "1.5", "2", "2.5", "3", "3.5", "4", "4.5", "5", "6", "8", "10"]
OPZIONI_SPESSORE_WOOD = ["", "10mm", "15mm", "18mm", "19mm", "20mm", "22mm", "24mm", "25mm", "30mm", "35mm"]

TERMINI_ANTICIPATI = [
    "CENTRAL", "LEFT", "RIGHT", "REINFORCED", "INTERNAL", "EXTERNAL", "STATIC", "ADJUSTABLE", "SEISMIC",
    "MULTIBAR", "MULTISTRIP", "TOP", "INTER-BASE SHELF", "ROUNDED", "SLOPING", "SHAPED", "CONNECTING", "SHUTTER", "COUPLING",
    "WIRE", "GRIPPED", "CHROMED", "PAINTED", "MESH", "SLIDING", "CURVED", "STRAIGHT", "MILLING", "WIRE-BASKET",
    "SEMICIRCULAR", "SINGLE", "DOUBLE", "END", "L-SHAPED", "U-SHAPED", "SERRATED LOCK", "UPRIGHT GRAFT"
]

# =========================================================
# 2. LOGICA FUNZIONALE
# =========================================================

def update_dims_from_section():
    sez = st.session_state.get("sub_Sezione", "")
    if "L55" in sez:
        st.session_state.dim_l, st.session_state.dim_p = "55", "63"
    elif "L80" in sez:
        st.session_state.dim_l, st.session_state.dim_p = "80", "69"
    elif "L100" in sez:
        st.session_state.dim_l, st.session_state.dim_p = "100", "75"
    elif "L120" in sez:
        st.session_state.dim_l, st.session_state.dim_p = "120", "75"
    elif "70X30" in sez:
        st.session_state.dim_l, st.session_state.dim_p = "70", "30"
    elif "90X30" in sez:
        st.session_state.dim_l, st.session_state.dim_p = "90", "30"

# =========================================================
# 3. INTERFACCIA UTENTE
# =========================================================

st.title("⚙️ REG - Title Generator & Classification")

# --- 1. TASTO AZZERA SUPERIORE CENTRATO ---
c1, c2, c3 = st.columns([2, 1, 2])
with c2:
    st.button("🔄 AZZERA TUTTO", on_click=activate_reset, use_container_width=True, key="btn_top")

st.markdown("---")

col_macro, col_workarea = st.columns([1, 3], gap="large")

with col_macro:
    st.subheader("📂 1. Categoria")
    macro_it = st.radio("Seleziona categoria:", options=list(DATABASE.keys()))
    
    uni_en_1090_active = False 
    
    if macro_it != "FASTENER":
        st.markdown("---")
        st.subheader("🔗 Compatibilità")
        pills_compatibilita = [opt for opt in OPZIONI_COMPATIBILITA if opt]
        
        # CAMBIO DA "multi" A "single"
        comp_selezionata = st.pills("Modelli:", options=pills_compatibilita, selection_mode="single", key="comp_tags")
        
        # Trasformiamo in lista per non rompere la logica successiva del codice
        comp_selezionate = [comp_selezionata] if comp_selezionata else []
        
        # Logica strutturale (rimane valida)
        modelli_strutturali = ["FORTISSIMO", "MINIRACK"]
        if any(m in comp_selezionate for m in modelli_strutturali):
            st.warning("⚡ Configurazione Strutturale")
            uni_en_1090_active = st.checkbox("Certificazione UNI EN-1090", value=False, key="check_1090")
    else:
        comp_selezionate = []

with col_workarea:
    st.subheader("🛠️ 2. Materiale e Particolare")
    
    mat_en = ""
    if macro_it == "ASSEMBLY":
        st.checkbox("ASSEMBLATA", key="check_assembled")
    else:
        materiali_disponibili = MATERIALI_CONFIG.get(macro_it, {})
        if materiali_disponibili:
            mat_it = st.radio(f"Materiale:", options=list(materiali_disponibili.keys()), horizontal=True)
            mat_en = materiali_disponibili[mat_it]
    
    part_dict = DATABASE[macro_it]["Particolari"]
    
    # --- Modifica: Gestione Placeholder (index=None) ---
    def format_part_label(nome_it):
        if nome_it is None:
            return "Seleziona o digita il particolare..."
        nome_en = part_dict[nome_it][0]
        return f"🔧 {nome_it} ({nome_en})"
        
    scelta_part_it = st.selectbox(
        "Cerca o seleziona dettaglio:", 
        options=sorted(list(part_dict.keys())), 
        index=None,
        placeholder="Seleziona o digita il particolare...",
        format_func=format_part_label,
        key="selectbox_part"
    )

    st.markdown("---")
    st.subheader("✨ 3. Extra e Note")
    
    # Variabili predefinite in caso di selezione nulla
    part_en = ""
    extra_dedicati_dict = {}
    tag_suggerimento = ""
    extra_selezionati = []
    
    if scelta_part_it:
        dati_part = part_dict[scelta_part_it]
        part_en, extra_dedicati_dict, tag_suggerimento = dati_part[0], dati_part[1], dati_part[2]
        
        extra_options = list(extra_dedicati_dict.keys())
        if extra_options:
            extra_selezionati = st.pills(f"Opzioni per {scelta_part_it}:", options=extra_options, selection_mode="multi", key="extra_tags")
            
            if extra_selezionati:
                for ex in extra_selezionati:
                    if ex in SUB_OPTIONS_CONFIG:
                        st.caption(f"↳ Specifiche per: **{ex}**")
                        opzioni_sub = SUB_OPTIONS_CONFIG[ex]
                        st.selectbox(f"↳ Seleziona variante {ex}:", options=list(opzioni_sub.keys()), key=f"sub_{ex}", label_visibility="collapsed", on_change=update_dims_from_section if ex=="Sezione" else None)
                    elif ex in EXTRA_CON_INPUT_MANUALE:
                        st.caption(f"↳ Inserimento manuale per: **{ex}**")
                        st.text_input(f"Specifica valore per {ex} (es. 40x40 o D30):", key=f"manual_{ex}", label_visibility="collapsed")
        else:
            st.info("Nessuna opzione extra disponibile per questo elemento.")
    else:
        st.info("⚠️ Seleziona prima un particolare nel punto 2 per vedere le opzioni extra.")

    extra_libero = st.text_input("Note libere (IT):", key="extra_text").strip()

    st.markdown("---")
    st.subheader("📏 4. Dimensioni e Normative")
    
    col_input, col_img = st.columns([2, 1])
    
    with col_input:
        if macro_it == "FASTENER":
            c_f1, c_f2, c_f3 = st.columns(3)
            with c_f1: dim_l = st.text_input("Lunghezza (L)", key="dim_l")
            with c_f2: dim_dia = st.text_input("Diametro (D/M)", key="dim_dia")
            
            opzioni_filtrare = {"": ""}
            if scelta_part_it and scelta_part_it in MAPPA_NORMATIVE_FASTENER:
                opzioni_filtrare = MAPPA_NORMATIVE_FASTENER[scelta_part_it]
            
            with c_f3: 
                norma_scelta_estesa = st.selectbox(f"Normativa", options=list(opzioni_filtrare.keys()))
                normativa = opzioni_filtrare[norma_scelta_estesa] if norma_scelta_estesa else ""
            
            dim_p, dim_h, dim_s, dim_dia_gen = "", "", "", ""
        else:
            # --- Modifica: Aggiunto campo Diametro separato ---
            c_g1, c_g2 = st.columns(2)
            with c_g1:
                dim_l = st.text_input("Lunghezza (L)", key="dim_l")
                dim_h = st.text_input("Altezza (H)", key="dim_h")
            with c_g2:
                dim_p = st.text_input("Profondità (P)", key="dim_p")
                dim_dia_gen = st.text_input("Diametro (Ø)", key="dim_dia_gen")
                
            if macro_it != "ASSEMBLY":
                lista_spessori = OPZIONI_SPESSORE_WOOD if macro_it == "WOOD COMP" else OPZIONI_SPESSORE_STD
                dim_s = st.selectbox("Spessore (S)", options=lista_spessori, key="dim_s")
            else: 
                dim_s = ""
            
    with col_img:
        st.image("https://raw.githubusercontent.com/wAsp191/generatetext/main/Gemini_Generated_Image_rtac8jrtac8jrtac%20(1).png", caption="Schema Riferimento", use_container_width=True)

# =========================================================
# 4. LOGICA DI GENERAZIONE E TRADUZIONE
# =========================================================

st.divider()

if 'stringa_editabile' not in st.session_state:
    st.session_state['stringa_editabile'] = ""

if st.button("🚀 GENERA STRINGA FINALE", use_container_width=True):
    if not scelta_part_it:
        st.error("⚠️ Seleziona un particolare prima di generare la stringa!")
    else:
        # --- A. Dimensioni ---
        dim_final_parts = []
        if macro_it == "FASTENER":
            d_val = st.session_state.get("dim_dia", "").strip().upper()
            l_val = st.session_state.get("dim_l", "").strip().upper()
            if d_val:
                prefix_d = "" if d_val.startswith('M') else "D"
                dim_final_parts.append(f"{prefix_d}{d_val}")
            if l_val:
                dim_final_parts.append(f"L{l_val}")
            dim_final = "X".join(dim_final_parts)
            if 'normativa' in locals() and normativa: dim_final += f" {normativa}"
        else:
            l_val_s = st.session_state.get("dim_l", "").strip().upper()
            p_val_s = st.session_state.get("dim_p", "").strip().upper()
            h_val_s = st.session_state.get("dim_h", "").strip().upper()
            dia_val_s = st.session_state.get("dim_dia_gen", "").strip().upper()
            s_val = st.session_state.get("dim_s", "").strip()
            
            if l_val_s: dim_final_parts.append(f"L{l_val_s}")
            if p_val_s: dim_final_parts.append(f"P{p_val_s}")
            if h_val_s: dim_final_parts.append(f"H{h_val_s}")
            
            lph_str = "X".join(dim_final_parts)
            
            # --- Modifica: Assemblaggio LPH + Ø + S ---
            dim_final_comps = []
            if lph_str: dim_final_comps.append(lph_str)
            if dia_val_s: dim_final_comps.append(f"Ø{dia_val_s}")
            if s_val: dim_final_comps.append(f"S{s_val}")
            
            dim_final = " ".join(dim_final_comps)

        # --- B. Extra da Bottoni ---
        extra_pills_list = []
        for ex in (extra_selezionati or []):
            base_trans = extra_dedicati_dict.get(ex, ex.upper())
            if ex in SUB_OPTIONS_CONFIG:
                sub_key = f"sub_{ex}"
                valore_sub_it = st.session_state.get(sub_key, "")
                traduzione_sub = SUB_OPTIONS_CONFIG[ex].get(valore_sub_it, "")
                extra_pills_list.append(f"{base_trans} {traduzione_sub}".strip())
            elif ex in EXTRA_CON_INPUT_MANUALE:
                manual_val = st.session_state.get(f"manual_{ex}", "").strip().upper()
                if manual_val: extra_pills_list.append(f"{base_trans} {manual_val}")
                else: extra_pills_list.append(base_trans)
            else:
                extra_pills_list.append(base_trans)

        # --- C. Note Libere ---
        note_libere_tradotte = ""
        if extra_libero:
            testo_pulito = extra_libero.lower()
            for ita, eng in GLOSSARIO_TECNICO.items():
                if ita in testo_pulito:
                    testo_pulito = testo_pulito.replace(ita, eng)
            try:
                note_libere_tradotte = GoogleTranslator(source='it', target='en').translate(testo_pulito).upper()
            except:
                note_libere_tradotte = extra_libero.upper()

        # --- D. Ordinamento ---
        prefissi = [ex for ex in extra_pills_list if any(p in ex for p in TERMINI_ANTICIPATI) and "FOR" not in ex]
        suffissi = [ex for ex in extra_pills_list if ex not in prefissi]
        
        prefix_str = " ".join(prefissi) if prefissi else ""
        extra_suffissi_str = ", ".join(suffissi) if suffissi else ""
        
        comp_list = [c for c in (comp_selezionate or []) if c.strip()]
        comp_str = ", ".join(comp_list) if comp_list else ""

        # --- E. Assemblaggio ---
        # CONTROLLO RIDONDANZA: Se il materiale è METAL e il nome parte contiene già METAL (es. SHEET METAL)
        # evitiamo di scrivere METAL SHEET METAL.
        
        if mat_en == "METAL" and "METAL" in part_en.upper():
            # In questo caso usiamo solo part_en senza aggiungere mat_en davanti
            descrizione_centrale = f"{prefix_str} {part_en} {dim_final}".strip().replace("  ", " ")
        else:
            # Caso standard (es. METAL BRACKET)
            descrizione_centrale = f"{mat_en} {prefix_str} {part_en} {dim_final}".strip().replace("  ", " ")
        
        final_segments = [descrizione_centrale]
        if extra_suffissi_str: final_segments.append(extra_suffissi_str)
        if note_libere_tradotte: final_segments.append(note_libere_tradotte) 
        if comp_str: final_segments.append(comp_str)
        
        temp_str = " - ".join(final_segments).upper().replace("  ", " ")
        temp_str = temp_str.replace("WITH WITH", "WITH")
        
        if temp_str.count("WITH") > 1:
            first_with_idx = temp_str.find("WITH")
            first_with_end = first_with_idx + 4
            parte_iniziale = temp_str[:first_with_end]
            parte_restante = temp_str[first_with_end:].replace("WITH", "AND")
            temp_str = parte_iniziale + parte_restante

        if macro_it == "ASSEMBLY" and st.session_state.get("check_assembled", False):
            temp_str = f"ASSEMBLED - {temp_str}"
        
        if uni_en_1090_active:
            temp_str = f"UNI EN-1090 - {temp_str}"
            
        st.session_state['stringa_editabile'] = temp_str.replace("  ", " ").strip()

# =========================================================
# 5. OUTPUT
# =========================================================

if st.session_state['stringa_editabile']:
    st.markdown("### 📋 Risultato Finale")
    st.code(st.session_state['stringa_editabile'], language=None)
    
    with st.expander("✏️ Modifica testo manualmente"):
        st.text_input("Modifica qui:", key='stringa_editabile', label_visibility="collapsed")

    lunghezza = len(st.session_state['stringa_editabile'])
    if lunghezza >= 99:
        st.error(f"⚠️ LIMITE SUPERATO ({lunghezza})")
    else:
        st.success(f"Lunghezza: {lunghezza} caratteri")

    comp_list_tags = [c for c in (comp_selezionate or []) if c.strip()]
    
    # Tag suggerimento gestito in modo sicuro
    all_tags = []
    if 'tag_suggerimento' in locals() and tag_suggerimento:
        all_tags.append(tag_suggerimento.upper())
    all_tags.extend([c.upper() for c in comp_list_tags])
    
    if uni_en_1090_active:
        all_tags.append("UNI EN-1090-1")
    if 'normativa' in locals() and normativa:
        all_tags.append(normativa.upper())
    
    if all_tags:
        st.info(f"**TAGS:** {' | '.join(all_tags)}")

# --- 2. TASTO AZZERA INFERIORE CENTRATO ---
st.markdown("<br>", unsafe_allow_html=True)
cb1, cb2, cb3 = st.columns([2, 1, 2])
with cb2:
    st.button("🔄 AZZERA TUTTO", on_click=activate_reset, use_container_width=True, key="btn_bottom")

# =========================================================
# 6. FEEDBACK
# =========================================================

st.sidebar.markdown("---")
st.sidebar.header("📢 Beta Test Feedback")

with st.sidebar.expander("🆘 Segnala mancanza o errore", expanded=False):
    st.write("Usa questo spazio per suggerire nuovi materiali, particolari o correzioni.")
    tipo_segnalazione = st.selectbox(
        "Cosa vorresti aggiungere?", 
        ["Particolare Mancante", "Materiale", "Aggiungi/rimuovi Extra", "Normativa", "Errore Traduzione", "Altro"],
        key="tipo_fb"
    )
    nota_feedback = st.text_area("Descrivi la modifica:", placeholder="Es: Manca la vite testa cilindrica DIN 912...", key="nota_fb")
    
    if st.button("Invia Segnalazione", use_container_width=True):
        if nota_feedback:
            ora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            nota_pulita = nota_feedback.replace(";", ",").replace("\n", " ")
            nuova_riga = f"{ora};{tipo_segnalazione};{nota_pulita}\n"
            
            try:
                with open("feedback.csv", "a", encoding="utf-8") as f:
                    f.write(nuova_riga)
                st.success("✅ Ricevuto! Grazie per l'aiuto.")
            except Exception as e:
                st.error(f"Errore nel salvataggio: {e}")
        else:
            st.warning("Inserisci un messaggio prima di inviare.")

st.sidebar.markdown("---")
with st.sidebar.expander("🛠️ Area Admin (Download)"):
    pw = st.text_input("Password accesso dati", type="password")
    if pw == "admin2024": 
        try:
            with open("feedback.csv", "rb") as file:
                st.download_button(
                    label="📥 SCARICA TUTTI I FEEDBACK",
                    data=file,
                    file_name="feedback_colleghi.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        except FileNotFoundError:
            st.info("Nessun feedback presente al momento.")
    elif pw != "":
        st.error("Password errata")
