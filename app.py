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
# 1A. GRUPPI DI PILLS (EXTRA) CENTRALIZZATI E CONDIVISI
# =========================================================
# Centralizzando i Pills azzeriamo i refusi e permettiamo all'Analytics 
# di mappare esattamente l'uso della stessa caratteristica su pezzi diversi.

PILLS_CONDIVISI = {
    "PILLS_PIEDI": {
        "Altezza piede (+)": "", 
        "Predisposto per montante (+)": "", 
        "Antisismico": "SEISMIC", 
        "Statico": "STATIC", 
        "Regolabile": "ADJUSTABLE",
        "Compatibilità piede di base (+)": ""
    },
    "PILLS_ZOCCOLI": {
        "Compatibilità piede di base (+)": "", 
        "Liscia": "PLAIN", 
        "Angolo aperto": "EXTERNAL CORNER", 
        "Angolo chiuso": "INNER CORNER", 
        "Inclinata": "INCLINED", 
        "Forata": "PERFORATED", 
        "Stondata": "ROUNDED", 
        "Completa di paracolpo ABS": "WITH ABS BUFFER",
        "Con lati bordati": "WITH EDGED SIDES", 
        "Con viteria": "WITH SCREWS"
    },
    "PILLS_PANNELLI": {
        "Centrale": "CTR", 
        "Scantonato": "NOTCHED", 
        "Forato": "PERFORATED", 
        "Multibarra": "MULTIBAR", 
        "Multilame": "MULTISTRIP", 
        "In rete": "MESH", 
        "Nervato": "RIBBED", 
        "Attacco montante": "HOOK ONTO UPRIGHT", 
        "Angolo aperto": "EXTERNAL CORNER", 
        "Angolo chiuso": "INNER CORNER",
        "Con mensole": "WITH BRACKET", 
        "Con viteria": "WITH SCREWS", 
        "Con lati bordati": "WITH EDGED SIDES",
        "Serigrafata": "SILKSCREENED", 
        "Antiurto": "SHOCKPROOF", 
        "Trasparente": "TRANSPARENT", 
        "Bordi smussati": "CHAMFERED EDGES",
        "Aggangio montante": "HOOK ONTO UPRIGHT"
    },
    "PILLS_CHIUSURE": {
        "Superiore": "TOP", 
        "Tra ripiani di base": "INTER-BASE SHELF", 
        "Con scasso": "WITH RECESS",
        "Per Top legno": "FOR TOP SHELF"
    },
    "PILLS_FIANCATE": {
        "Orientamento (+)": "", 
        "Forata": "PERFORATED", 
        "Portante": "LOAD-BEARING", 
        "Non portante": "NON LOAD-BEARING", 
        "Stondata": "ROUNDED", 
        "Trapezoidale": "SLOPING", 
        "Sagomata": "SHAPED",
        "Con mensole": "WITH BRACKET", 
        "Con lati bordati": "WITH EDGED SIDES", 
        "Con viteria": "WITH SCREWS", 
        "Fresata": "MILLING"
    },
    "PILLS_MENSOLE": {
        "Orientamento (+)": "", 
        "Posizioni multiple (+)": "", 
        "Antisgancio": "ANTI-RELEASE", 
        "Rinforzata": "REINFORCED", 
        "Nervata": "RIBBED", 
        "Per ripiano in vetro": "FOR GLASS SHELF", 
        "Per ripiano in legno": "FOR WOODEN SHELF", 
        "A pinza": "GRIPPED", 
        "Minirack": "FOR MINIRACK"
    },
    "PILLS_RIPIANI": {
        "Liscio": "PLAIN", 
        "Forato": "PERFORATED", 
        "Stondato": "ROUNDED", 
        "In filo": "WIRE", 
        "Semicircolare": "SEMICIRCULAR", 
        "Con rinforzo": "REINFORCED", 
        "Con inserti filettati": "WITH RIVET", 
        "Con portaprezzo": "WITH TICKET-HOLDER", 
        "Scantonato": "NOTCHED",
        "Con mensole": "WITH BRACKET", 
        "Con lati bordati": "WITH EDGED SIDES", 
        "Con viteria": "WITH SCREWS", 
        "Fresata": "MILLING",
        "Per ripiano": "FOR SHELF"
    },
    "PILLS_CESTI_FILO": {
        "Per attacco montante": "HOOK ONTO UPRIGHT", 
        "Per attacco fiancata": "HOOK ONTO SIDE-PANEL", 
        "Impilabile": "STACKABLE", 
        "Con mensole saldate": "WITH WELDED BRACKET"
    },
    "PILLS_CIELINI": {
        "Dritto": "STRAIGHT", 
        "Inclinato": "SLOPING", 
        "Con finestra": "WITH WINDOW", 
        "Stondato": "CURVED", 
        "Centrale": "CENTRAL", 
        "Con illuminazione": "WITH LIGHTING",
        "Con mensole": "WITH BRACKET", 
        "Con viteria": "WITH SCREWS", 
        "Con lati bordati": "WITH EDGED SIDES"
    },
    "PILLS_CORRENTI": {
        "A seggiola": "L-SHAPED PROFILE", 
        "VPA (+)": "VPA", 
        "Tipologia di mensola (+)": ""
    },
    "PILLS_DIAGONALI_DIST": {
        "Forata": "PERFORATED", 
        "Per crociera verticale": "FOR VERTICAL CROSS-WALL",
        "Per controventatura": "FOR CROSS-WALL"
    },
    "PILLS_GANCI": {
        "Attacco gancio (+)": "", 
        "Singolo": "SINGLE", 
        "Predisposto per portaprezzo": "ACCEPTS TICKET-HOLDER", 
        "Doppio": "DOUBLE", 
        "Rovescio": "REVERSE"
    },
    "PILLS_PROFILI": {
        "Profilo a L": "L-SHAPED", 
        "Profilo a U": "U-SHAPED"
    },
    "PILLS_RINFORZI_STAFFE": {
        "Asolato": "SLOTTED", 
        "Per ripiano di base": "FOR BASE SHELF", 
        "Per fiancata": "FOR SIDE PANEL",
        "Con viteria": "WITH SCREWS", 
        "Di collegamento": "CONNECTING"
    },
    "PILLS_ANTE_SPORTELLI": {
        "Scorrevoli": "SLIDING", 
        "Con foro serratura": "WITH LOCK HOLE", 
        "A saracinesca": "SHUTTER", 
        "Forata": "PERFORATED",
        "Trasparente": "TRANSPARENT", 
        "Bordi smussati": "CHAMFERED EDGES", 
        "Serigrafata": "SILKSCREENED", 
        "Antiurto": "SHOCKPROOF",
        "Orientamento (+)": "",
        "Scorrevole": "SLIDING"
    },
    "PILLS_CASSETTI": {
        "Compatibilità piede di base (+)": "", 
        "Su ruote": "ON WHEELS", 
        "Con serratura": "WITH LOCK", 
        "Senza serratura": "WITHOUT LOCK",
        "Con guide RAM": "WITH RAM GUIDE", 
        "Attacco montante": "HOOK ONTO UPRIGHT",
        "Con cassetto": "WITH DRAWER", 
        "Con ruote": "WITH WHEELS"
    },
    "PILLS_COPRIMONTANTI": {
        "Per montante H70": "FOR H70 UPRIGHT", 
        "Per montante H90": "FOR H90 UPRIGHT",
        "Minirack": "MINIRACK", 
        "Con lati bordati": "WITH EDGED SIDES", 
        "Con viteria": "WITH SCREWS"
    },
    "PILLS_DIVISORI_FRONTALINI": {
        "In filo": "WIRE", 
        "Trapezoidale": "SLOPING", 
        "Per ripiano": "FOR SHELF",
        "Cromato": "CHROMED", 
        "Verniciato": "PAINTED",
        "Trasparente": "TRANSPARENT",
        "Inclinato": "SLOPING"
    },
    "PILLS_CONTROVENTATURE": {
        "Per montante": "FOR UPRIGHT", 
        "Con mensole saldate": "WITH WELDING BRACKET", 
        "Passo 25": "PITCH 25", 
        "Passo 50": "PITCH 50",
        "Forato": "PERFORATED",
        "Con viteria": "WITH SCREWS",
        "Gondola": "GONDOLA", 
        "Sezione (+)": "", 
        "Su due livelli": "TWO LEVELS", 
        "Numero diagonali (+)": "", 
        "Con distanziale (+)": "WITH SPACER"
    },
    "PILLS_TUBOLARI_FILO": {
        "Con componente saldato": "WITH WELDED ELEMENT", 
        "Sezione quadrata": "SQUARE SECTION", 
        "Sezione circolare": "CIRCULAR SECTION", 
        "Piegato-saldato": "BENT AND WELDED", 
        "Con mensole saldate": "WITH WELDING BRACKET", 
        "Con viteria": "WITH SCREWS",
        "Piegato": "BENT", 
        "Con viteria saldata": "WITH WELDING SCREWS"
    },
    "PILLS_MONTANTI_LAMIERE": {
        "Sezione (+)": "", 
        "Statico": "STATIC", 
        "Antisismico": "ANTI-SEISMIC", 
        "Regolabile": "ADJUSTABLE", 
        "Con collegamento superiore": "WITH UPPER CONNECTION",
        "Forata": "PERFORATED", 
        "Piegata": "BENT", 
        "Saldata": "WELDED"
    },
    "PILLS_ADATTATORI_CANALINE": {
        "Forato": "PERFORATED", 
        "Aggangio montante": "HOOK ONTO UPRIGHT", 
        "Passo 25": "PITCH 25", 
        "Passo 50": "PITCH 50", 
        "L50": "L50", 
        "L55": "L55",
        "Con viteria": "WITH SCREWS",
        "Con piega frontale": "WITH DOWNWARD"
    },
    "PILLS_PORTAPREZZI": {
        "Trasparente": "TRANSPARENT", 
        "Colorato": "COLORED", 
        "Con tasca oscillante": "WITH LIFT-UP POCKET", 
        "Adesivo": "ADHESIVE", 
        "Con asola centrale": "WITH CENTRAL SLOT"
    },
    "PILLS_GLASS_ARM": {
        "Orientamento (+)": "", 
        "Illuminato": "ILLUMINATED", 
        "Serigrafata": "SILKSCREENED", 
        "Antiurto": "SHOCKPROOF"
    },
    "PILLS_VITI_BULLONI": {
        "Autoperforanti": "SELF-DRILLING", 
        "Testa svasata": "COUNTERSUNK HEAD", 
        "Testa esagonale": "HEX HEAD", 
        "Testa a croce": "CROSS HEAD", 
        "Testa esagono incassato": "HEXAGON SOCKET HEAD", 
        "Testa Bombata": "ROUND HEAD"
    },
    "PILLS_RONDELLE_DADI": {
        "Dentellata": "SERRATED LOCK", 
        "Fascia Larga": "WIDE BAND", 
        "Elastica": "GROWER",
        "Autobloccante": "SELF-LOCKING", 
        "Flangiato": "FLANGED",
        "Con testa": "WITH HEAD", 
        "Senza testa": "WITHOUT HEAD"
    },
    "PILLS_ASSEMBLY_VETRINE": {
        "Terminale": "END", 
        "Centrale": "CENTRAL", 
        "Con illuminazione": "WITH LIGHTING", 
        "Con ante scorrevoli": "WITH SLIDING DOOR",
        "Mobile": "MOBILE", 
        "Per alimenti": "FOR FOOD",
        "Rotante": "ROTATING", 
        "Per casse automatiche": "FOR SELF PAY"
    },
    "PILLS_ASSEMBLY_SPALLE": {
        "Sezione (+)": "", 
        "Numero diagonali (+)": "", 
        "Antisismico": "SEISMIC-RESISTANT", 
        "Zincato": "GALVANIZED", 
        "Verniciata": "POWDER COATED", 
        "Asimmetrica (+)": ""
    },
    "PILLS_ASSEMBLY_AVANCASSA": {
        "Con ripiani": "WITH SHELF", 
        "Con ripiani inclinati": "WITH INCLINED SHELF", 
        "Con rete divisoria": "WITH DIVIDING NET", 
        "Con ruote": "WITH WHEELS", 
        "Con ganci": "WITH HOOKS", 
        "Con batticarrello": "WITH TROLLEY BEATER",
        "Numero tasche (+)": "", 
        "Con portaprezzo in filo": "WITH PRICE-HOLDER WIRE",
        "Con macchine di pagamento": "WITH GLORY MACHINES PAYMENT",
        "Numero gradoni (+)": "",
        "Forato": "PERFORATED", 
        "Attacco montante": "ONTO THE UPRIGHT", 
        "Con mensole saldate": "WITH WELDED BRACKETS"
    },
    "PILLS_VUOTO": {}
}

# =========================================================
# 1B. DATABASE COMPONENTI SNELLITO (Puntatori ai Pills)
# =========================================================
DATABASE = {
    "METAL COMP": {
        "macro_en": "METAL COMPONENT",
        "Particolari": {
            "Piede di base": ["BASE FOOT", "PILLS_PIEDI", "FOOT"],
            "Zoccolatura": ["PLINTH", "PILLS_ZOCCOLI", "PLINTH"],
            "Pannello rivestimento": ["BACK PANEL", "PILLS_PANNELLI", "PANEL"],
            "Copripiede": ["FOOT COVER", "PILLS_PIEDI", "COVER"],
            "Chiusura": ["COVER", "PILLS_CHIUSURE", "COVER"],
            "Fiancata laterale": ["SIDE PANEL", "PILLS_FIANCATE", "SIDE-PANEL"],
            "Mensola": ["BRACKET", "PILLS_MENSOLE", "BRACKET"],
            "Ripiano": ["SHELF", "PILLS_RIPIANI", "SHELF"],
            "Cesto in filo": ["WIRE-BASKET", "PILLS_CESTI_FILO", "BASKET"],
            "Cielino": ["CANOPY", "PILLS_CIELINI", "CANOPY"],
            "Corrente": ["BEAM", "PILLS_CORRENTI", "BEAM"],
            "Diagonale": ["DIAGONAL", "PILLS_DIAGONALI_DIST", "DIAGONAL"],
            "Distanziale": ["SPACER", "PILLS_DIAGONALI_DIST", "SPACER"],
            "Gancio": ["HOOK", "PILLS_GANCI", "HOOK"],
            "Profilo": ["PROFILE", "PILLS_PROFILI", "PROFILE"],
            "Rinforzo": ["STIFFENER", "PILLS_RINFORZI_STAFFE", "STIFFENER"],
            "Staffa": ["PLATE", "PILLS_RINFORZI_STAFFE", "PLATE"],
            "Anta/sportello": ["DOOR", "PILLS_ANTE_SPORTELLI", "DOOR"],
            "Piastra di fissaggio": ["FIXING PLATE", "PILLS_RINFORZI_STAFFE", "PLATE"],
            "Cassetto estraibile": ["PULL-OUT DRAWER", "PILLS_CASSETTI", "DRAWER"],
            "Coprimontante": ["UPRIGHT-COVER", "PILLS_COPRIMONTANTI", "COVER"],
            "Pedana di base": ["BASE PLATFORM", "PILLS_RINFORZI_STAFFE", "BASE"],
            "Divisorio": ["DIVIDER", "PILLS_DIVISORI_FRONTALINI", "DIVIDER"],
            "Frontalino": ["RISER", "PILLS_DIVISORI_FRONTALINI", "RISER"],
            "Compensazione": ["FILLER PIECE", "PILLS_RINFORZI_STAFFE", "SPACER"],
            "Controventatura": ["BRACING", "PILLS_CONTROVENTATURE", "BRACING"],
            "Traversino": ["CROSS BAR", "PILLS_CONTROVENTATURE", "CROSS BAR"],
            "Tubolare": ["TUBULAR", "PILLS_TUBOLARI_FILO", "BAR"],
            "Filo": ["WIRE", "PILLS_TUBOLARI_FILO", "WIRE"],
            "Montante": ["UPRIGHT", "PILLS_MONTANTI_LAMIERE", "UPRIGHT"],
            "Lamiera generica": ["SHEET METAL", "PILLS_MONTANTI_LAMIERE", "GENERIC SHEET METAL"],
            "Pannello frontale": ["FRONT PANEL", "PILLS_PANNELLI", "PANEL"],
            "Adattatore": ["ADAPTER", "PILLS_ADATTATORI_CANALINE", "ADAPTER"],
            "Canalina passa cavi": ["CABLE TRAY", "PILLS_ADATTATORI_CANALINE", "ESA"],
            "Protezione": ["PROTECTION FOR PERFORATED SHELF", "PILLS_ADATTATORI_CANALINE", "PROTECTION"]
        }
    },
    "WOOD COMP": {
        "macro_en": "WOOD COMPONENT",
        "Particolari": {
            "Ripiano Legno": ["WOODEN SHELF", "PILLS_RIPIANI", "SHELF"],
            "Schienale Legno": ["WOODEN BACK", "PILLS_PANNELLI", "PANEL"],
            "Cielino": ["WOODEN CANOPY", "PILLS_CIELINI", "CANOPY"],
            "Zoccolatura": ["WOODEN PLINTH", "PILLS_ZOCCOLI", "PLINTH"],
            "Fiancata": ["WOODEN SIDE PANEL", "PILLS_FIANCATE", "SIDE PANEL"],
            "Copripiede": ["WOODEN FOOT-COVER", "PILLS_ZOCCOLI", "COVER"],
            "Coprimontante": ["WOODEN UPRIGHT-COVER", "PILLS_COPRIMONTANTI", "COVER"],
            "Compensazione": ["WOODEN FILLER PIECE", "PILLS_CHIUSURE", "SPACER"],
            "Mobiletto in legno": ["WOODEN CABINET", "PILLS_FIANCATE", "CABINET"]
        }
    },
    "PLASTIC COMP": {
        "macro_en": "PLASTIC COMPONENT",
        "Particolari": {
            "Tappo": ["PLASTIC CAP", "PILLS_VUOTO", "CAP"],
            "Guarnizione": ["GASKET", "PILLS_VUOTO", "ACCESSORY"],
            "Cerniera": ["HINGE", "PILLS_VUOTO", "ACCESSORY"],
            "Divisorio": ["DIVIDER", "PILLS_DIVISORI_FRONTALINI", "DIVIDER"],
            "Frontalino": ["RISER", "PILLS_DIVISORI_FRONTALINI", "RISER"],
            "Pannello": ["PANEL", "PILLS_PANNELLI", "PANEL"],
            "Anta": ["DOOR", "PILLS_ANTE_SPORTELLI", "DOOR"],
            "Portaprezzo": ["TICKET-HOLDER", "PILLS_PORTAPREZZI", "TICKET-HOLDER"]
        }
    },
    "GLASS COMP": {
        "macro_en": "GLASS COMPONENT",
        "Particolari": {
            "Ripiano": ["GLASS SHELF", "PILLS_VUOTO", "SHELF"],
            "Anta": ["GLASS DOOR", "PILLS_ANTE_SPORTELLI", "DOOR"],
            "Cancelletto": ["GLASS ARM", "PILLS_GLASS_ARM", "ARM"]
        }
    },
    "FASTENER": {
        "macro_en": "FASTENER",
        "Particolari": {
            "Vite": ["SCREW", "PILLS_VITI_BULLONI", "SCREW"],
            "Bullone": ["BOLT", "PILLS_VUOTO", "FASTENER"],
            "Rondella": ["WASHER", "PILLS_RONDELLE_DADI", "WASHER"],
            "Dado": ["NUT", "PILLS_RONDELLE_DADI", "NUT"],
            "Inserti filettati": ["RIVET", "PILLS_RONDELLE_DADI", "RIVET"]
        }
    },
    "ASSEMBLY": {
        "macro_en": "ASSEMBLY",
        "Particolari": {
            "Vetrina": ["SHOWCASE", "PILLS_ASSEMBLY_VETRINE", "SHOWCASE"],
            "Espositore": ["DISPLAY", "PILLS_ASSEMBLY_VETRINE", "DISPLAY"],
            "Totem": ["TOTEM", "PILLS_ASSEMBLY_VETRINE", "DISPLAY"],
            "Spalla": ["FRAME", "PILLS_ASSEMBLY_SPALLE", "FRAME"],
            "Controventatura": ["CROSS-BRACING", "PILLS_CONTROVENTATURE", "CROSS-BRACING"],
            "Banco espositore di legno": ["WOODEN DESK", "PILLS_CASSETTI", "DESK"],
            "Avancassa": ["IMPULSE UNIT", "PILLS_ASSEMBLY_AVANCASSA", "DISPLAY"],
            "Cassettiera": ["CHEST OF DRAWERS", "PILLS_CASSETTI", "DRAWER"],
            "Espositore riviste": ["DISPLAY FOR MAGAZINE", "PILLS_ASSEMBLY_AVANCASSA", "DISPLAY", "BOOK AND MAGAZINE"],
            "Cassa pagamento automatico": ["SELF CHECKOUT", "PILLS_ASSEMBLY_AVANCASSA", "SELF CHECKOUT (SCO)"],
            "Espositore a gradoni": ["STEPLADDER DISPLAY", "PILLS_ASSEMBLY_AVANCASSA", "DISPLAY"],
            "Telaio saldato": ["METAL WELDMENT", "PILLS_ASSEMBLY_AVANCASSA", "FRAME"]
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
            # Gestiamo solo il toggle. 
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
        dati_part = part_info.get(scelta_part_it, ["", "PILLS_VUOTO", ""])
        
        # --- LOGICA CORRETTA PER PILLS CENTRALIZZATI ---
        # Recuperiamo la stringa-chiave del gruppo (es: "PILLS_PIEDI")
        chiave_gruppo_pills = dati_part[1]
        # Estraiamo i relativi Pills dal dizionario globale PILLS_CONDIVISI
        pills_disponibili = PILLS_CONDIVISI.get(chiave_gruppo_pills, {})
        extra_options = list(pills_disponibili.keys())
        
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
        part_db = DATABASE.get(macro_it, {}).get("Particolari", {}).get(scelta_part_it, ["", "PILLS_VUOTO", ""])
        part_en = part_db[0].upper()
        
        # --- LOGICA ADATTATA AL NUOVO DB CENTRALIZZATO ---
        chiave_gruppo_pills = part_db[1]
        dict_extra_db = PILLS_CONDIVISI.get(chiave_gruppo_pills, {})
        
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
        if macro_it == "ASSEMBLY":
            prefix_base = "ASSEMBLED" if st.session_state.get("check_assembled") else ""
        else:
            prefix_base = mat_en

        elementi_prefisso = [prefix_base] + lista_prima
        prefisso_lista = [p.strip().upper() for p in elementi_prefisso if p.strip()]
        prefix_completo = " ".join(prefisso_lista)
        
        part_en_upper = part_en.strip().upper()
        
        parole_prefisso = set(prefix_completo.split())
        parole_componente = set(part_en_upper.split())

        if parole_prefisso and (parole_prefisso.issubset(parole_componente) or part_en_upper.startswith(prefix_completo)):
            core = part_en_upper
        else:
            core = f"{prefix_completo} {part_en_upper}".strip()
        
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
            corpo += " (UNI EN 1090-1)"

        # --- F. SALVATAGGIO IN SESSION STATE ---
        st.session_state['stringa_stabile'] = " ".join(corpo.split()).upper()

        # =========================================================
        # 📊 LIVE INJECTION: INVIO AUTOMATICO A GOOGLE SHEETS
        # =========================================================
        # Il sistema invia i log solo se sono stati attivati dei Pills 
        # o se i colleghi hanno inserito delle note libere a mano.
        if tags_scelti_raw or note_en:
            try:
                import datetime
                import pandas as pd
                from streamlit_gsheets import GSheetsConnection
                
                # Connessione al volo ai Secrets di Streamlit
                conn = st.connection("gsheets", type=GSheetsConnection)
                
                # Normalizzazione orario locale italiano
                orario_corrente = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                
                # Prepariamo i record. Se ci sono più Pills scelti, generiamo una riga per ciascuno.
                # Se non ci sono Pills ma ci sono note libere, mandiamo una riga generica di tracciamento.
                righe_log = []
                pills_da_loggare = tags_scelti_raw if tags_scelti_raw else ["- NESSUNO -"]
                
                for pill in pills_da_loggare:
                    righe_log.append({
                        "Data": orario_corrente,
                        "Categoria": str(macro_it).upper(),
                        "Componente": str(scelta_part_it).upper(),
                        "Pill": str(pill).upper(),
                        "Note Tradotte": str(note_en).upper()
                    })
                
                df_log = pd.DataFrame(righe_log)
                conn.append_row(df_log)
            except:
                pass # Fail-safe blindato: se Google è offline l'app principale non va mai in crash
        
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
