import streamlit as st
from deep_translator import GoogleTranslator

# =========================================================
# 0. CONFIGURAZIONE PAGINA E LOGICA RESET (POTENZIATA)
# =========================================================
st.set_page_config(page_title="Technical Generator v8.7", layout="wide")

def activate_reset():
    """Reset mirato dei campi di input senza mandare in crash i componenti"""
    
    # 1. Definizione delle chiavi
    keys_to_reset = [
        'dim_l', 'dim_p', 'dim_h', 'dim_dia', 'dim_dia_gen', 'dim_s',
        'extra_text', 'selectbox_part', 'comp_tags', 'extra_tags',
        'stringa_editabile', 'check_1090', 'check_assembled'
    ]
    
    for key in keys_to_reset:
        if key in st.session_state:
            # --- CORREZIONE CRASH PILLS ---
            if key == 'comp_tags':
                # Essendo selection_mode="single", resettiamo a None, non []
                st.session_state[key] = None 
            
            elif key == 'extra_tags':
                # Essendo multi-selezione, qui la lista [] va bene
                st.session_state[key] = []
                
            elif key in ['check_1090', 'check_assembled']:
                st.session_state[key] = False
                
            elif key == 'selectbox_part':
                st.session_state[key] = None
                
            else:
                st.session_state[key] = ""
    
    # 2. Reset dinamico per campi manual_ e sub_
    for key in list(st.session_state.keys()):
        if key.startswith("manual_") or key.startswith("sub_"):
            st.session_state[key] = ""
            
    st.toast("Interfaccia pulita!", icon="✨")

# =========================================================
# 1. DIZIONARI E DATABASE
# =========================================================

# --- REGOLE DI INCOMPATIBILITÀ (FILTRO SOFT) ---
# Aggiungi qui i gruppi di opzioni che NON devono essere selezionate insieme.
# Usa i nomi esatti in Italiano che compaiono a schermo.
COPPIE_INCOMPATIBILI = [
    {"Statico", "Antisismico"},
    {"Angolo aperto", "Angolo chiuso"},
    {"Portante", "Non portante"},
    {"Singolo", "Doppio"},
    {"Per ripiano in vetro", "Per ripiano in legno"},
    {"Con serratura", "Senza serratura"},
    {"Passo 25", "Passo 50"},
    {"L50", "L55"},
    {"Scorrevoli", "A saracinesca"},
    {"Per attacco montante", "Per attacco fiancata"},
    {"Superiore", "Tra ripiani di base"},
    {"Dritto", "Inclinato"},
    {"Cromato", "Verniciato"},
    {"Multibarra", "Multilame", "In rete"},
    {"Profilo a L", "Profilo a U"},
    {"Per ripiano di base", "Per fiancata"},
    {"Liscio", "Liscia", "Forato", "Forata", "In filo"},
    {"Terminale", "Centrale"},
]

GLOSSARIO_TECNICO = {
    "mensola": "BRACKET",
    "mensole": "BRACKETS",
    "gondola": "GONDOLA",
    "spalla": "FRAME",
    "innesto": "COUPLING",
    "montante": "UPRIGHT",
    "per": "FOR",
    "losanga": "LOSANGA"
}

SUB_OPTIONS_CONFIG = {
    "VPA (+)": {
        "Serie S": "S SERIES",
        "Serie SS": "SS SERIES",
        "Serie M": "M SERIES",
        "Serie L": "L SERIES"
    },
    "Con distanziale (+)": {
        "L100": "L100", "L150": "L150", "L200": "L200", "L250": "L250"
    },
    "Numero diagonali (+)": {
        "2": "2 DIAGONALS", "3": "3 DIAGONALS", "4": "4 DIAGONALS"
    },
    "Sezione (+)": {
        "L55": "L55", "L80 Z/S": "L80 Z/S", "L80 Z/M": "L80 Z/M", "L100 Z/S": "L100 Z/S", "L100 Z/M": "L100 Z/M", "L120 Z/S": "L120 Z/S", "70X30": "70X30", "90X30": "90X30"
    },
    "Tipologia di mensola (+)": {
        "Mensola saldata a filo superiore": "UPPER BRACKET", "Mensola saldata a filo inferiore": "LOWER BRACKET"
    },
    "Compatibilità piede di base (+)": {
        "Per piede H90": "FOR H90 BASE FOOT", "Per piede H100": "FOR H100 BASE FOOT", "Per piede H150": "FOR H150 BASE FOOT"
    },
    "Attacco gancio (+)": {
        "Attacco barra": "HOOK FOR BAR", "Attacco multilame": "HOOK FOR MULTISRIP", "Attacco pannello forato": "HOOK FOR SLOTTED PANEL"
    },
    "Orientamento (+)": {
        "Destra": "RIGHT", "Sinistra": "LEFT"
    },
    "Posizioni multiple (+)": {
        "1 posizione": "1 POSITION", "2 posizioni": "2 position", "3 posizioni": "3 POSITION"
    },
    "Altezza piede (+)": {
        "H90": "H90", "H100": "H100", "H150": "H150"
    },
    "Predisposto per montante (+)": {
        "L80": "FOR L80 UPRIGHT", "L100/L120": "FOR L100/L120 UPRIGHT"
    },
    "Numero tasche (+)": {
        "1 Tasca": "1 POCKET", "2 Tasche": "2 POCKETS"
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
            "Piede di base": ["BASE FOOT", {"Altezza piede (+)": "", "Predisposto per montante (+)": "", "Antisismico": "SEISMIC", "Statico": "STATIC", "Regolabile": "ADJUSTABLE"}, "FOOT"],
            "Zoccolatura": ["PLINTH", {"Compatibilità piede di base (+)": "", "Liscia": "PLAIN", "Angolo aperto": "EXTERNAL CORNER", "Angolo chiuso": "INNER CORNER", "Inclinata": "INCLINATED", "Forata": "PERFORATED", "Stondata": "ROUNDED", "Completa di paracolpo ABS": "WITH ABS BUFFER"}, "PLINTH"],
            "Pannello rivestimento": ["BACK PANEL", {"Centrale": "CTR", "Scantonato": "NOTCHED", "Forato": "PERFORATED", "Multibarra": "MULTIBAR", "Multilame": "MULTISTRIP", "In rete": "MESH", "Nervato": "RIBBED", "Attacco montante": "HOOK ONTO UPRIGHT", "Angolo aperto": "EXTERNAL CORNER", "Angolo chiuso": "INNER CORNER"}, "PANEL"],
            "Copripiede": ["FOOT COVER", {"Compatibilità piede di base (+)": ""}, "COVER"],
            "Chiusura": ["COVER", {"Superiore": "TOP", "Tra ripiani di base": "INTER-BASE SHELF", "Con scasso": "WITH RECESS"}, "COVER"],
            "Fiancata laterale": ["SIDE PANEL", {"Orientamento (+)": "", "Forata": "PERFORATED", "Portante": "LOAD-BEARING", "Non portante": "NON LOAD-BEARING", "Stondata": "ROUNDED", "Trapezoidale": "SLOPING", "Sagomata": "SHAPED"}, "SIDE-PANEL"],
            "Mensola": ["BRACKET", {"Orientamento (+)": "", "Posizioni multiple (+)": "", "Rinforzata": "REINFORCED", "Nervata": "RIBBED", "Per ripiano in vetro": "FOR GLASS SHELF", "Per ripiano in legno": "FOR WOODEN SHELF", "A pinza": "GRIPPED", "Minirack": "FOR MINIRACK"}, "BRACKET"],
            "Ripiano": ["SHELF", {"Liscio": "PLAIN", "Forato": "PERFORATED", "Stondato": "ROUNDED", "In filo": "WIRE", "Semicircolare": "SEMICIRCULAR", "Con rinforzo": "REINFORCED", "Con inserti filettati": "WITH RIVET", "Con portaprezzo": "WITH TICKET-HOLDER", "Scantonato": "NOTCHED"}, "SHELF"],
            "Cesto in filo": ["WIRE-BASKET", {"Per attacco montante": "HOOK ONTO UPRIGHT", "Per attacco fiancata": "HOOK ONTO SIDE-PANEL", "Impilabile": "STACKABLE", "Con mensole saldate": "WITH WELDED BRACKET"}, "BASKET"],
            "Cielino": ["CANOPY", {"Dritto": "STRAIGHT", "Inclinato": "SLOPING", "Con finestra": "WITH WINDOW", "Stondato": "CURVED", "Centrale": "CENTRAL", "Con illuminazione": "WITH LIGHTING"}, "CANOPY"],
            "Corrente": ["BEAM", {"A seggiola": "L-SHAPED PROFILE", "VPA (+)": "VPA", "Tipologia di mensola (+)": ""}, "BEAM"],
            "Diagonale": ["DIAGONAL", {"Forata": "PERFORATED", "Per crociera verticale": "FOR VERTICAL CROSS-WALL"}, "DIAGONAL"],
            "Distanziale": ["SPACER", {"Per controventatura": "FOR CROSS-WALL"}, "SPACER"],
            "Gancio": ["HOOK", {"Attacco gancio (+)": "", "Singolo": "SINGLE", "Predisposto per portaprezzo": "ACCEPTS TICKET-HOLDER", "Doppio": "DOUBLE", "Rovescio": "REVERSE"}, "HOOK"],
            "Profilo": ["PROFILE", {"Profilo a L": "L-SHAPED", "Profilo a U": "U-SHAPED"}, "PROFILE"],
            "Rinforzo": ["STIFFENER", {"Asolato": "SLOTTED", "Per ripiano di base": "FOR BASE SHELF", "Per fiancata": "FOR SIDE PANEL"}, "STIFFENER"],
            "Staffa": ["PLATE", {"Con viteria": "WITH SCREWS", "Di collegamento": "CONNECTING"}, "PLATE"],
            "Anta/sportello": ["DOOR", {"Scorrevoli": "SLIDING", "Con foro serratura": "WITH LOCK HOLE", "A saracinesca": "SHUTTER", "Forata": "PERFORATED"}, "DOOR"],
            "Piastra di fissaggio": ["FIXING PLATE", {"Con viti": "COMPLETE WITH SCREW"}, "PLATE"],
            "Cassetto estraibile": ["PULL-OUT DRAWER", {"Compatibilità piede di base (+)": "", "Su ruote": "ON WHEELS", "Con serratura": "WITH LOCK", "Senza serratura": "WITHOUT LOCK"}, "DRAWER"],
            "Coprimontante": ["UPRIGHT-COVER", {"Per montante H70": "FOR H70 UPRIGHT", "Per montante H90": "FOR H90 UPRIGHT"}, "COVER"],
            "Pedana di base": ["BASE PLATFORM", {"Con rinforzi": "REINFORCED"}, "BASE"],
            "Divisorio": ["DIVIDER", {"In filo": "WIRE", "Trapezoidale": "SLOPING", "Per ripiano": "FOR SHELF"}, "DIVIDER"],
            "Frontalino": ["RISER", {"In filo": "WIRE", "Per ripiano": "FOR SHELF", "Cromato": "CHROMED", "Verniciato": "PAINTED"}, "RISER"],
            "Compensazione": ["FILLER PIECE", {"Per piede di base": "FOR BASE FOOT", "Per spalle L100/L120": "FOR L100/L120 FRAME"}, "SPACER"],
            "Controventatura": ["BRACING", {"Per montante": "FOR UPRIGHT", "Con mensole saldate": "WITH WELDING BRACKET", "Passo 25": "PITCH 25", "Passo 50": "PITCH 50"}, "BRACING"],
            "Traversino": ["CROSS BAR", {"Forato": "PERFORATED", "Con mensole saldate": "WITH WELDING BRACKET", "Con viteria": "WITH SCREWS"}, "CROSS BAR"],
            "Tubolare": ["TUBULAR", {"Con componente saldato": "WITH WELDED ELEMENT", "Sezione quadrata": "SQUARE SECTION", "Sezione circolare": "CIRCULAR SECTION", "Piegato-saldato": "BENT AND WELDED", "Con mensole saldate": "WITH WELDING BRACKET", "Con viteria": "WITH SCREWS"}, "BAR"],
            "Filo": ["WIRE", {"Piegato": "BENT", "Piegato-saldato": "BENT AND WELDED", "Con viteria saldata": "WITH WELDING SCREWS"}, "WIRE"],
            "Montante": ["UPRIGHT", {"Sezione (+)": "", "Statico": "STATIC", "Antisismico": "ANTI-SEISMIC", "Regolabile": "ADJUSTABLE"}, "UPRIGHT"],
            "Lamiera generica": ["SHEET METAL", {"Forata": "PERFORATED", "Piegata": "BENT", "Saldata": "WELDED"}, "GENERIC SHEET METAL"],
            "Pannello frontale": ["FRONT PANEL", {"Forato": "PERFORATED", "Aggangio montante": "HOOK ONTO UPFRIGHT"}, "PANEL"],
            "Adattatore": ["ADAPTER", {"Forato": "PERFORATED", "Aggangio montante": "HOOK ONTO UPFRIGHT", "Passo 25": "PITCH 25", "Passo 50": "PITCH 50", "L50": "L50", "L55": "L55"}, "ADAPTER"]
        }
    },
    "WOOD COMP": {
        "macro_en": "WOOD COMPONENT",
        "Particolari": {
            "Ripiano Legno": ["WOODEN SHELF", {"Con mensole": "WITH BRACKET", "Con lati bordati": "WITH EDGED SIDES", "Con zoccolatura": "WITH PLINTH", "Con viteria": "WITH SCREWS", "Fresata": "MILLING"}, "SHELF"],
            "Schienale Legno": ["WOODEN BACK", {"Con mensole": "WITH BRACKET", "Con viteria": "WITH SCREWS", "Con lati bordati": "WITH EDGED SIDES"}, "PANEL"],
            "Cielino": ["WOODEN CANOPY", {"Con mensole": "WITH BRACKET", "Con viteria": "WITH SCREWS", "Dritto": "STRAIGHT", "Inclinato": "SLOPING", "Con finestra": "WITH WINDOW", "Stondato": "CURVED", "Centrale": "CENTRAL", "Con illuminazione": "WITH LIGHTING", "Con lati bordati": "WITH EDGED SIDES"}, "CANOPY"],
            "Zoccolatura": ["WOODEN PLINTH", {"Compatibilità piede di base (+)": "", "Con lati bordati": "WITH EDGED SIDES", "Con viteria": "WITH SCREWS"}, "PLINTH"],
            "Fiancata": ["WOODEN SIDE PANEL", {"Con mensole": "WITH BRACKET", "Sagomata": "SHAPED", "Con lati bordati": "WITH EDGED SIDES", "Con viteria": "WITH SCREWS", "Fresata": "MILLING"}, "SIDE PANEL"],
            "Copripiede": ["WOODEN FOOT-COVER", {"Compatibilità piede di base (+)": "", "Con lati bordati": "WITH EDGED SIDES", "Con viteria": "WITH SCREWS"}, "COVER"],
            "Coprimontante": ["WOODEN UPRIGHT-COVER", {"Minirack": "MINIRACK", "Con lati bordati": "WITH EDGED SIDES", "Con viteria": "WITH SCREWS"}, "COVER"],
            "Compensazione": ["WOODEN FILLER PIECE", {"Per Top legno": "FOR TOP SHELF"}, "SPACER"]
        }
    },
    "PLASTIC COMP": {
        "macro_en": "PLASTIC COMPONENT",
        "Particolari": {
            "Tappo": ["PLASTIC CAP", {}, "CAP"],
            "Guarnizione": ["GASKET", {}, "ACCESSORY"],
            "Cerniera": ["HINGE", {}, "ACCESSORY"],
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
            "Cancelletto": ["GLASS ARM", {"Orientamento": "", "Illuminato": "ILLUMINATED"}, "ARM"],
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
            "Totem": ["TOTEM", {"Mobile": "MOBILE", "Rotante": "ROTATING", "Per casse automatiche": "FOR SELF PAY"}, "DISPLAY"],
            "Spalla": ["FRAME", {"Antisismico": "SEISMIC-RESISTANT", "Sezione (+)": "", "Zincato": "GALVANIZED"}, "FRAME"],
            "Controventatura": ["CROSS-BRACING", {"Gondola": "GONDOLA", "Sezione (+)": "", "Su due livelli": "TWO LEVELS", "Numero diagonali (+)": "", "Con distanziale (+)": "WITH SPACER"}, "CROSS-BRACING"],
            "Banco espositore di legno": ["WOODEN DESK", {"Con cassetto": "WITH DRAWER", "Con ruote": "WITH WHEELS"}, "DESK"],
            "Avancassa": ["IMPULSE UNIT", {"Con ripiani": "WITH SHELF", "Con ripiani inclinati": "WITH INCLINATED SHELF", "Con rete divisoria": "WITH DIVIDING NET", "Con ruote": "WITH WHEELS", "Con ganci": "WITH HOOKS", "Con batticarrello": "WITH TROLLEY BEATER"}, "DISPLAY"],
            "Cassettiera": ["CHEST OF DRAWERS", {"Con guide RAM": "WITH RAM GUIDE", "Attacco montante": "HOOK ONTO UPRIGHT"}, "DRAWER"],
            "Espositore riviste": ["DISPLAY FOR MAGAZINE", {"Numero tasche (+)": "", "Con portaprezzo in filo": "WITH PRIZE-HOLDER WIRE"}, "DISPLAY", "BOOK AND MAGAZINE"],
        }
    }
}

OPZIONI_COMPATIBILITA = ["", "F25", "F25 BESPOKE", "F25 READY", "F50", "F50 BESPOKE", "F50 READY", "UNIVERSAL", "BC", "FORTISSIMO", "MINIRACK"]

MAPPA_NORMATIVE_FASTENER = {
    "Vite": {
        "": "",
        "DIN 912 - Testa cilindrica": "DIN 912",
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
    "SEMICIRCULAR", "SINGLE", "DOUBLE", "END", "L-SHAPED", "U-SHAPED", "SERRATED LOCK", "ROTATING", "CTR", "UPRIGHT-GRAFT"
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
# 3. INTERFACCIA UTENTE (Layout Verticale - Fix Multi-Tags)
# =========================================================

# --- INIZIALIZZAZIONE VARIABILI DI STATO (Per evitare NameError) ---
uni_en_1090_active = False 
mat_en = ""
part_en = ""
extra_dedicati_dict = {}
tag_suggerimento = ""
extra_selezionati = []
normativa = ""
comp_list_tags = []
blocco_incompatibilita = False  # Variabile per gestire il blocco del tasto finale

# Variabili di configurazione rapida
LARGHEZZA_IMMAGINE = 600 
TESTO_MANUALE = """
**PROCEDURA STANDARD:**
1. **CATEGORIA**: Seleziona il gruppo a sinistra.
2. **MODELLO**: Scegli tipologia materiale e la compatibilità (F25, Fortissimo, ecc.).
3. **PARTICOLARE**: Cerca il componente specifico e aggiungi le varie caratteristiche
4. **QUOTE**: Inserisci i valori in millimetri.
5. **GENERA**: Clicca il tasto rosso in fondo.

---
**NOTE TECNICHE:**
* I prefissi L-P-H sono automatici.
* Le note libere vengono tradotte in inglese.
* Lunghezza max stringa: 100 caratteri.
"""

st.title("⚙️ REG - Title Generator & Classification")

# --- 1. TASTO AZZERA SUPERIORE CENTRATO ---
c1, c2, c3 = st.columns([2, 1, 2])
with c2:
    st.button("🔄 AZZERA TUTTO", on_click=activate_reset, use_container_width=True, key="btn_top")

st.markdown("---")

# LAYOUT A 2 COLONNE PRINCIPALI: Sidebar (SX) | Area Lavoro (DX)
col_left, col_workarea = st.columns([1, 3], gap="large")

with col_left:
    st.subheader("📂 1. Categoria")
    macro_it = st.radio("Seleziona categoria:", options=list(DATABASE.keys()), key="radio_macro", label_visibility="collapsed")
    
    st.markdown("---")
    st.subheader("📖 Manuale d'uso")
    st.info(TESTO_MANUALE)

with col_workarea:
    st.subheader("🛠️ 2. Materiale e Compatibilità")
    
    # RIGA MATERIALE + COMPATIBILITÀ
    c_mat, c_comp = st.columns([1, 1.5])
    
    with c_mat:
        if macro_it == "ASSEMBLY":
            st.toggle("ASSEMBLATO", key="check_assembled")
        else:
            materiali_disponibili = MATERIALI_CONFIG.get(macro_it, {})
            if materiali_disponibili:
                mat_it = st.radio(f"Materiale:", options=list(materiali_disponibili.keys()), horizontal=True)
                mat_en = materiali_disponibili[mat_it]

    with c_comp:
        comp_selezionate = []
        if macro_it != "FASTENER":
            pills_compatibilita = [opt for opt in OPZIONI_COMPATIBILITA if opt]
            comp_selezionata = st.pills("Modello Compatibilità:", options=pills_compatibilita, selection_mode="single", key="comp_tags")
            comp_selezionate = [comp_selezionata] if comp_selezionata else []
            
            if any(m in comp_selezionate for m in ["FORTISSIMO", "MINIRACK"]):
                st.warning("⚡ Strutturale")
                uni_en_1090_active = st.checkbox("Certificazione UNI EN-1090", key="check_1090")
        else:
            comp_selezionate = []

    st.markdown("---")
    
    # SELEZIONE PARTICOLARE
    part_dict = DATABASE[macro_it]["Particolari"]
    def format_part_label(nome_it):
        if nome_it is None: return "Seleziona o digita il particolare..."
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
    
    if scelta_part_it:
        dati_part = part_dict[scelta_part_it]
        part_en = dati_part[0]
        extra_dedicati_dict = dati_part[1]
        
        if len(dati_part) > 2:
            tag_suggerimento = " - ".join(dati_part[2:]) 
        else:
            tag_suggerimento = ""
        
        extra_options = list(extra_dedicati_dict.keys())
        if extra_options:
            extra_selezionati = st.pills(f"Opzioni:", options=extra_options, selection_mode="multi", key="extra_tags")
            
            # ---------------------------------------------------------
            # LOGICA INTERSEZIONE (Fix Incompatibilità più di 2 parole)
            # ---------------------------------------------------------
            tags_attivi = set(extra_selezionati) if extra_selezionati else set()
            
            for gruppo in COPPIE_INCOMPATIBILI:
                intersezione = set(gruppo).intersection(tags_attivi)
                if len(intersezione) >= 2:
                    st.error(f"⚠️ **CONFLITTO:** Non puoi selezionare contemporaneamente: {', '.join(intersezione)}")
                    blocco_incompatibilita = True
            # ---------------------------------------------------------

            if extra_selezionati:
                for ex in extra_selezionati:
                    if ex in SUB_OPTIONS_CONFIG:
                        st.selectbox(f"↳ Variante {ex}:", options=list(SUB_OPTIONS_CONFIG[ex].keys()), key=f"sub_{ex}")
                    elif ex in EXTRA_CON_INPUT_MANUALE:
                        st.text_input(f"↳ Valore {ex}:", key=f"manual_{ex}")
        
        if tag_suggerimento:
            st.caption(f"🔍 Suggerimento Classificazione: **{tag_suggerimento}**")

    extra_libero = st.text_input("Note libere (IT):", key="extra_text").strip()

    st.markdown("---")
    st.subheader("📏 4. Dimensionamento e Normative")
    
    col_campi, col_immagine = st.columns([1, 1.5], gap="medium")

    with col_campi:
        if macro_it == "FASTENER":
            dim_l = st.text_input("Lunghezza (L)", key="dim_l")
            dim_dia = st.text_input("Diametro (D/M)", key="dim_dia")
            opzioni_norm = MAPPA_NORMATIVE_FASTENER.get(scelta_part_it, {"": ""})
            norma_scelta = st.selectbox("Normativa", options=list(opzioni_norm.keys()))
            normativa = opzioni_norm[norma_scelta] if norma_scelta else ""
            dim_p, dim_h, dim_s, dim_dia_gen = "", "", "", ""
        else:
            dim_l = st.text_input("Lunghezza (L)", key="dim_l")
            dim_p = st.text_input("Profondità (P)", key="dim_p")
            dim_h = st.text_input("Altezza (H)", key="dim_h")
            dim_dia_gen = st.text_input("Diametro (Ø)", key="dim_dia_gen")
            dim_s = "" 
            
    with col_immagine:
        st.image(
            "https://raw.githubusercontent.com/wAsp191/generatetext/main/Gemini_Generated_Image_rtac8jrtac8jrtac%20(1).png", 
            caption="Riferimento Quote", 
            width=LARGHEZZA_IMMAGINE
        )
    
# =========================================================
# 4. LOGICA DI GENERAZIONE E TRADUZIONE (v8.6 - Comma Fix)
# =========================================================

st.divider()

if 'stringa_editabile' not in st.session_state:
    st.session_state['stringa_editabile'] = ""

# --- CONTROLLO INCOMPATIBILITÀ (FILTRO SOFT) ---
errori_rilevati = []

# Se abbiamo delle extra selezionate, confrontiamole col database di esclusione
if extra_selezionati:
    for coppia in COPPIE_INCOMPATIBILI:
        # Se entrambi i termini della coppia "proibita" sono tra quelli selezionati:
        if coppia.issubset(set(extra_selezionati)):
            elementi = list(coppia)
            errori_rilevati.append(f"⚠️ **Incongruenza Tecnica:** Non puoi selezionare **'{elementi[0]}'** e **'{elementi[1]}'** contemporaneamente.")

# Se ci sono errori, mostriamo i banner rossi
for errore in errori_rilevati:
    st.error(errore)

# La variabile diventa True se c'è almeno un errore, disabilitando così il tasto
blocco_genera = len(errori_rilevati) > 0

# TASTO DI GENERAZIONE (Ora con il parametro disabled)
if st.button("🚀 GENERA STRINGA FINALE", use_container_width=True, disabled=blocco_genera):
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
            
            lph_str = " ".join(dim_final_parts)
            
            dim_final_comps = []
            if lph_str: dim_final_comps.append(lph_str)
            if dia_val_s: dim_final_comps.append(f"Ø{dia_val_s}")
            if s_val: dim_final_comps.append(f"S{s_val}")
            
            dim_final = " ".join(dim_final_comps)

        # --- B. Extra da Bottoni (Pills) - ORDINE FISSO ---
        extra_pills_list = []
        
        # Invece di: for ex in (extra_selezionati or []):
        # Usiamo l'ordine originale del database/options:
        ordine_fisso_opzioni = list(extra_dedicati_dict.keys())
        
        for ex in ordine_fisso_opzioni:
            if extra_selezionati and ex in extra_selezionati:
                base_trans = extra_dedicati_dict.get(ex, ex.upper())
                
                if ex in SUB_OPTIONS_CONFIG:
                    sub_key = f"sub_{ex}"
                    valore_sub_it = st.session_state.get(sub_key, "")
                    traduzione_sub = SUB_OPTIONS_CONFIG[ex].get(valore_sub_it, "")
                    extra_pills_list.append(f"{base_trans} {traduzione_sub}".strip())
                    
                elif ex in EXTRA_CON_INPUT_MANUALE:
                    manual_val = st.session_state.get(f"manual_{ex}", "").strip().upper()
                    if manual_val: 
                        extra_pills_list.append(f"{base_trans} {manual_val}")
                    else: 
                        extra_pills_list.append(base_trans)
                else:
                    extra_pills_list.append(base_trans)

        # --- C. Note Libere (Traduzione) ---
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

        # --- D. Ordinamento Prefissi/Suffissi Pills ---
        prefissi = [ex for ex in extra_pills_list if ex in TERMINI_ANTICIPATI]
        suffissi = [ex for ex in extra_pills_list if ex not in prefissi]
        
        prefix_str = " ".join(prefissi) if prefissi else ""
        extra_suffissi_str = " ".join(suffissi) if suffissi else "" # Spazio tra extra
        
        comp_list = [c for c in (comp_selezionate or []) if c.strip()]
        comp_str = " - ".join(comp_list) if comp_list else ""

        # --- E. Assemblaggio (LOGICA RICHIESTA) ---
        
        # 1. Base Descrizione (Materiale + Prefisso + Nome + Misure)
        if mat_en == "METAL" and "METAL" in part_en.upper():
            corpo = f"{prefix_str} {part_en} {dim_final}".strip()
        else:
            corpo = f"{mat_en} {prefix_str} {part_en} {dim_final}".strip()
        
        # 2. Aggiunta Extra (Pills) uniti da spazio (come richiesto in esempio)
        if extra_suffissi_str:
            corpo = f"{corpo} {extra_suffissi_str}".strip()
            
        # 3. Aggiunta Note Libere precedute da VIRGOLA
        if note_libere_tradotte:
            corpo = f"{corpo}, {note_libere_tradotte}".strip()
        
        # 4. Unione finale con il MODELLO tramite TRATTINO
        final_segments = [corpo]
        if comp_str:
            final_segments.append(comp_str)

        temp_str = " - ".join(final_segments).upper().replace("  ", " ")
        
        # 5. Pulizia finale "WITH" e prefissi speciali
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
    
    # --- LOGICA VISUALIZZAZIONE CLASSIFICAZIONE ---
    all_tags = []
    
    # 1. Aggiungiamo i tag dal database (quelli estratti con il ".join" di prima)
    if 'tag_suggerimento' in locals() and tag_suggerimento:
        all_tags.append(tag_suggerimento.upper())
    
    # 2. Aggiungiamo la compatibilità (F25, ecc.)
    all_tags.extend([c.upper() for c in comp_list_tags])
    
    # 3. Aggiungiamo certificazioni e normative
    if uni_en_1090_active:
        all_tags.append("UNI EN-1090-1")
    if 'normativa' in locals() and normativa:
        all_tags.append(normativa.upper())
    
    # 4. Visualizzazione finale con la nuova dicitura
    if all_tags:
        st.info(f"🔍 **CLASSIFY:** {' | '.join(all_tags)}")

# --- 2. TASTO AZZERA INFERIORE CENTRATO ---
st.markdown("<br>", unsafe_allow_html=True)
cb1, cb2, cb3 = st.columns([2, 1, 2])
with cb2:
    st.button("🔄 AZZERA TUTTO", on_click=activate_reset, use_container_width=True, key="btn_bottom")
