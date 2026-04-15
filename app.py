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
# 1. DATABASE E CONFIGURAZIONI (v9.0 - Finiture Legno)
# =========================================================

# --- 1.1 CONFIGURAZIONE FINITURE LEGNO (CATEGORIZZATA) ---
# Struttura: "MATERIALE": { "Nome Utente": "Sigla" }

FINITURE_LEGNO = {
    "LAMINATO": {
        "LE04 - LAM R20064 ROVERE": "LE04",
        "LE06 - LAM. PFLEIDERER U16002W TORTORA": "LE06",
        "LE11 - LAM. KASTAMONU A847 ALASKA": "LE11",
        "LE15 - LAM ANTIGR THERMOP U12231 PFLEDERER": "LE15",
        "LE24 - LAM. ROV. MILANO R20095MO": "LE24",
        "LE27 - CLEAF SHERWOOD S073SJP": "LE27",
        "LE40 - LAM. KAINDL 37744 BIANCO": "LE40",
        "LE42 - LAM. KAINDL 37777 FRASSINO COIMBRA": "LE42",
        "LE63 - LAM. ROV. MILANO R20095 ML": "LE63",
        "LE73 - LAM. ROVERE KRONO D4225 OV": "LE73",
        "LE79 - LAM PFLEIDERER F76044 SD - GRIGIO": "LE79",
        "LE86 - LAM EUREKA OAK DA1 FIN.EVO": "LE86",
        "LH06 - LAM. FUNDER 0260 AREZZO": "LH06",
        "LH23 - LAM. CLEAF SABLE' VALLEY LR22": "LH23",
        "LH27 - LAM. CLEAF ARES FB11 BETON": "LH27",
        "LH29 - LAM. PFLEIDERER R42033 ML": "LH29",
        "LH37 - LAM. CLEAF MONTILLA FC 18": "LH37",
        "LH38 - LAM. CLEAF MILLENIUM S083 NAGOLD": "LH38",
        "LH40 - LAM. SAIB CH3013 GRIGIO GRAFITE": "LH40",
        "LH62 - LAM. CLEAF PIOMBO HM07": "LH62",
        "LH64 - LAM. EGGER W1000ST19 B.CO PREMIUM": "LH64",
        "LH81 - LAM. EGGER H3331 ST15 HYDROFUGE": "LH81",
        "LH83 - LAM. BIANCO TRAFFICO SDW10140": "LH83",
        "LH95 - LAM. PFLEIDERER ROVERE R20099": "LH95",
        "LH98 - LAM. PFLEIDERER BLU CRISTAL U18003": "LH98",
        "LH99 - LAM. SM'ART 4565 OLMO MIELE": "LH99",
        "LTH1 - LAM. THERMOPAL U506 ANTRHAZIT": "LTH1",
        "LU51 - LAM. AMET.U504 ST BLU": "LU51",
        "LU61 - LAM. EGGER H3303": "LU61",
        "LU62 - LAM. ABET LAMINATI 1860PRINT": "LU62",
        "LU63 - LAM. GREENLAM 5049 - SUEDE RED OAK": "LU63",
        "LU64 - LAM. EGGER H3152 ROV VICEN SBIA ST19": "LU64",
        "LU71 - LAM. KRONOSPAN D4823VL": "LU71",
        "LU73 - LAM. ABET PRINT 1832 F. SEI": "LU73",
        "LU74 - LAM. FORMICA K 1238 UN": "LU74",
        "LU75 - LAM. LEGNOPAN 111 FIN ROV 19POR NAT": "LU75",
        "L035 - LAM. PRINT 421 SEI NERO": "L035",
        "L036 - LAM. ABET PRINT FIN. 460 SEI VERDE": "L036",
        "L039 - LAM. PRINT 871 SEI GRIGIO CENE": "L039",
        "L040 - LAM. PRINT 475 SEI GRIGIO SILICIO": "L040",
        "L041 - LAM. PRINT 411 SEI BIANCO": "L041",
        "L386 - LAM. OLMO LEONE PLEID.R37009 MO": "L386",
        "L406 - LAM. PRINT 406 BIANCO": "L406",
        "L410 - LAM. ABET PRINT 410 SEI BIANCO": "L410",
        "L418 - LAM. PRINT 418 SEI BIANCO": "L418",
        "L428 - LAM. PRINT 428 SEI BLU": "L428",
        "L466 - LAM. PHOENIX F76026 MARRONE CR PFL": "L466",
        "L469 - LAM. PRINT 469 SEI GIALLO": "L469",
        "L559 - LAM. FUNDERMAX 0921 SU BROWN SILVER": "L559",
        "L563 - LAM. PRINT 563 MANDARIN GRIGIO": "L563",
        "L578 - LAM. ROVERE BARDOLINO": "L578",
        "L579 - LAM. PFLEID.R20128 ROVERE SON.F.RU": "L579",
        "L590 - LAM. EGGER U332 ARANCIO": "L590",
        "L641 - LAM. THERMOPAL SR 209/01 B.LUC": "L641",
        "L696 - LAM. THERM.F21/005 OLIVO SPAGN CHIA": "L696",
        "L716 - LAM. THERMOPAL U018(47) GRIGIO": "L716",
        "L745 - LAM. THERM R20031RU L745": "L745",
        "L752 - LAM. PFLEIDERER W10003 MP BIANCO": "L752",
        "L767 - LAM. EGGER ROV.HALIFAX H1180 ST37": "L767",
        "L786 - LAM. PRINT 1677 ACERO EX PURICELLI": "L786",
        "L814 - LAM. ABET 1666 FIN SEI DUE FAGGIO": "L814",
        "L833 - LAM. PRINT 2810 CLIMB": "L833",
        "L835 - LAM. PRINT 835 SEI ARANCIO": "L835",
        "L852 - LAM. PRINT 852 SEI BLU": "L852",
        "L873 - LAM. PRINT 873 FIN SATINATA": "L873",
        "L879 - LAM. PRINT 879 SEI GRIGIO ANTRACITE": "L879",
    },
    "NOBILITATO": {
        "LU70 - NOB. KRONO ABETE D79841": "LU70",
        "NE05 - NOB. PFLEIDERER U16002W TORTORA": "NE05",
        "NE12 - NOB. KASTAMONU A847 ALASKA": "NE12",
        "NE19 - NOB. EGGER W911 BIANCO ST15": "NE19",
        "NE28 - NOB. CLEAF SHERWOOD S073 S.J.P.": "NE28",
        "NE38 - NOB. KAINDL 34140 RV ROV.SANREMO CL": "NE38",
        "NE41 - NOB. KAINDL 37777 FRASSINO COIMBRA": "NE41",
        "NE46 - NOB. PFLEIDERER U19008 VERDE SCURO": "NE46",
        "NE62 - NOB. 256 H1145 ST10 CHENE BARDOLINO": "NE62",
        "NE67 - NOB. ROVERE GLADST H3309 ST28": "NE67",
        "NE70 - NOB. GRAPHITE U961 ST9": "NE70",
        "NE74 - NOB. ROVERE KRONO D4225 OV A": "NE74",
        "NE75 - NOB. EGGER H3156 ROV.CORB.GR": "NE75",
        "NE88 - NOB. CLEAF UA32 TALCO GRIGIO": "NE88",
        "NE91 - NOB. PFLEIDERER PHOENIX F76026": "NE91",
        "NE99 - NOB. PFLEIDERER R20099": "NE99",
        "NH01 - NOB. R20065 ROVERE MONTAGNA SCURO": "NH01",
        "NH03 - NOB. EGGER GLADSTONE BIANCO H3335": "NH03",
        "NH04 - NOB. FUNDER 0290 NA ROVERE SBIA": "NH04",
        "NH07 - NOB. FUNDER 0260 AREZZO": "NH07",
        "NH22 - NOB. CLEAF SABLE' VALLEY LR22": "NH22",
        "NH26 - NOB. CLEAF ARES FB11 BETON": "NH26",
        "NH28 - NOB. PFLEIDERER R42033 ML": "NH28",
        "NH33 - NOB. KAINDL K4949 AT SPRUCE ANT EXP": "NH33",
        "NH34 - NOB. PFLEIDERER U11209ML": "NH34",
        "NH35 - NOB. LEGNOPAN 09 ROVERE SEGATO": "NH35",
        "NH36 - NOB. NERO PFLEIDERER U12000 MP": "NH36",
        "NH39 - NOB. CLEAF MILLENIUM S083 NAGOLD": "NH39",
        "NH64 - NOB. EGGER W1000ST19 B.CO PREMIUM": "NH64",
        "NH68 - NOB. FUNDERMAX 0921 SU BROWN SILVER": "NH68",
        "NH69 - NOB. PFLEIDERER U12018SD GRIGIO B.": "NH69",
        "NH82 - NOB. BIANCO TRAFFICO SDW10140": "NH82",
        "NH85 - NOB. CLEAF S160 OKOBO": "NH85",
        "NH92 - NOB. ROV.MILANO R20095 NW": "NH92",
        "NH94 - NOB. FUNDERMAX VERDE MEDIO 0041": "NH94",
        "NH97 - NOB. PFLEIDERER BLU CRISTAL U18003": "NH97",
        "NU50 - NOB. EGGER U504 ST BLU": "NU50",
        "NU60 - NOB. EGGER H3303": "NU60",
        "NU65 - NOB. EGGER H3152 ROV VICEN SBIA ST19": "NU65",
        "NU66 - NOB. PFLEIDERER U15190 SD-CUVO": "NU66",
        "NU67 - NOB. PFLEIDERER U16000 SD-GR.TARTUFO": "NU67",
        "NU68 - NOB. SM'ART 4565 OLMO MIELE": "NU68",
        "NU69 - NOB. KRONO ABETE D79841": "NU69",
        "NU71 - NOB. KRONOSPAN D4823VL": "NU71",
        "NU76 - NOB. LEGNOPAN 111 FIN ROV 19POR NAT": "NU76",
        "N001 - NOB. NOCE PADANO": "N001",
        "N003 - NOB. GRIGIO CENERE O335": "N003",
        "N004 - NOB. GRIGIO SILICIO 0357": "N004",
        "N005 - NOB. GRIG ANTRACIT PFLEIDERER U12231": "N005",
        "N006 - NOB. BIANCO": "N006",
        "N013 - NOB. ACERO NATURALE": "N013",
        "N018 - NOB. NERO FIN CERA": "N018",
        "N391 - NOB. OLMO LEONE N391": "N391",
        "N457 - NOB. PFLEIDERER U12115": "N457",
        "N500 - NOB. PFLEIDERER R42006 ML CIL.HAVAN": "N500",
        "N538 - NOB. PFLEID.R20128 ROVERE SON.F.RU": "N538",
        "N554 - NOB. THERMOPAL U508 GRIGIO": "N554",
        "N585 - NOB. THERMO U506 ANTR.MP CERA OPACO": "N585",
        "N589 - NOB. EGGER U332 ARANCIO": "N589",
        "N594 - NOB. EGGER H1145 ROVERE BARDOL": "N594",
        "N640 - NOB. THERMOPAL SR 209/01 B.LUC": "N640",
        "N656 - NOB. THERMOPAL SV 140 BIANCO LUCIDO": "N656",
        "N675 - NOB. THERM.U018(47) GRIGIO": "N675",
        "N698 - NOB. THERM.F21/005 OLIVO SPAGNA": "N698",
        "N744 - NOB. THERM R20031 RU": "N744",
        "N748 - NOB. PFLEIDERER U12179 GRIGIO": "N748",
        "N750 - NOB. R20038 ROVERE CHALET NAT.P": "N750",
        "N759 - NOB. EGGER ROV. HALIFAX H1180 ST37": "N759",
        "N765 - NOB. EGGER H1487 ST22 ABETE": "N765",
        "N768 - NOB. ROV. MILANO R20095MO": "N768",
        "N769 - NOB. OLMO LEONE PLEID.R37009 MW": "N769",
        "N897 - NOB. THERMOPAL U00059 BLU": "N897",
        "N946 - NOB. TERMOPAL U00225 47 PERL ROSSO": "N946",
        "N957 - NOB. MAGNOLIA LIGNOLUX 312 ANNOVATI": "N957",
        "N963 - NOB. GRIGIO CHIARO THERM.U1131": "N963",
    },
    "TRUCIOLARE": {
        "RAW - TRUCIOLARE GREZZO": "RAW",
        "IDRO - TRUCIOLARE IDROFUGO": "IDRO"
    }
}

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
# 2. INTERFACCIA UTENTE (v9.5 - Ragionamento Ragionato)
# =========================================================

# --- INIZIALIZZAZIONE VARIABILI DI STATO ---
uni_en_1090_active = False 
mat_en, part_en, normativa, tag_suggerimento = "", "", "", ""
extra_dedicati_dict = {}
extra_selezionati = []
blocco_incompatibilita = False 
mat_it = None # Inizializzazione di sicurezza

# Configurazione Immagine e Testo
LARGHEZZA_IMMAGINE = 600 
TESTO_MANUALE = """
**PROCEDURA STANDARD:**
1. **CATEGORIA**: Scegli a sinistra.
2. **MATERIALE/COMP**: Scegli i parametri tecnici.
3. **DETTAGLIO**: Scegli il pezzo e le finiture (Dinamiche).
4. **QUOTE**: Inserisci i valori.
5. **GENERA**: Crea la stringa finale.
"""

st.title("⚙️ REG - Title Generator & Classification")

# --- TASTO AZZERA SUPERIORE ---
c1, c2, c3 = st.columns([2, 1, 2])
with c2:
    st.button("🔄 AZZERA TUTTO", on_click=activate_reset, use_container_width=True, key="btn_top_global")

st.markdown("---")

# --- LAYOUT PRINCIPALE ---
col_left, col_workarea = st.columns([1, 3], gap="large")

with col_left:
    st.subheader("📂 1. Categoria")
    macro_it = st.radio("Seleziona categoria:", options=list(DATABASE.keys()), key="radio_macro_main", label_visibility="collapsed")
    st.markdown("---")
    st.info(TESTO_MANUALE)

# =========================================================
# 2. INTERFACCIA UTENTE (v9.7 - INTEGRALE & STABILE)
# =========================================================

# --- 2.1 FUNZIONI DI SUPPORTO & STATO ---
def activate_reset():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Inizializzazione variabili di sicurezza
uni_en_1090_active = False 
mat_en, part_en, normativa = "", "", ""
extra_selezionati = []
blocco_incompatibilita = False 
LARGHEZZA_IMMAGINE = 600 

st.title("⚙️ REG - Title Generator & Classification")

# --- 2.2 TASTO AZZERA ---
c1, c2, c3 = st.columns([2, 1, 2])
with c2:
    st.button("🔄 AZZERA TUTTO", on_click=activate_reset, use_container_width=True, key="global_reset_btn")

st.markdown("---")

# --- 2.3 LAYOUT SIDEBAR / AREA LAVORO ---
# Definiamo le colonne che prima mancavano nel tuo codice
col_left, col_workarea = st.columns([1, 3], gap="large")

with col_left:
    st.subheader("📂 1. Categoria")
    macro_it = st.radio(
        "Seleziona categoria:", 
        options=list(DATABASE.keys()), 
        key="radio_macro_main", 
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.info("""
    **ISTRUZIONI:**
    1. Scegli Categoria.
    2. Definisci il Materiale.
    3. Seleziona il Pezzo.
    4. Scegli la Finitura.
    5. Inserisci le Quote.
    """)

# --- 2.4 AREA DI LAVORO CENTRALE ---
with col_workarea:
    st.subheader("🛠️ 2. Materiale e Compatibilità")
    
    c_mat, c_comp = st.columns([1, 1.5])
    
    with c_mat:
        if macro_it == "ASSEMBLY":
            st.toggle("ASSEMBLATO (Prefisso)", key="check_assembled")
            st.toggle("🎨 ATTIVA FINITURE MULTIPLE", key="check_fin_multi_toggle")
            mat_it = "ASSEMBLY"
        else:
            materiali_disponibili = MATERIALI_CONFIG.get(macro_it, {})
            if materiali_disponibili:
                # Key dinamica per evitare conflitti tra categorie
                mat_it = st.radio(
                    f"Materiale {macro_it}:", 
                    options=list(materiali_disponibili.keys()), 
                    horizontal=True, 
                    key=f"radio_mat_{macro_it}"
                )
                mat_en = materiali_disponibili[mat_it]

    with c_comp:
        if macro_it != "FASTENER":
            pills_opts = [opt for opt in OPZIONI_COMPATIBILITA if opt]
            comp_selezionata = st.pills("Modello Compatibilità:", options=pills_opts, selection_mode="single", key="comp_tags_pills")
            
            if comp_selezionata in ["FORTISSIMO", "MINIRACK"]:
                st.warning("⚡ Strutturale")
                uni_en_1090_active = st.toggle("Certificazione UNI EN-1090", key="check_1090_toggle")

    st.markdown("---")
    
    # --- SEZIONE 3: SELEZIONE PARTICOLARE E FINITURE ---
    st.subheader("🔧 3. Dettaglio e Caratteristiche")
    
    part_dict = DATABASE[macro_it]["Particolari"]
    scelta_part_it = st.selectbox(
        "Cerca o seleziona dettaglio:", 
        options=sorted(list(part_dict.keys())), 
        index=None,
        placeholder="Scrivi qui per cercare il componente...",
        format_func=lambda x: f"🔧 {x} ({part_dict[x][0]})" if x else "Seleziona...",
        key="selectbox_part_final"
    )

    # --- LOGICA FINITURE UNIVERSALE ---
    if scelta_part_it:
        if macro_it == "WOODCOMP":
            # Uniamo tutte le finiture in una lista unica
            tutte_le_finiture = {}
            for categoria in FINITURE_LEGNO.values():
                tutte_le_finiture.update(categoria)
            
            st.markdown("---")
            st.selectbox(
                "🎨 Catalogo Finiture (Laminati / Nobilitati / Truciolati):",
                options=["-"] + sorted(list(tutte_le_finiture.keys())),
                key="fin_wood_select",
                index=0,
                help="Cerca qui la finitura."
            )

        elif macro_it == "ASSEMBLY" and st.session_state.get("check_fin_multi_toggle"):
            st.markdown("---")
            st.info("🎨 Configurazione Finiture Multiple")
            all_fin_ass = {}
            for sub in FINITURE_LEGNO.values(): all_fin_ass.update(sub)
            
            fa1, fa2, fa3 = st.columns(3)
            with fa1: st.selectbox("Finitura 1", ["-"] + sorted(list(all_fin_ass.keys())), key="ass_fin_1")
            with fa2: st.selectbox("Finitura 2", ["-"] + sorted(list(all_fin_ass.keys())), key="ass_fin_2")
            with fa3: st.selectbox("Finitura 3", ["-"] + sorted(list(all_fin_ass.keys())), key="ass_fin_3")

        st.markdown("---")
        
        # --- GESTIONE EXTRA ---
        dati_part = part_dict[scelta_part_it]
        part_en = dati_part[0]
        extra_dedicati_dict = dati_part[1]
        
        extra_options = list(extra_dedicati_dict.keys())
        if extra_options:
            extra_selezionati = st.pills("Caratteristiche:", options=extra_options, selection_mode="multi", key="extra_tags_final")
            
            for ex in (extra_selezionati or []):
                if ex in SUB_OPTIONS_CONFIG:
                    st.selectbox(f"↳ Variante {ex}:", options=list(SUB_OPTIONS_CONFIG[ex].keys()), key=f"sub_{ex}")
                elif ex in EXTRA_CON_INPUT_MANUALE:
                    st.text_input(f"↳ Valore {ex}:", key=f"manual_{ex}")

    st.text_input("Note libere (Traduzione automatica):", key="extra_text_input").strip()

    st.markdown("---")
    
    # --- SEZIONE 4: DIMENSIONAMENTO ---
    st.subheader("📏 4. Dimensionamento")
    col_campi, col_immagine = st.columns([1, 1.5], gap="medium")

    with col_campi:
        if macro_it == "FASTENER":
            st.text_input("Lunghezza (L)", key="dim_l")
            st.text_input("Diametro (D/M)", key="dim_dia")
            opzioni_norm = MAPPA_NORMATIVE_FASTENER.get(scelta_part_it, {"": ""})
            norma_scelta = st.selectbox("Normativa", options=list(opzioni_norm.keys()), key="norm_fast")
            normativa = opzioni_norm[norma_scelta] if norma_scelta else ""
        else:
            st.text_input("Lunghezza (L)", key="dim_l")
            st.text_input("Profondità (P)", key="dim_p")
            st.text_input("Altezza (H)", key="dim_h")
            st.text_input("Diametro (Ø)", key="dim_dia_gen")
            
    with col_immagine:
        st.image(
            "https://raw.githubusercontent.com/wAsp191/generatetext/main/Gemini_Generated_Image_rtac8jrtac8jrtac%20(1).png", 
            caption="Riferimento Quote", 
            width=LARGHEZZA_IMMAGINE
        )
        
# =========================================================
# 3. LOGICA DI GENERAZIONE E TRADUZIONE (v9.2 - Fix Finiture)
# =========================================================

st.divider()

if 'stringa_editabile' not in st.session_state:
    st.session_state['stringa_editabile'] = ""

# --- A. CONTROLLO ERRORI ---
errori_rilevati = []
if extra_selezionati:
    for coppia in COPPIE_INCOMPATIBILI:
        if coppia.issubset(set(extra_selezionati)):
            errori_rilevati.append(f"⚠️ **Incongruenza:** {list(coppia)[0]} e {list(coppia)[1]} non compatibili.")

for errore in errori_rilevati:
    st.error(errore)

blocco_genera = len(errori_rilevati) > 0

# --- B. TASTO DI GENERAZIONE ---
if st.button("🚀 GENERA STRINGA FINALE", use_container_width=True, disabled=blocco_genera):
    if not scelta_part_it:
        st.error("⚠️ Seleziona un particolare prima di generare!")
    else:
        # 1. GESTIONE DIMENSIONI
        dim_parts = []
        if macro_it == "FASTENER":
            d_val = st.session_state.get("dim_dia", "").strip().upper()
            l_val = st.session_state.get("dim_l", "").strip().upper()
            if d_val:
                pfx = "" if d_val.startswith('M') else "D"
                dim_parts.append(f"{pfx}{d_val}")
            if l_val: dim_parts.append(f"L{l_val}")
            dim_final = "X".join(dim_parts)
            if normativa: dim_final += f" {normativa}"
        else:
            l_v = st.session_state.get("dim_l", "").strip().upper()
            p_v = st.session_state.get("dim_p", "").strip().upper()
            h_v = st.session_state.get("dim_h", "").strip().upper()
            dia_v = st.session_state.get("dim_dia_gen", "").strip().upper()
            
            lph = []
            if l_v: lph.append(f"L{l_v}")
            if p_v: lph.append(f"P{p_v}")
            if h_v: lph.append(f"H{h_v}")
            
            dim_final = " ".join(lph)
            if dia_v: dim_final += f" Ø{dia_v}"

        # 2. GESTIONE FINITURE (LOGICA AGGIORNATA)
        sigle_finiture = []
        
        # Controlliamo il nuovo key del toggle
        if st.session_state.get("check_fin_multi_toggle"):
            if macro_it == "WOODCOMP":
                val_scelto = st.session_state.get("fin_wood_select_unique") # Nuova key
                if val_scelto and val_scelto != "-" and val_scelto in FINITURE_LEGNO:
                    sigle_finiture.append(FINITURE_LEGNO[val_scelto])
            
            elif macro_it == "ASSEMBLY":
                for i in range(1, 4):
                    f_val = st.session_state.get(f"ass_fin_{i}_new") # Nuova key
                    if f_val and f_val != "-" and f_val in FINITURE_LEGNO:
                        sigle_finiture.append(FINITURE_LEGNO[f_val])
        
        stringa_finiture = "/".join(sigle_finiture) if sigle_finiture else ""

        # 3. EXTRA (PILLS)
        pills_tradotte = []
        for ex in list(extra_dedicati_dict.keys()):
            if extra_selezionati and ex in extra_selezionati:
                base = extra_dedicati_dict.get(ex, ex.upper())
                if ex in SUB_OPTIONS_CONFIG:
                    sub_v = st.session_state.get(f"sub_{ex}", "")
                    trad = SUB_OPTIONS_CONFIG[ex].get(sub_v, "")
                    pills_tradotte.append(f"{base} {trad}".strip())
                elif ex in EXTRA_CON_INPUT_MANUALE:
                    man_v = st.session_state.get(f"manual_{ex}", "").strip().upper()
                    pills_tradotte.append(f"{base} {man_v}" if man_v else base)
                else:
                    pills_tradotte.append(base)

        pre = [p for p in pills_tradotte if any(term in p for term in TERMINI_ANTICIPATI)]
        suf = [p for p in pills_tradotte if p not in pre]
        
        pre_str = " ".join(pre)
        suf_str = " ".join(suf)

        # 4. TRADUZIONE NOTE LIBERE
        note_it = st.session_state.get("extra_text", "").strip().lower()
        note_en = ""
        if note_it:
            for ita, eng in GLOSSARIO_TECNICO.items():
                note_it = note_it.replace(ita, eng)
            try:
                from deep_translator import GoogleTranslator
                note_en = GoogleTranslator(source='it', target='en').translate(note_it).upper()
            except:
                note_en = note_it.upper()

        # 5. ASSEMBLAGGIO FINALE
        m_pfx = mat_en if not (mat_en == "METAL" and "METAL" in part_en.upper()) else ""
        
        # Schema: MATERIALE + PREFISSI + NOME + MISURE + SUFFISSI + FINITURE
        parti_corpo = [m_pfx, pre_str, part_en, dim_final, suf_str, stringa_finiture]
        corpo = " ".join([p for p in parti_corpo if p and p.strip()]).replace("  ", " ").strip()
        
        if note_en:
            corpo = f"{corpo}, {note_en}"

        comp_tags = st.session_state.get("comp_tags", "")
        res = f"{corpo} - {comp_tags}" if comp_tags else corpo

        # Pulizia Grammaticale
        res = res.upper().replace("WITH WITH", "WITH")
        if res.count("WITH") > 1:
            bits = res.split("WITH")
            res = bits[0] + "WITH" + " AND".join(bits[1:])

        # Prefissi Speciali
        if uni_en_1090_active: res = f"UNI EN-1090 - {res}"
        if macro_it == "ASSEMBLY" and st.session_state.get("check_assembled"):
            res = f"ASSEMBLED - {res}"

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
