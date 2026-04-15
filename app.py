import streamlit as st
from deep_translator import GoogleTranslator

import streamlit as st

# =========================================================
# 0. CONFIGURAZIONE PAGINA E LOGICA RESET
# =========================================================
st.set_page_config(page_title="Technical Generator v8.7", layout="wide")

def activate_reset():
    """Reset centralizzato e robusto dello stato dell'interfaccia"""
    
    # Mappatura dei valori di default per tipo di componente
    # Questo elimina i vari if/elif rendendo il codice compatto
    defaults = {
        'comp_tags': None,         # Pills single
        'selectbox_part': None,    # Selectbox
        'extra_tags': [],          # Pills multi
        'check_1090': False,       # Checkbox/Toggle
        'check_assembled': False,  # Checkbox/Toggle
    }

    # Chiavi che devono essere resettate a stringa vuota
    text_keys = [
        'dim_l', 'dim_p', 'dim_h', 'dim_dia', 'dim_dia_gen', 
        'dim_s', 'extra_text', 'stringa_editabile'
    ]

    # 1. Reset chiavi fisse
    for key in (list(defaults.keys()) + text_keys):
        if key in st.session_state:
            st.session_state[key] = defaults.get(key, "")

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
        "1 posizione": "1 POSITION", "2 posizioni": "2 POSITION", "3 posizioni": "3 POSITION"
    },
    "Altezza piede (+)": {"H90": "H90", "H100": "H100", "H150": "H150"},
    "Predisposto per montante (+)": {
        "L80": "FOR L80 UPRIGHT", "L100/L120": "FOR L100/L120 UPRIGHT"
    },
    "Numero tasche (+)": {"1 Tasca": "1 POCKET", "2 Tasche": "2 POCKETS"}   
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
            "Canalina passa cavi": ["CABLE TRAY", {"Forato": "PERFORATED", "Con viteria": "WITH SCREWS"}, "ESA"]
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
            "Cassa pagamento automatico": ["SELF CHECKOUT", {"Con macchine di pagamento": "WITH GLORY MACHINES PAYMENT"}, "SELF CHECKOUT (SCO)"]
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
1. **CATEGORIA**: Seleziona il gruppo a sinistra.
2. **MODELLO**: Scegli materiale e compatibilità (F25, ecc.).
3. **PARTICOLARE**: Cerca il componente e aggiungi varianti.
4. **QUOTE**: Inserisci i valori in millimetri.
5. **GENERA**: Clicca il tasto rosso in fondo.

---
**NOTE TECNICHE:**
* Prefissi L-P-H automatici.
* Note libere tradotte in inglese.
* Max 100 caratteri totali.
"""

st.title("⚙️ REG - Title Generator & Classification")

# --- TASTO AZZERA (Sempre visibile) ---
col_a, col_b, col_c = st.columns([2, 1, 2])
with col_b:
    st.button("🔄 AZZERA INTERFACCIA", on_click=activate_reset, use_container_width=True, key="btn_top")

st.markdown("---")

# LAYOUT: Sidebar (SX) | Area Lavoro (DX)
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
            st.toggle("ASSEMBLATO", key="check_assembled", help="Attiva se il componente è fornito già montato")
        else:
            materiali_disponibili = MATERIALI_CONFIG.get(macro_it, {})
            if materiali_disponibili:
                mat_it = st.radio(f"Materiale:", options=list(materiali_disponibili.keys()), horizontal=True)
                mat_en = materiali_disponibili[mat_it]

    with c_comp:
        if macro_it != "FASTENER":
            pills_compatibilita = [opt for opt in OPZIONI_COMPATIBILITA if opt]
            comp_selezionata = st.pills("Modello Compatibilità:", options=pills_compatibilita, selection_mode="single", key="comp_tags")
            
            if comp_selezionata in ["FORTISSIMO", "MINIRACK"]:
                st.warning("⚡ Componente Strutturale")
                uni_en_1090_active = st.checkbox("Certificazione UNI EN-1090", key="check_1090")
    
    st.markdown("---")
    
    # SELEZIONE PARTICOLARE
    part_dict = DATABASE[macro_it]["Particolari"]
    
    scelta_part_it = st.selectbox(
        "Cerca o seleziona dettaglio:", 
        options=sorted(list(part_dict.keys())), 
        index=None,
        placeholder="Inizia a scrivere per cercare...",
        format_func=lambda x: f"🔧 {x} ({part_dict[x][0]})" if x else "Seleziona...",
        key="selectbox_part"
    )

    st.markdown("---")
    st.subheader("✨ 3. Extra e Note")
    
    if scelta_part_it:
        dati_part = part_dict[scelta_part_it]
        part_en = dati_part[0]
        extra_dedicati_dict = dati_part[1]
        
        # Gestione Tag Suggerimento
        tag_suggerimento = " - ".join(dati_part[2:]) if len(dati_part) > 2 else ""
        
        extra_options = list(extra_dedicati_dict.keys())
        if extra_options:
            extra_selezionati = st.pills("Caratteristiche:", options=extra_options, selection_mode="multi", key="extra_tags")
            
            # --- LOGICA INCOMPATIBILITÀ ---
            if extra_selezionati:
                tags_attivi = set(extra_selezionati)
                for gruppo in COPPIE_INCOMPATIBILI:
                    intersezione = gruppo.intersection(tags_attivi)
                    if len(intersezione) >= 2:
                        st.error(f"⚠️ **CONFLITTO:** {', '.join(intersezione)} non possono stare insieme.")
                        blocco_incompatibilita = True

                # Visualizzazione Sub-Opzioni
                for ex in extra_selezionati:
                    if ex in SUB_OPTIONS_CONFIG:
                        st.selectbox(f"↳ Variante {ex}:", options=list(SUB_OPTIONS_CONFIG[ex].keys()), key=f"sub_{ex}")
                    elif ex in EXTRA_CON_INPUT_MANUALE:
                        st.text_input(f"↳ Valore specifico per {ex}:", key=f"manual_{ex}")
        
        if tag_suggerimento:
            st.caption(f"🔍 Classificazione suggerita: **{tag_suggerimento}**")

    st.text_input("Note libere (Traduzione automatica):", key="extra_text", placeholder="es: con tappi in gomma...").strip()

    st.markdown("---")
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

# =========================================================
# 3. LOGICA DI GENERAZIONE E TRADUZIONE - FIX NAMEERROR
# =========================================================

st.divider()

# --- RECUPERO SICURO DELLE VARIABILI ---
# Recuperiamo i valori direttamente dallo stato per evitare NameError
extra_libero = st.session_state.get("extra_text", "").strip()
# comp_selezionate e extra_selezionati dovrebbero essere già definiti 
# dai widget pills nel Modulo 2, ma per sicurezza:
if 'extra_tags' not in st.session_state: st.session_state['extra_tags'] = []
extra_selezionati = st.session_state['extra_tags']

# --- A. GESTIONE ERRORI E INCOMPATIBILITÀ ---
errori_rilevati = []
if extra_selezionati:
    # ... resto del codice delle incompatibilità ...
    for coppia in COPPIE_INCOMPATIBILI:
        if coppia.issubset(set(extra_selezionati)):
            errori_rilevati.append(f"⚠️ **Incongruenza:** Non puoi usare '{list(coppia)[0]}' e '{list(coppia)[1]}' insieme.")

for errore in errori_rilevati:
    st.error(errore)

blocco_genera = len(errori_rilevati) > 0

# --- B. TASTO GENERAZIONE ---
if st.button("🚀 GENERA STRINGA FINALE", use_container_width=True, disabled=blocco_genera):
    if not scelta_part_it:
        st.error("⚠️ Seleziona un particolare prima di procedere!")
    else:
        # 1. ELABORAZIONE DIMENSIONI
        dim_parts = []
        if macro_it == "FASTENER":
            d_val = st.session_state.get("dim_dia", "").strip().upper()
            l_val = st.session_state.get("dim_l", "").strip().upper()
            if d_val:
                prefix = "" if d_val.startswith('M') else "D"
                dim_parts.append(f"{prefix}{d_val}")
            if l_val: dim_parts.append(f"L{l_val}")
            dim_final = "X".join(dim_parts)
            if normativa: dim_final += f" {normativa}"
        else:
            # Recupero valori da session_state
            for p, label in [("dim_l", "L"), ("dim_p", "P"), ("dim_h", "H")]:
                val = st.session_state.get(p, "").strip().upper()
                if val: dim_parts.append(f"{label}{val}")
            
            lph_str = " ".join(dim_parts)
            dia_val = st.session_state.get("dim_dia_gen", "").strip().upper()
            s_val = st.session_state.get("dim_s", "").strip().upper()
            
            dim_final = " ".join(filter(None, [lph_str, f"Ø{dia_val}" if dia_val else None, f"S{s_val}" if s_val else None]))

        # 2. ELABORAZIONE EXTRA (PILLS) - Mantenendo ordine DB
        extra_pills_final = []
        for opt in list(extra_dedicati_dict.keys()):
            if extra_selezionati and opt in extra_selezionati:
                base_t = extra_dedicati_dict.get(opt, opt.upper())
                # Gestione Sotto-Opzioni (+)
                if opt in SUB_OPTIONS_CONFIG:
                    val_sub = st.session_state.get(f"sub_{opt}", "")
                    trad_sub = SUB_OPTIONS_CONFIG[opt].get(val_sub, "")
                    extra_pills_final.append(f"{base_t} {trad_sub}".strip())
                # Gestione Input Manuale
                elif opt in EXTRA_CON_INPUT_MANUALE:
                    v_man = st.session_state.get(f"manual_{opt}", "").strip().upper()
                    extra_pills_final.append(f"{base_t} {v_man}" if v_man else base_t)
                else:
                    extra_pills_final.append(base_t)

        # 3. TRADUZIONE NOTE LIBERE
        note_tradotte = ""
        if extra_libero:
            testo_it = extra_libero.lower()
            for ita, eng in GLOSSARIO_TECNICO.items():
                testo_it = testo_it.replace(ita, eng)
            try:
                note_tradotte = GoogleTranslator(source='it', target='en').translate(testo_it).upper()
            except:
                note_tradotte = extra_libero.upper()

        # 4. ASSEMBLAGGIO LOGICO
        # --- NUOVA LOGICA DI SMISTAMENTO (MATCH PAROLA INTERA) ---
        pre = []
        suf = []
        
        # Rendiamo i termini anticipati un set per confronto rapido
        set_anticipati = {term.upper() for term in TERMINI_ANTICIPATI}
        
        for p in extra_pills_final:
            parole_nel_pill = set(p.upper().split())
            if not parole_nel_pill.isdisjoint(set_anticipati):
                pre.append(p)
            else:
                suf.append(p)
        
        pre_str = " ".join(pre)
        suf_str = " ".join(suf)
        
        # Gestione Materiale: evito "METAL METAL"
        # QUI C'ERA L'ERRORE DI INDENTAZIONE
        mat_prefix = mat_en if not (mat_en == "METAL" and "METAL" in part_en.upper()) else ""
        
        # Costruzione corpo centrale
        corpo = f"{mat_prefix} {pre_str} {part_en} {dim_final} {suf_str}".replace("  ", " ").strip()
        
        # Aggiunta Note con virgola
        if note_tradotte:
            corpo = f"{corpo}, {note_tradotte}"

        # Unione con Modello/Compatibilità
        comp_str = st.session_state.get("comp_tags", "")
        res = f"{corpo} - {comp_str}" if comp_str else corpo

        # 5. PULIZIA FINALE (GRAMMATICA AI)
        res = res.upper().replace("WITH WITH", "WITH")
        if res.count("WITH") > 1:
            parts = res.split("WITH")
            res = parts[0] + "WITH" + " AND".join(parts[1:])
        
        # Prefissi di certificazione
        if macro_it == "ASSEMBLY" and st.session_state.get("check_assembled"):
            res = f"ASSEMBLED - {res}"
        if uni_en_1090_active:
            res = f"UNI EN-1090 - {res}"

        st.session_state['stringa_editabile'] = res.replace("  ", " ").strip()
        
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

# --- TASTO RESET INFERIORE ---
st.markdown("<br>", unsafe_allow_html=True)
cb1, cb2, cb3 = st.columns([2, 1, 2])
with cb2:
    st.button("🔄 NUOVA GENERAZIONE", on_click=activate_reset, use_container_width=True, key="btn_bottom")
