import streamlit as st
from deep_translator import GoogleTranslator

# =========================================================
# 0. CONFIGURAZIONE PAGINA E LOGICA RESET
# =========================================================

# Spostiamo set_page_config come primissima istruzione per evitare errori
st.set_page_config(page_title="Technical Generator v8.7", layout="wide")

# CSS per compattare l'interfaccia
st.markdown("""
    <style>
        /* 1. Riduciamo il padding superiore della pagina */
        .block-container {
            padding-top: 3.0rem !important;
            padding-bottom: 0rem !important;
        }

        /* 2. Compattiamo lo spazio tra ogni elemento (widget) */
        [data-testid="stVerticalBlock"] > div {
            flex-direction: column;
            gap: 0.15rem !important; /* Riduce il buco tra un widget e l'altro */
        }

        /* 3. Riduciamo l'altezza dei titoli */
        h1 { margin-bottom: -1rem !important; font-size: 1.6rem !important; }
        h2 { margin-bottom: -0.8rem !important; font-size: 1.2rem !important; }
        h3 { margin-bottom: -0.5rem !important; font-size: 1.0rem !important; }

        /* 4. Compattiamo i divisori (st.divider / st.markdown("---")) */
        hr {
            margin-top: 0.4rem !important;
            margin-bottom: 0.4rem !important;
        }

        /* 5. Trick per ridurre lo spazio sotto le label dei widget */
        .st-emotion-cache-1p3m0jg {
            margin-bottom: -0.8rem !important;
        }

        /* 6. Riduciamo lo spazio interno ai widget (Selectbox, Text Input) */
        div[data-baseweb="select"] > div, 
        div[data-testid="stTextInput"] > div > div > input {
            padding-top: 0px !important;
            padding-bottom: 0px !important;
            min-height: 1.6rem !important;
        }
        
        /* 7. Nascondiamo lo spazio extra dei Pills */
        [data-testid="stPills"] {
            margin-top: -0.5rem !important;
        }
        /* 8. Ingrandimento scritte Categorie (st.radio) */
        [data-testid="stWidgetLabel"] p {
            font-size: 1.6rem !important; /* Ingrandisce la label del widget */
            font-weight: 700 !important;
        }

        [data-testid="stMarkdownContainer"] p {
            font-size: 1.2rem !important; /* Ingrandisce le opzioni del radio (Metal Comp, etc) */
        }
        
        /* Ottimizzazione spazio tra le opzioni del radio per non farle accavallare */
        [data-testid="stAudioRadio"] div {
            gap: 0.5rem !important;
        }

        /* 9. Distanziamento verticale tra le opzioni del Radio (Categorie) */
        div[data-testid="stRadio"] div[role="radiogroup"] label {
            margin-bottom: 12px !important; /* Aggiunge spazio sotto ogni categoria */
            padding: 5px 0px !important;    /* Dà un po' di respiro interno */
            transition: all 0.2s ease;      /* Effetto fluido al passaggio del mouse */
        }

        /* Opzionale: un leggero effetto hover per capire cosa stiamo selezionando */
        div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# CONTROLLO TOAST: Eseguito ad ogni ricaricamento
if st.session_state.get('reset_eseguito'):
    st.toast("Interfaccia pulita!", icon="✨")
    st.session_state['reset_eseguito'] = False

# --- LOGICA DI RESET OTTIMIZZATA ---
def activate_reset():
    """
    Reset centralizzato dello stato. 
    Nota: Non chiamiamo st.rerun() qui perché usata come callback 'on_click',
    evitando l'avviso 'no-op'.
    """
    
    # 1. Valori di default
    defaults = {
        'comp_tags': None,
        'selectbox_part': None,
        'extra_tags': [],
        'check_1090': False,
        'check_assembled': False,
        'stringa_stabile': "",
        'tags_stabili': []
    }

    text_keys = [
        'dim_l', 'dim_l_gen', 'dim_p', 'dim_h', 
        'dim_dia', 'dim_dia_gen', 'dim_s', 'extra_text', 
        'stringa_editabile', 'input_manuale'
    ]

    # 2. Esecuzione Reset Session State
    for key, val in defaults.items():
        st.session_state[key] = val
        
    for key in text_keys:
        if key in st.session_state:
            st.session_state[key] = ""

    # 3. Pulizia chiavi dinamiche
    for key in list(st.session_state.keys()):
        if key.startswith(("manual_", "sub_")):
            del st.session_state[key]

    # 4. Flag per attivare il toast al termine del refresh automatico
    st.session_state['reset_eseguito'] = True
    
# =========================================================
# 1. DIZIONARI E DATABASE (OTTIMIZZATO)
# =========================================================

# --- REGOLE DI INCOMPATIBILITÀ (FILTRO SOFT) ---
# Gruppi di opzioni che non possono coesistere. 
COPPIE_INCOMPATIBILI = [
    {"Statico", "Antisismico"}, {"Angolo aperto", "Angolo chiuso"},
    {"Portante", "Non portante"}, {"Singolo", "Doppio"},
    {"Per ripiano in vetro", "Per ripiano in legno"}, {"Con serratura", "Senza serratura"},
    {"Passo 25", "Passo 50"}, {"L50", "L55"}, {"Scorrevoli", "A saracinesca"},
    {"Per attacco montante", "Per attacco fiancata"}, {"Superiore", "Tra ripiani di base"},
    {"Dritto", "Inclinato"}, {"Cromato", "Verniciato"},
    {"Multibarra", "Multilame", "In rete"}, {"Profilo a L", "Profilo a U"},
    {"Per ripiano di base", "Per fiancata"}, {"Terminale", "Centrale"},
    {"Liscio", "Liscia", "Forato", "Forata", "In filo"}, {"Zincato", "Verniciata"}
]

# --- TRADUZIONI FISSE ---
GLOSSARIO_TECNICO = {
    "mensola": "BRACKET", "mensole": "BRACKETS", "gondola": "GONDOLA",
    "spalla": "FRAME", "innesto": "COUPLING", "montante": "UPRIGHT",
    "per": "FOR", "losanga": "LOSANGA"
}

# --- CONFIGURAZIONE SOTTO-OPZIONI (+) ---
SUB_OPTIONS_CONFIG = {
    "VPA (+)": {
        "Serie S": "S SERIES", "Serie SS": "SS SERIES", 
        "Serie M": "M SERIES", "Serie L": "L SERIES"
    },
    "Con distanziale (+)": {
        "L100": "L100", "L150": "L150", "L200": "L200", "L250": "L250"
    },
    "Numero diagonali (+)": {
        "Doppie": "DD", "Triple": "TD", "Quadruple": "QD"
    },
    "Sezione (+)": {
        "L55": "L55", "L80 Z/S": "L80 Z/S", "L80 Z/M": "L80 Z/M", 
        "L100 Z/S": "L100 Z/S", "L100 Z/M": "L100 Z/M", "L120 Z/S": "L120 Z/S", 
        "70X30": "70X30", "90X30": "90X30"
    },
    "Tipologia di mensola (+)": {
        "Mensola saldata a filo superiore": "UPPER BRACKET", 
        "Mensola saldata a filo inferiore": "LOWER BRACKET"
    },
    "Compatibilità piede di base (+)": {
        "Per piede H90": "FOR H90 BASE FOOT", 
        "Per piede H100": "FOR H100 BASE FOOT", 
        "Per piede H150": "FOR H150 BASE FOOT"
    },
    "Attacco gancio (+)": {
        "Attacco barra": "HOOK FOR BAR", 
        "Attacco multilame": "HOOK FOR MULTISTRIP", 
        "Attacco pannello forato": "HOOK FOR SLOTTED PANEL"
    },
    "Orientamento (+)": {"Destra": "RIGHT", "Sinistra": "LEFT"},
    "Posizioni multiple (+)": {
        "1 posizione": "1 POSITION", "2 posizioni": "2 POSITIONS", "3 posizioni": "3 POSITIONS"
    },
    "Altezza piede (+)": {"H90": "H90", "H100": "H100", "H150": "H150"},
    "Predisposto per montante (+)": {
        "L80": "FOR L80 UPRIGHT", "L100/L120": "FOR L100/L120 UPRIGHT"
    },
    "Numero tasche (+)": {"1 Tasca": "1 POCKET", "2 Tasche": "2 POCKETS"},
    "Numero gradoni (+)": {"1 gradone": "1 STEP", "2 gradoni": "2 STEPS", "3 gradoni": "3 STEPS"},
    "Asimmetrica (+)": {"AS240": "AS240", "AS340": "AS340", "AS440": "AS440"}
}

EXTRA_CON_INPUT_MANUALE = ["Sezione circolare", "Sezione quadrata"]

# --- CONFIGURAZIONE MATERIALI ---
MATERIALI_CONFIG = {
    "METAL COMP": {"METAL": "METAL", "ZINCATO": "GALVANIZED", "INOX": "STAINLESS STEEL", "ALLUMINIO": "ALUMINIUM"},
    "WOOD COMP": {"LAMINATO": "LAMINATED", "NOBILITATO": "MELAMINE", "TRUCIOLARE": "OSB"},
    "PLASTIC COMP": {"PLX": "PLX", "POLICARBONATO": "POLYCARBONATE", "PVC": "PVC", "GOMMA": "RUBBER"},
    "GLASS COMP": {"VETRO TEMPRATO": "TEMPERED", "VETRO SATINATO": "SATIN"},
    "FASTENER": {"NERO": "", "ZINCATO": "GALVANIZED", "BRUNITO": "BURNISHED"}
}

# --- DATABASE COMPONENTI ---
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
            "Mensola": ["BRACKET", {"Orientamento (+)": "", "Posizioni multiple (+)": "", "Antisgancio": "ANTI-RELEASE", "Rinforzata": "REINFORCED", "Nervata": "RIBBED", "Per ripiano in vetro": "FOR GLASS SHELF", "Per ripiano in legno": "FOR WOODEN SHELF", "A pinza": "GRIPPED", "Minirack": "FOR MINIRACK"}, "BRACKET"],
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
            "Pannello frontale": ["FRONT PANEL", {"Forato": "PERFORATED", "Aggangio montante": "HOOK ONTO UPRIGHT"}, "PANEL"],
            "Adattatore": ["ADAPTER", {"Forato": "PERFORATED", "Aggangio montante": "HOOK ONTO UPRIGHT", "Passo 25": "PITCH 25", "Passo 50": "PITCH 50", "L50": "L50", "L55": "L55"}, "ADAPTER"],
            "Canalina passa cavi": ["CABLE TRAY", {"Forato": "PERFORATED", "Con viteria": "WITH SCREWS"}, "ESA"],
            "Protezione": ["PROTECTION FOR PERFORATED SHELF", {"Con piega frontale": "WITH DOWNWARD"}, "PROTECTION"]
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
            "Compensazione": ["WOODEN FILLER PIECE", {"Per Top legno": "FOR TOP SHELF"}, "SPACER"],
            "Mobiletto in legno": ["WOODEN CABINET", {"Sagomato": "SHAPED"}, "CABINET"]
        }
    },
    "PLASTIC COMP": {
        "macro_en": "PLASTIC COMPONENT",
        "Particolari": {
            "Tappo": ["PLASTIC CAP", {}, "CAP"],
            "Guarnizione": ["GASKET", {}, "ACCESSORY"],
            "Cerniera": ["HINGE", {}, "ACCESSORY"],
            "Divisorio": ["DIVIDER", {"Inclinato": "SLOPING", "Per ripiano": "FOR SHELF"}, "DIVIDER"],
            "Frontalino": ["RISER", {"Per ripiano": "FOR SHELF", "Trasparente": "TRASPARENT"}, "RISER"],
            "Pannello": ["PANEL", {"Forato": "PERFORATED", "Trasparente": "TRASPARENT", "Bordi smussati": "CHAMFERED EDGES"}, "PANEL"],
            "Portaprezzo": ["TICKET-HOLDER", {"Trasparente": "TRASPARENT", "Colorato": "COLOURED", "Con tasca oscillante": "WITH LIFT-UP POCKET", "Adesivo": "ADHESIVE", "Con asola centrale": "WITH CENTRAL SLOT"}, "TICKET-HOLDER"]
        }
    },
    "GLASS COMP": {
        "macro_en": "GLASS COMPONENT",
        "Particolari": {
            "Ripiano": ["GLASS SHELF", {}, "SHELF"],
            "Anta": ["GLASS DOOR", {"Orientamento (+)": "", "Con foro serratura": "WITH LOCK HOLE", "Scorrevole": "SLIDING"}, "DOOR"],
            "Cancelletto": ["GLASS ARM", {"Orientamento (+)": "", "Illuminato": "ILLUMINATED"}, "ARM"],
        }
    },
    "FASTENER": {
        "macro_en": "FASTENER",
        "Particolari": {
            "Vite": ["SCREW", {"Autoperforanti": "SELF-DRILLING", "Testa svasata": "COUNTERSUNK HEAD", "Testa esagonale": "HEX HEAD", "Testa a croce": "CROSS HEAD", "Testa esagono incassato": "HEXAGON SOCKET HEAD", "Testa Bombata": "T-BOM"}, "SCREW"],
            "Bullone": ["BOLT", {}, "FASTENER"],
            "Rondella": ["WASHER", {"Dentellata": "SERRATED LOCK", "Fascia Larga": "WIDE BAND", "Elastica": "GROWER"}, "WASHER"],
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
            "Spalla": ["FRAME", {"Numero diagonali (+)": "", "Antisismico": "SEISMIC-RESISTANT", "Sezione (+)": "", "Zincato": "GALVANIZED", "Verniciata": "POWDER COATED", "Asimmetrica (+)": ""}, "FRAME"],
            "Controventatura": ["CROSS-BRACING", {"Gondola": "GONDOLA", "Sezione (+)": "", "Su due livelli": "TWO LEVELS", "Numero diagonali (+)": "", "Con distanziale (+)": "WITH SPACER"}, "CROSS-BRACING"],
            "Banco espositore di legno": ["WOODEN DESK", {"Con cassetto": "WITH DRAWER", "Con ruote": "WITH WHEELS"}, "DESK"],
            "Avancassa": ["IMPULSE UNIT", {"Con ripiani": "WITH SHELF", "Con ripiani inclinati": "WITH INCLINATED SHELF", "Con rete divisoria": "WITH DIVIDING NET", "Con ruote": "WITH WHEELS", "Con ganci": "WITH HOOKS", "Con batticarrello": "WITH TROLLEY BEATER"}, "DISPLAY"],
            "Cassettiera": ["CHEST OF DRAWERS", {"Con guide RAM": "WITH RAM GUIDE", "Attacco montante": "HOOK ONTO UPRIGHT"}, "DRAWER"],
            "Espositore riviste": ["DISPLAY FOR MAGAZINE", {"Numero tasche (+)": "", "Con portaprezzo in filo": "WITH PRICE-HOLDER WIRE"}, "DISPLAY", "BOOK AND MAGAZINE"],
            "Cassa pagamento automatico": ["SELF CHECKOUT", {"Con macchine di pagamento": "WITH GLORY MACHINES PAYMENT"}, "SELF CHECKOUT (SCO)"],
            "Espositore a gradoni": ["STEPLADDER DISPLAY", {"Numero gradoni (+)": ""}, "DISPLAY"]
        }
    }
}

OPZIONI_COMPATIBILITA = ["", "F25", "F25 BESPOKE", "F25 READY", "F50", "F50 BESPOKE", "F50 READY", "UNIVERSAL", "BC", "FORTISSIMO", "MINIRACK", "UNIMOB"]

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

# OPZIONI_SPESSORE_STD = ["", "0.5", "0.6", "0.75", "0.8", "1", "1.2", "1.5", "2", "2.5", "3", "3.5", "4", "4.5", "5", "6", "8", "10"]
# OPZIONI_SPESSORE_WOOD = ["", "10mm", "15mm", "18mm", "19mm", "20mm", "22mm", "24mm", "25mm", "30mm", "35mm"]

TERMINI_ANTICIPATI = [
    "CENTRAL", "LEFT", "RIGHT", "REINFORCED", "INTERNAL", "EXTERNAL", "STATIC", "ADJUSTABLE", "SEISMIC",
    "MULTIBAR", "MULTISTRIP", "TOP", "INTER-BASE SHELF", "ROUNDED", "SLOPING", "SHAPED", "CONNECTING", "SHUTTER", "COUPLING",
    "WIRE", "GRIPPED", "CHROMED", "PAINTED", "MESH", "SLIDING", "CURVED", "STRAIGHT", "MILLING", "WIRE-BASKET",
    "SEMICIRCULAR", "SINGLE", "DOUBLE", "END", "L-SHAPED", "U-SHAPED", "SERRATED LOCK", "ROTATING", "CTR", "UPRIGHT-GRAFT"
]

# =========================================================
# 2. INTERFACCIA UTENTE (Layout & Logica)
# =========================================================

# --- INIZIALIZZAZIONE VARIABILI DI STATO ---
if "mat_en" not in st.session_state: 
    st.session_state.mat_en = ""

# Configurazione visuale
LARGHEZZA_IMMAGINE = 600 
TESTO_MANUALE = """
<div style="font-family: sans-serif; font-size: 14px; line-height: 1.6;">
    <p><b>PROCEDURA STANDARD:</b></p>
    <ul>
        <li>📁 <b>CATEGORIA</b>: Seleziona la tipologia a sinistra.</li>
        <li>🛠️ <b>CONFIGURAZIONE</b>: Scegli materiale e componente.</li>
        <li>✨ <b>EXTRA</b>: Seleziona i dettagli e aggiungi note.</li>
        <li>📏 <b>MISURE</b>: Inserisci dimensioni e normative.</li>
        <li>🔗 <b>COMPATIBILITÀ</b>: Scegli il modello di destinazione.</li>
        <li>🚀 <b>GENERA</b>: Clicca il tasto per creare la stringa.</li>
    </ul>
</div>
"""

# --- HEADER ---
col_t, col_m, col_r = st.columns([2.5, 1.5, 1], vertical_alignment="bottom")
with col_t: 
    st.title("⚙️ REG - Title Generator")
with col_m:
    with st.expander("📖 Manuale d'uso"):
        st.markdown(f'<div style="font-size: 14px;">{TESTO_MANUALE}</div>', unsafe_allow_html=True)
with col_r: 
    # Colleghiamo direttamente la funzione del Modulo 0 come callback
    st.button("🔄 AZZERA", on_click=activate_reset, use_container_width=True)

st.markdown("---")

col_left, col_workarea = st.columns([1, 4], gap="large")

with col_left:
    st.subheader("📂 1. Categoria")
    mappa_estetica = {
        "METAL COMP": "⚙️ METAL COMP", 
        "WOOD COMP": "🪵 WOOD COMP", 
        "PLASTIC COMP": "🧪 PLASTIC COMP", 
        "GLASS COMP": "🧊 GLASS COMP", 
        "FASTENER": "🔩 FASTENER", 
        "ASSEMBLY": "🏛️ ASSEMBLY"
    }
    macro_it = st.radio(
        "Seleziona categoria:", 
        options=list(DATABASE.keys()), 
        format_func=lambda x: mappa_estetica.get(x, x), 
        key="radio_macro", 
        label_visibility="collapsed"
    )

with col_workarea:
    st.subheader("🛠️ 2. Configurazione Base")
    c_mat, c_search = st.columns([1, 1.5])
    
    with c_mat:
        if "ASSEMBLY" in macro_it.upper(): 
            # MODIFICA: Gestiamo solo il toggle. 
            # mat_en viene resettato per evitare che "ASSEMBLY" entri come stringa fissa
            st.toggle("ASSEMBLATO", key="check_assembled")
            st.session_state.mat_en = "" 
        else:
            materiali_disponibili = MATERIALI_CONFIG.get(macro_it, {})
            if materiali_disponibili:
                mat_it = st.radio("Materiale:", options=list(materiali_disponibili.keys()), horizontal=True, key="mat_radio")
                temp_mat_en = materiali_disponibili[mat_it]
                
                if mat_it.upper() == "ZINCATO":
                    tipo_zinc = st.radio("Tipo zincatura:", ["A FREDDO (Zinc Plated)", "A CALDO (Galvanized)"], horizontal=True, key="zinc_type_radio")
                    st.session_state.mat_en = "ZINC PLATED" if "A FREDDO" in tipo_zinc else "GALVANIZED"
                else:
                    st.session_state.mat_en = temp_mat_en

    with c_search:
        part_info = DATABASE.get(macro_it, {}).get("Particolari", {})
        scelta_part_it = st.selectbox(
            "Cerca dettaglio:", 
            options=sorted(list(part_info.keys())), 
            index=None, 
            placeholder="Cerca componente...", 
            format_func=lambda x: f"🔧 {x} ({part_info[x][0]})" if x else "Seleziona...", 
            key="selectbox_part"
        )

    st.markdown("---")
    
    # --- SEZIONE 3: EXTRA E NOTE ---
    st.subheader("✨ 3. Extra e Note")
    st.session_state.conflitto_attivo = False 

    if scelta_part_it:
        dati_part = part_info.get(scelta_part_it, ["", {}, ""])
        extra_options = list(dati_part[1].keys())
        
        if extra_options:
            st.pills("Caratteristiche:", options=extra_options, selection_mode="multi", key="extra_tags")
            
            tags_scelti_raw = st.session_state.get("extra_tags", [])
            tags_scelti_upper = [str(t).upper().strip() for t in tags_scelti_raw]
            
            conflitto_rilevato = False
            messaggio_errore = ""

            for gruppo in COPPIE_INCOMPATIBILI:
                gruppo_upper = [str(elemento).upper().strip() for elemento in gruppo]
                intersezione = set(gruppo_upper).intersection(set(tags_scelti_upper))
                
                if len(intersezione) > 1:
                    conflitto_rilevato = True
                    st.session_state.conflitto_attivo = True 
                    nomi_originali = [t for t in tags_scelti_raw if str(t).upper().strip() in intersezione]
                    messaggio_errore = f"⚠️ **Incompatibilità**: Non puoi selezionare contemporaneamente **{', '.join(nomi_originali)}**."
                    break
            
            if conflitto_rilevato:
                st.error(messaggio_errore)
            
            for ex in tags_scelti_raw:
                col_indent, col_input = st.columns([0.1, 0.9])
                with col_input:
                    if ex in SUB_OPTIONS_CONFIG:
                        st.selectbox(f"Dettaglio per {ex}:", options=list(SUB_OPTIONS_CONFIG[ex].keys()), key=f"sub_{ex}")
                    elif ex in EXTRA_CON_INPUT_MANUALE:
                        st.text_input(f"Specifica valore per {ex}:", key=f"manual_{ex}")

    st.text_input(
        "Note libere (Traduzione automatica):", 
        key="extra_text", 
        placeholder="es: con tappi in gomma...",
        help="Il testo inserito verrà tradotto in inglese nel risultato finale."
    )
    
    st.markdown("---")
    
    # --- SEZIONE 4: DIMENSIONAMENTO ---
    st.subheader("📏 4. Dimensionamento")

    # Inizializzazione sicura chiavi
    for k in ["dim_l", "dim_dia", "dim_l_gen", "dim_p", "dim_h", "dim_dia_gen"]:
        if k not in st.session_state:
            st.session_state[k] = ""

    if macro_it == "FASTENER":
        c1, c2, c3, _ = st.columns([1, 1, 2, 2])
        with c1: 
            st.text_input("L", key="dim_l", placeholder="Lung.")
        with c2: 
            st.text_input("D/M", key="dim_dia", placeholder="Diam.")
        with c3: 
            opzioni_norm = MAPPA_NORMATIVE_FASTENER.get(scelta_part_it, {"": ""})
            st.selectbox("Normativa", options=list(opzioni_norm.keys()), key="norm_select")
    else:
        c1, c2, c3, c4, _ = st.columns([1, 1, 1, 1, 1])
        with c1: 
            st.text_input("L", key="dim_l_gen", placeholder="Lung.")
        with c2: 
            st.text_input("P", key="dim_p", placeholder="Prof.")
        with c3: 
            st.text_input("H", key="dim_h", placeholder="Alt.")
        with c4: 
            st.text_input("Ø", key="dim_dia_gen", placeholder="Diam.")

    st.markdown("---")
    
    # --- SEZIONE 5: COMPATIBILITÀ ---
    st.subheader("🔗 5. Compatibilità")
    c_pills, c_check = st.columns([3, 1], vertical_alignment="center")
    
    with c_pills:
        if macro_it != "FASTENER":
            st.pills("Modello di destinazione:", options=OPZIONI_COMPATIBILITA, selection_mode="single", key="comp_tags", label_visibility="collapsed")
        else:
            st.info("Nessuna compatibilità necessaria per i Fastener.")
            
    with c_check:
        if st.session_state.get("comp_tags") in ["FORTISSIMO", "MINIRACK"]:
            st.checkbox("Cert. 1090", key="check_1090")
            
# =========================================================
# 3. LOGICA DI GENERAZIONE (MOTORE DI CALCOLO)
# =========================================================
st.divider()

# 1. Funzione di traduzione note con Glossario Tecnico
from deep_translator import GoogleTranslator

def traduci_note(testo):
    if not testo: return ""
    
    # GLOSSARIO FORZATO (Termini tecnici specifici)
    GLOSSARIO_TECNICO = {
        "mensola": "BRACKET", 
        "mensole": "BRACKETS", 
        "gondola": "GONDOLA",
        "spalla": "FRAME", 
        "innesto": "COUPLING", 
        "montante": "UPRIGHT",
        "per": "FOR", 
        "losanga": "LOSANGA",
        "rivestimento": "BACK PANEL"
    }
    
    testo_elaborato = testo.lower().strip()
    
    # Sostituzione forzata termini del glossario
    for it, en in GLOSSARIO_TECNICO.items():
        if it in testo_elaborato:
            testo_elaborato = testo_elaborato.replace(it, en)
            
    try:
        # Il traduttore riceve il testo con i termini tecnici già in inglese
        traduzione = GoogleTranslator(source='it', target='en').translate(testo_elaborato)
        return traduzione.upper()
    except:
        return testo_elaborato.upper()

# --- LOGICA DI CONTROLLO INCOMPATIBILITÀ ---
tags_scelti_raw = st.session_state.get("extra_tags", [])
tags_scelti_upper = [str(t).upper().strip() for t in tags_scelti_raw]
conflitto_rilevato = False
messaggio_errore = ""

for gruppo in COPPIE_INCOMPATIBILI:
    gruppo_upper = [str(elemento).upper().strip() for elemento in gruppo]
    intersezione = set(gruppo_upper).intersection(set(tags_scelti_upper))
    if len(intersezione) > 1:
        conflitto_rilevato = True
        nomi_originali = [t for t in tags_scelti_raw if str(t).upper().strip() in intersezione]
        messaggio_errore = f"⚠️ **Conflitto rilevato**: Non puoi combinare **{', '.join(nomi_originali)}**."
        break

if conflitto_rilevato:
    st.error(messaggio_errore)

# 2. TASTO GENERA
if st.button("🚀 GENERA STRINGA FINALE", use_container_width=True, disabled=conflitto_rilevato):
    
    macro_it = st.session_state.get("radio_macro", "")
    scelta_part_it = st.session_state.get("selectbox_part", "")
    mat_en = st.session_state.get("mat_en", "").upper()
    
    if scelta_part_it:
        part_db = DATABASE.get(macro_it, {}).get("Particolari", {}).get(scelta_part_it, ["", {}, ""])
        part_en = part_db[0].upper()
        dict_extra_db = part_db[1]
        tag_reale_db = part_db[2] if len(part_db) > 2 else ""

        # --- B. GESTIONE EXTRA E AGGETTIVI ---
        lista_prima = []
        lista_dopo = []
        
        for tag in tags_scelti_raw:
            if tag in SUB_OPTIONS_CONFIG:
                chiave_sub = st.session_state.get(f"sub_{tag}", "")
                traduzione = SUB_OPTIONS_CONFIG[tag].get(chiave_sub, chiave_sub).upper()
            elif tag in EXTRA_CON_INPUT_MANUALE:
                traduzione = st.session_state.get(f"manual_{tag}", "").upper()
            else:
                traduzione = dict_extra_db.get(tag, tag).upper()
            
            if traduzione in TERMINI_ANTICIPATI:
                lista_prima.append(traduzione)
            else:
                lista_dopo.append(traduzione)

        # --- C. DIMENSIONI ---
        dim_list = []
        
        L = st.session_state.get("dim_l", "").strip() or st.session_state.get("dim_l_gen", "").strip()
        P = st.session_state.get("dim_p", "").strip()
        H = st.session_state.get("dim_h", "").strip()
        D = st.session_state.get("dim_dia", "").strip() or st.session_state.get("dim_dia_gen", "").strip()

        if L: dim_list.append(f"L{L.upper()}")
        if P: dim_list.append(f"P{P.upper()}")
        if H: dim_list.append(f"H{H.upper()}")
        if D:
            prefix_d = "M" if (macro_it == "FASTENER" and not D.upper().startswith("M")) else "Ø"
            dim_list.append(f"{prefix_d}{D.upper()}")
        
        dim_str = " ".join(dim_list)
        
        norma_sel = st.session_state.get("norm_select", "")
        norma_str = MAPPA_NORMATIVE_FASTENER.get(scelta_part_it, {}).get(norma_sel, "")

        # --- D. TRADUZIONE NOTE ---
        note_it = st.session_state.get("extra_text", "").strip()
        note_en = traduci_note(note_it)

        # --- E. ASSEMBLAGGIO FINALE (Logica Anti-Rifuso Infallibile) ---
        
        # 1. Recupero Prefisso Base
        if macro_it == "ASSEMBLY":
            prefix_base = "ASSEMBLED" if st.session_state.get("check_assembled") else ""
        else:
            prefix_base = mat_en  # Es: "METAL"

        # 2. Costruzione Prefisso Completo (Materiale + Aggettivi come HEAVY DUTY)
        elementi_prefisso = [prefix_base] + lista_prima
        # Pulizia da stringhe vuote e normalizzazione
        prefisso_lista = [p.strip().upper() for p in elementi_prefisso if p.strip()]
        prefix_completo = " ".join(prefisso_lista)
        
        # 3. Normalizzazione Nome Componente
        part_en_upper = part_en.strip().upper()
        
        # --- LOGICA DI CONFRONTO AVANZATA ---
        # Creiamo dei set di parole per vedere se il prefisso è ridondante
        parole_prefisso = set(prefix_completo.split())
        parole_componente = set(part_en_upper.split())

        # Se il prefisso è già interamente contenuto nel nome del componente (es: METAL in SHEET METAL)
        # O se il componente inizia esattamente con quel prefisso
        if parole_prefisso and (parole_prefisso.issubset(parole_componente) or part_en_upper.startswith(prefix_completo)):
            core = part_en_upper
        else:
            core = f"{prefix_completo} {part_en_upper}".strip()
        
        # --- COSTRUZIONE RESTO DELLA STRINGA ---
        info_aggiuntive = []
        if lista_dopo: info_aggiuntive.append(" ".join(lista_dopo))
        if dim_str: info_aggiuntive.append(dim_str)
        if norma_str: info_aggiuntive.append(norma_str)
        
        corpo = f"{core} {' '.join(info_aggiuntive)}".strip()
        
        if note_en:
            corpo = f"{corpo}, {note_en}"
            
        comp_tag = st.session_state.get("comp_tags", "")
        if comp_tag:
            corpo = f"{corpo} - {comp_tag}"
            
        if st.session_state.get("check_1090"):
            corpo += " (UNI EN 1090-2)"

        # --- F. SALVATAGGIO ---
        # Join/Split finale per eliminare ogni doppio spazio residuo
        st.session_state['stringa_stabile'] = " ".join(corpo.split()).upper()
        
# =========================================================
# 4. OUTPUT E MONITORAGGIO (VERSIONE DEFINITIVA COMPATTA)
# =========================================================

# Funzione di callback per sincronizzare l'input manuale con lo stato globale
def sincronizza_modifica():
    if 'input_manuale' in st.session_state:
        # Aggiorniamo la stringa principale con quella modificata a mano
        st.session_state['stringa_stabile'] = st.session_state['input_manuale'].upper()

# Contenitore principale: garantisce che l'interfaccia non "salti"
risultato_container = st.container()

# Verifichiamo se esiste una stringa generata dal Modulo 3
if st.session_state.get('stringa_stabile'):
    with risultato_container:
        st.markdown("---")
        
        # 1. LAYOUT CONTROLLI (Header + Toggle Modifica)
        col_titolo, col_opt = st.columns([4, 1])
        with col_titolo:
            st.subheader("📋 Risultato Finale")
        
        modifica_attiva = col_opt.toggle("✏️ Modifica", key="toggle_manual_edit")

        # 2. AREA RISULTATO
        if modifica_attiva:
            # FIX: Usiamo una chiave statica e la logica on_change 
            # per mantenere la modifica persistente
            st.text_input(
                "Modifica manuale stringa:", 
                value=st.session_state['stringa_stabile'],
                key="input_manuale",
                on_change=sincronizza_modifica,
                label_visibility="collapsed"
            )
        else:
            # Visualizzazione Standard con tasto COPIA
            st.code(st.session_state['stringa_stabile'], language=None)

        # 3. MONITORAGGIO LUNGHEZZA (Logica snellita)
        stringa_attuale = st.session_state['stringa_stabile']
        lunghezza = len(stringa_attuale)
        
        # Calcoliamo la percentuale per la progress bar (max 100%)
        perc = min(lunghezza / 100, 1.0)
        
        if lunghezza > 100:
            st.error(f"⚠️ LIMITE CRITICO: {lunghezza}/100")
        elif lunghezza >= 90:
            st.warning(f"🟡 ATTENZIONE: {lunghezza}/100")
        else:
            # Usiamo un colore verde per la caption se tutto è ok
            st.markdown(f"<p style='color: #00cc66; font-size: 0.8rem; margin-bottom: -10px;'>✅ Lunghezza ottimale: {lunghezza}/100</p>", unsafe_allow_html=True)
        
        st.progress(perc)

        # 4. TAGS DI CLASSIFICAZIONE
        tags_reali = st.session_state.get('tags_stabili', [])
        if tags_reali:
            # Formattazione più pulita per i tag
            tag_html = " ".join([f"<code>{t}</code>" for t in tags_reali])
            st.markdown(f"**Classificazione:** {tag_html}", unsafe_allow_html=True)
