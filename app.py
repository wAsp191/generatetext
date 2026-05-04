import streamlit as st
from deep_translator import GoogleTranslator

# =========================================================
# 0. CONFIGURAZIONE PAGINA E LOGICA RESET
# =========================================================
st.set_page_config(page_title="Technical Generator v8.7", layout="wide")

def activate_reset():
    """Reset centralizzato e robusto dello stato dell'interfaccia"""
    
    # Valori di default per tipo di componente
    defaults = {
        'comp_tags': None,       # Pills single
        'selectbox_part': None,  # Selectbox
        'extra_tags': [],        # Pills multi
        'check_1090': False,     # Checkbox
        'check_assembled': False # Toggle
    }

    # Chiavi che devono essere sempre stringhe vuote
    text_keys = [
        'dim_l', 'dim_p', 'dim_h', 'dim_dia', 'dim_dia_gen', 
        'dim_s', 'extra_text', 'stringa_editabile'
    ]

    # 1. Reset chiavi fisse (Priorità ai valori del dizionario defaults)
    for key in defaults:
        st.session_state[key] = defaults[key]
        
    for key in text_keys:
        st.session_state[key] = ""

    # 2. Reset dinamico (campi generati a runtime)
    for key in list(st.session_state.keys()):
        if key.startswith(("manual_", "sub_")):
            st.session_state[key] = ""
            
    st.toast("Interfaccia pulita!", icon="✨")
    
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
    "Numero tasche (+)": {"1 Tasca": "1 POCKET", "2 Tasche": "2 POCKETS"}, # Qui ho tolto la graffa extra
    "Numero gradoni (+)": {"1 gradone": "1 STEP", "2 gradoni": "2 STEPS", "3 gradoni": "3 STEPS"}
}

EXTRA_CON_INPUT_MANUALE = ["Sezione circolare", "Sezione quadrata"]

# --- CONFIGURAZIONE MATERIALI ---
MATERIALI_CONFIG = {
    "METAL COMP": {"METAL": "METAL", "ZINCATO": "GALVANIZED", "INOX": "STAINLESS STEEL", "ALLUMINIO": "ALUMINIUM"},
    "WOOD COMP": {"LAMINATO": "LAMINATED", "NOBILITATO": "MELAMINE", "TRUCIOLARE": "OSB"},
    "PLASTIC COMP": {"POLICARBONATO": "POLYCARBONATE", "PVC": "PVC", "GOMMA": "RUBBER"},
    "GLASS COMP": {"VETRO TEMPRATO": "TEMPERED", "VETRO SATINATO": "SATIN"},
    "FASTENER": {"ZINCATO": "GALVANIZED", "BRUNITO": "BURNISHED", "NERO": ""}
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
            "Divisorio": ["DIVIDER", {"Sloping": "SLOPING", "Per ripiano": "FOR SHELF"}, "DIVIDER"],
            "Frontalino": ["RISER", {"Per ripiano": "FOR SHELF", "Trasparente": "TRASPARENT"}, "RISER"],
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
            "Spalla": ["FRAME", {"Numero diagonali (+)": "", "Antisismico": "SEISMIC-RESISTANT", "Sezione (+)": "", "Zincato": "GALVANIZED", "Verniciata": "POWDER COATED"}, "FRAME"],
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

OPZIONI_SPESSORE_STD = ["", "0.5", "0.6", "0.75", "0.8", "1", "1.2", "1.5", "2", "2.5", "3", "3.5", "4", "4.5", "5", "6", "8", "10"]
OPZIONI_SPESSORE_WOOD = ["", "10mm", "15mm", "18mm", "19mm", "20mm", "22mm", "24mm", "25mm", "30mm", "35mm"]

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
uni_en_1090_active = False 
mat_en, part_en, normativa, tag_suggerimento = "", "", "", ""
extra_dedicati_dict = {}
extra_selezionati = []
blocco_incompatibilita = False 

# Configurazione visuale
LARGHEZZA_IMMAGINE = 600 
TESTO_MANUALE = """
**PROCEDURA STANDARD:**
1. **CATEGORIA 📂**: Seleziona una tipologia dal gruppo a sinistra.
2. **CONFIGURAZIONE BASE 🛠️**: Scegli il tipo di materiale e componente.
3. **EXTRA E NOTE ✨**: Seleziona i pills necessari aggiungendo eventuali note.
4. **DIMENSIONAMENTO E MORMATIVE 📏**: Aggiungi dimensioni ed eventuali normative.
5. **COMPATIBILITA' 🔗**: Scegli la compatibilità (F25, F50, ecc.).
6. **GENERA STRINGA 🚀**: Clicca il tasto rosso in fondo.

---
**NOTE TECNICHE:**
* Prefissi L-P-H nel campo dimensionamento sono automatici.
* Note libere tradotte in inglese e formattate in stampatello automaticamente.
* Max 100 caratteri totali.
"""

# --- HEADER: TITOLO | MANUALE | RESET ---
col_t, col_m, col_r = st.columns([2.5, 1.5, 1], vertical_alignment="bottom")

with col_t:
    st.title("⚙️ REG - Title Generator")

with col_m:
    with st.expander("📖 Manuale d'uso"):
        st.markdown(f"""
        <div style="font-size: 14px; line-height: 1.4;">
        {TESTO_MANUALE}
        """, unsafe_allow_html=True)

with col_r:
    st.button("🔄 AZZERA", on_click=activate_reset, use_container_width=True, key="btn_top")

st.markdown("---")

# LAYOUT PRINCIPALE: Sidebar (SX) | Area Lavoro (DX)
col_left, col_workarea = st.columns([1, 4], gap="large")

with col_left:
    st.subheader("📂 1. Categoria")
    
    # --- PICCOLO BLOCCO CSS SICURO ---
    st.markdown("""
        <style>
        /* Ingrandisce il font delle opzioni nel radio button */
        div[data-testid="stRadio"] label p {
            font-size: 20px !important;
            font-weight: 500 !important;
            margin-bottom: 10px !important; /* Distanza tra le opzioni */
            padding: 5px 0px !important;
        }
        /* Aggiunge spazio tra un'opzione e l'altra */
        div[data-testid="stWidgetLabel"] {
            margin-bottom: 15px !important;
        }
        </style>
        """, unsafe_allow_html=True)

    # Mappa estetica (le tue icone)
    mappa_estetica = {
        "METAL COMP": "⚙️ METAL COMP",
        "WOOD COMP": "🪵 WOOD COMP",
        "PLASTIC COMP": "🧪 PLASTIC COMP",
        "GLASS COMP": "🧊 GLASS COMP",
        "FASTENER": "🔩 FASTENER",
        "ASSEMBLY": "🏛️ ASSEMBLY"
    }

    # Il widget radio con il font ora maggiorato dal CSS sopra
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
        # --- FIX: Usiamo 'in' per ignorare emoji o spazi extra ---
        if "ASSEMBLY" in macro_it.upper(): 
            st.toggle("ASSEMBLATO", key="check_assembled", help="Attiva se il componente è fornito già montato")
            mat_it, mat_en = "ASSEMBLY", "" # Inizializzazione sicura per il Modulo 3
        else:
            materiali_disponibili = MATERIALI_CONFIG.get(macro_it, {})
            
            if materiali_disponibili:
                # 1. Selezione Materiale Base
                mat_it = st.radio("Materiale:", options=list(materiali_disponibili.keys()), horizontal=True)
                mat_en = materiali_disponibili[mat_it]
                
                # 2. Logica Zincatura (Più robusta)
                if mat_it.upper() == "ZINCATO":
                    tipo_zinc = st.radio(
                        "Tipo zincatura:",
                        ["A FREDDO (Zinc Plated)", "A CALDO (Galvanized)"],
                        horizontal=True,
                        key="zinc_type_radio"
                    )
                    
                    # Sovrascriviamo subito mat_en per il Modulo 3
                    if "A FREDDO" in tipo_zinc:
                        mat_en = "ZINC PLATED"
                    else:
                        mat_en = "GALVANIZED"

    with c_search:
        # Recupero dettagli dal Database
        # Usiamo .get() per evitare errori se la macro_it non esiste per un millisecondo
        part_info = DATABASE.get(macro_it, {}).get("Particolari", {})
        
        scelta_part_it = st.selectbox(
            "Cerca o seleziona dettaglio:", 
            options=sorted(list(part_info.keys())), 
            index=None,
            placeholder="Cerca componente...",
            format_func=lambda x: f"🔧 {x} ({part_info[x][0]})" if x else "Seleziona...",
            key="selectbox_part"
        )

    st.markdown("---")
    
    # --- SEZIONE 3: EXTRA E NOTE ---
    st.subheader("✨ 3. Extra e Note")
    
    if scelta_part_it:
        # Recuperiamo i dati corretti dal dizionario dei particolari
        dati_part = part_info[scelta_part_it]
        part_en = dati_part[0] # Nome inglese
        extra_dedicati_dict = dati_part[1] # Dizionario extra
        
        tag_suggerimento = " - ".join(dati_part[2:]) if len(dati_part) > 2 else ""
        
        extra_options = list(extra_dedicati_dict.keys())
        if extra_options:
            extra_selezionati = st.pills("Caratteristiche:", options=extra_options, selection_mode="multi", key="extra_tags")
            
            if extra_selezionati:
                # Controllo incompatibilità (manteniamo la tua logica)
                tags_attivi = set(extra_selezionati)
                for gruppo in COPPIE_INCOMPATIBILI:
                    intersezione = gruppo.intersection(tags_attivi)
                    if len(intersezione) >= 2:
                        st.error(f"⚠️ **CONFLITTO:** {', '.join(intersezione)} non possono stare insieme.")
                        blocco_incompatibilita = True

                # Sotto-opzioni e Input manuali
                for ex in extra_selezionati:
                    if ex in SUB_OPTIONS_CONFIG:
                        st.selectbox(f"↳ Variante {ex}:", options=list(SUB_OPTIONS_CONFIG[ex].keys()), key=f"sub_{ex}")
                    elif ex in EXTRA_CON_INPUT_MANUALE:
                        st.text_input(f"↳ Valore specifico per {ex}:", key=f"manual_{ex}")
        
        if tag_suggerimento:
            st.caption(f"🔍 Classificazione suggerita: **{tag_suggerimento}**")
    
    # --- SEZIONE 4: DIMENSIONAMENTO ---
    st.subheader("📏 4. Dimensionamento e Normative")
    col_campi, col_immagine = st.columns([1, 1.5], gap="medium")

    with col_campi:
        if macro_it == "FASTENER":
            dim_l = st.text_input("Lunghezza (L)", key="dim_l")
            dim_dia = st.text_input("Diametro (D/M)", key="dim_dia")
            opzioni_norm = MAPPA_NORMATIVE_FASTENER.get(scelta_part_it, {"": ""})
            norma_scelta = st.selectbox("Riferimento Normativo", options=list(opzioni_norm.keys()))
            normativa = opzioni_norm[norma_scelta] if norma_scelta else ""
            dim_p, dim_h, dim_dia_gen = "", "", ""
        else:
            dim_l = st.text_input("Lunghezza (L)", key="dim_l")
            dim_p = st.text_input("Profondità (P)", key="dim_p")
            dim_h = st.text_input("Altezza (H)", key="dim_h")
            dim_dia_gen = st.text_input("Diametro (Ø)", key="dim_dia_gen")
            
    with col_immagine:
        st.image(
            "https://raw.githubusercontent.com/wAsp191/generatetext/main/Gemini_Generated_Image_rtac8jrtac8jrtac%20(1).png", 
            caption="Standard Quote Tecniche", 
            width=LARGHEZZA_IMMAGINE
        )

    st.markdown("---")

    # --- SEZIONE 5: COMPATIBILITÀ (L'ULTIMO STEP) ---
    st.subheader("🔗 5. Compatibilità")
    if macro_it != "FASTENER":
        pills_compatibilita = [opt for opt in OPZIONI_COMPATIBILITA if opt]
        comp_selezionata = st.pills("Seleziona il Modello di destinazione:", options=pills_compatibilita, selection_mode="single", key="comp_tags")
        
        if comp_selezionata in ["FORTISSIMO", "MINIRACK"]:
            st.warning("⚡ Componente Strutturale")
            uni_en_1090_active = st.checkbox("Certificazione UNI EN-1090", key="check_1090")
    else:
        st.info("Nessuna compatibilità necessaria per la categoria FASTENER.")

# =========================================================
# 3. LOGICA DI GENERAZIONE E TRADUZIONE (VERSIONE BLINDATA)
# =========================================================

st.divider()

# --- 1. RECUPERO DATI DALLO STATO ---
# Usiamo .get() con fallback per evitare che il codice crashi se l'utente non ha ancora toccato i widget
note_libere_it = st.session_state.get("extra_text", "").strip()
extra_selezionati = st.session_state.get("extra_tags", [])
macro_it = st.session_state.get("radio_macro", "")
scelta_part_it = st.session_state.get("selectbox_part", "")

# --- DEBUG (Rimuovi i commenti qui sotto per vedere i dati in tempo reale se non funziona) ---
# st.write(f"DEBUG: Note rilevate: '{note_libere_it}'")
# st.write(f"DEBUG: Extra: {extra_selezionati}")

# --- 2. FUNZIONE DI TRADUZIONE ROBUSTA ---
from deep_translator import GoogleTranslator

def processa_note(testo):
    if not testo:
        return ""
    try:
        # Traduzione + pulizia spazi + maiuscolo
        tradotto = GoogleTranslator(source='it', target='en').translate(testo)
        return tradotto.strip().upper()
    except Exception as e:
        # Se l'API fallisce (es. no internet), non blocchiamo tutto: usiamo l'originale in CAPS
        st.warning(f"⚠️ Traduzione fallita (usato testo originale): {e}")
        return testo.strip().upper()

# --- 3. CONTROLLO ERRORI ---
errori_rilevati = []
if extra_selezionati:
    tags_attivi = set(extra_selezionati)
    for coppia in COPPIE_INCOMPATIBILI:
        if len(coppia.intersection(tags_attivi)) >= 2:
            errori_rilevati.append(f"⚠️ **Incongruenza:** {', '.join(coppia)} sono incompatibili.")

for err in errori_rilevati:
    st.error(err)

# --- 4. TASTO GENERAZIONE ---
# Calcolo dinamico label e stato del tasto
mancano_dim = not any([st.session_state.get(f"dim_{x}", "").strip() for x in ["l", "p", "h", "dia_gen"]])
if not scelta_part_it:
    label_tasto, icona_t, disabilitato = "⚠️ SELEZIONA PARTICOLARE", "❌", True
elif mancano_dim and macro_it != "ASSEMBLY":
    label_tasto, icona_t, disabilitato = "📐 INSERISCI DIMENSIONI", "📏", False # Lasciamo False per permettere test
else:
    label_tasto, icona_t, disabilitato = "🚀 GENERA STRINGA FINALE", "✅", False

if st.button(label_tasto, use_container_width=True, disabled=disabilitato or len(errori_rilevati) > 0):
    
    # --- A. TRADUZIONE NOTE ---
    # Forza il recupero immediato dal widget per sicurezza
    note_finali_en = processa_note(note_libere_it)

    # --- B. RECUPERO INFO DATABASE ---
    # Accediamo al database dei nomi inglesi e extra
    part_info_dict = DATABASE.get(macro_it, {}).get("Particolari", {}).get(scelta_part_it, ["", {}])
    part_en = part_info_dict[0]
    extra_map = part_info_dict[1]

    # --- C. COSTRUZIONE DIMENSIONI ---
    dim_final = ""
    if macro_it == "FASTENER":
        d = st.session_state.get("dim_dia", "").strip().upper()
        l = st.session_state.get("dim_l", "").strip().upper()
        dim_final = f"{'' if d.startswith('M') else 'D'}{d}X{l}" if d and l else d or l
    else:
        dims = []
        for k, l in [("dim_l", "L"), ("dim_p", "P"), ("dim_h", "H")]:
            v = st.session_state.get(k, "").strip().upper()
            if v: dims.append(f"{l}{v}")
        lph = " ".join(dims)
        dia = st.session_state.get("dim_dia_gen", "").strip().upper()
        dim_final = " ".join(filter(None, [lph, f"Ø{dia}" if dia else None]))

    # --- D. COSTRUZIONE EXTRA (PILLS) ---
    extra_tradotti = []
    for ex in extra_selezionati:
        base = extra_map.get(ex, ex.upper())
        # Sotto-opzioni
        if ex in SUB_OPTIONS_CONFIG:
            sub_val = st.session_state.get(f"sub_{ex}", "")
            sub_tr = SUB_OPTIONS_CONFIG[ex].get(sub_val, "")
            extra_tradotti.append(f"{base} {sub_tr}".strip())
        # Manuali
        elif ex in EXTRA_CON_INPUT_MANUALE:
            m_val = st.session_state.get(f"manual_{ex}", "").strip().upper()
            extra_tradotti.append(f"{base} {m_val}" if m_val else base)
        else:
            extra_tradotti.append(base)

    # --- E. ASSEMBLAGGIO FINALE ---
    # Dividiamo tra prefissi (es. PAINTED) e suffissi
    pre, suf = [], []
    set_pre = {t.upper() for t in TERMINI_ANTICIPATI}
    for et in extra_tradotti:
        if et.split()[0].upper() in set_pre: pre.append(et)
        else: suf.append(et)

    # Materiale (evita doppioni tipo METAL METAL)
    mat_prefix = mat_en if mat_en.upper() not in part_en.upper() else ""
    
    # Unione pezzi
    componenti = [mat_prefix, " ".join(pre), part_en, dim_final, " ".join(suf)]
    corpo = " ".join(filter(None, [c.strip() for c in componenti]))
    
    # Aggiunta Note Libere (Il pezzo mancante!)
    if note_finali_en:
        corpo = f"{corpo}, {note_finali_en}"

    # Pulizia spazi e WITH
    res = " ".join(corpo.split()).upper()
    if " WITH " in f" {res} ":
        p = [x.strip() for x in res.split("WITH") if x.strip()]
        if len(p) > 1: res = f"{p[0]} WITH {' AND '.join(p[1:])}"

    # Prefissi speciali
    if macro_it == "ASSEMBLY" and st.session_state.get("check_assembled"): res = f"ASSEMBLED - {res}"
    if st.session_state.get("check_1090"): res = f"UNI EN-1090 - {res}"

    # Salvataggio
    st.session_state['stringa_editabile'] = res.strip()
    st.toast("Generato con successo!", icon=icona_t)
        
# =========================================================
# 4. OUTPUT E CLASSIFICAZIONE (FINAL STEP)
# =========================================================

if st.session_state.get('stringa_editabile'):
    st.markdown("---")
    st.subheader("📋 Risultato Finale")
    
    # Visualizzazione stringa generata
    st.code(st.session_state['stringa_editabile'], language=None)
    
    # Campo di modifica rapida
    with st.expander("✏️ Modifica manuale stringa"):
        st.text_input("Modifica il testo:", key='stringa_editabile', label_visibility="collapsed")

    # Monitoraggio lunghezza (Cruciale per i database aziendali)
    lunghezza = len(st.session_state['stringa_editabile'])
    if lunghezza > 100:
        st.error(f"⚠️ LIMITE CRITICO SUPERATO: {lunghezza}/100 caratteri")
    elif lunghezza >= 90:
        st.warning(f"🟡 Attenzione: Lunghezza limite vicina ({lunghezza}/100)")
    else:
        st.success(f"✅ Lunghezza ottimale: {lunghezza} caratteri")

    # --- SISTEMA DI CLASSIFICAZIONE (TAGS) ---
    all_tags = []
    
    # 1. Tag suggeriti dal database componenti
    if tag_suggerimento:
        all_tags.append(tag_suggerimento.upper())
    
    # 2. Modello di Compatibilità (se presente)
    comp_selezionata = st.session_state.get("comp_tags")
    if comp_selezionata:
        all_tags.append(comp_selezionata.upper())
    
    # 3. Certificazioni e Normative
    if st.session_state.get("check_1090"):
        all_tags.append("UNI EN-1090-1")
    
    if normativa:
        all_tags.append(normativa.upper())
    
    # Visualizzazione finale dei Metadati
    if all_tags:
        # Rimuoviamo eventuali duplicati mantenendo l'ordine
        all_tags = list(dict.fromkeys(all_tags))
        st.info(f"🔍 **TAGS CLASSIFICAZIONE:** {' | '.join(all_tags)}")
