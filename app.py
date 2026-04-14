import streamlit as st
from deep_translator import GoogleTranslator

# =========================================================
# 0. CONFIGURAZIONE PAGINA E LOGICA RESET
# =========================================================
st.set_page_config(page_title="Technical Generator v8.8", layout="wide")

def activate_reset():
    keys_to_reset = [
        'dim_l', 'dim_p', 'dim_h', 'dim_dia', 'dim_dia_gen', 'dim_s',
        'extra_text', 'selectbox_part', 'comp_tags', 'extra_tags',
        'stringa_editabile', 'check_1090', 'check_assembled',
        'cat_wood', 'fin_wood', 'cat_as_1', 'fin_as_1', 
        'cat_as_2', 'fin_as_2', 'cat_as_3', 'fin_as_3', 'show_finishes_assembly'
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            if key == 'comp_tags': st.session_state[key] = None 
            elif key == 'extra_tags': st.session_state[key] = []
            elif key in ['check_1090', 'check_assembled', 'show_finishes_assembly']: st.session_state[key] = False
            elif key == 'selectbox_part': st.session_state[key] = None
            else: st.session_state[key] = ""
    for key in list(st.session_state.keys()):
        if key.startswith("manual_") or key.startswith("sub_"):
            st.session_state[key] = ""
    st.toast("Interfaccia pulita!", icon="✨")

# =========================================================
# 1. DIZIONARI E DATABASE (ESTESI)
# =========================================================

DB_FINITURE_LEGNO = {
    "LAMINATO": [
        "", "LE04 - LAM R20064 ROVERE", "LE06 - LAM. PFLEIDERER U16002W TORTORA", 
        "LE11 - LAM. KASTAMONU A847 ALASKA", "LE15 - LAM ANTIGR THERMOP U12231 PFLEDERER", 
        "LE24 - LAM. ROV. MILANO R20095MO", "LE27 - CLEAF SHERWOOD S073SJP", 
        "LE40 - LAM. KAINDL 37744 BIANCO", "LE42 - LAM. KAINDL 37777 FRASSINO COIMBRA", 
        "LE63 - LAM. ROV. MILANO R20095 ML", "LE73 - LAM. ROVERE KRONO D4225 OV", 
        "LE79 - LAM PFLEIDERER F76044 SD - GRIGIO", "LE86 - LAM EUREKA OAK DA1 FIN.EVO", 
        "LH06 - LAM. FUNDER 0260 AREZZO", "LH23 - LAM. CLEAF SABLE' VALLEY LR22", 
        "LH27 - LAM. CLEAF ARES FB11 BETON", "LH29 - LAM. PFLEIDERER R42033 ML", 
        "LH37 - LAM. CLEAF MONTILLA FC 18", "LH38 - LAM. CLEAF MILLENIUM S083 NAGOLD", 
        "LH40 - LAM. SAIB CH3013 GRIGIO GRAFITE", "LH62 - LAM. CLEAF PIOMBO HM07", 
        "LH64 - LAM. EGGER W1000ST19 B.CO PREMIUM", "LH81 - LAM. EGGER H3331 ST15 HYDROFUGE", 
        "LH83 - LAM. BIANCO TRAFFICO SDW10140", "LH95 - LAM. PFLEIDERER ROVERE R20099", 
        "LH98 - LAM. PFLEIDERER BLU CRISTAL U18003", "LH99 - LAM. SM'ART 4565 OLMO MIELE", 
        "LTH1 - LAM. THERMOPAL U506 ANTRHAZIT", "LU51 - LAM. AMET.U504 ST BLU", 
        "LU61 - LAM. EGGER H3303", "LU62 - LAM. ABET LAMINATI 1860PRINT", 
        "LU63 - LAM. GREENLAM 5049 - SUEDE RED OAK", "LU64 - LAM. EGGER H3152 ROV VICEN SBIA ST19", 
        "LU71 - LAM. KRONOSPAN D4823VL", "LU73 - LAM. ABET PRINT 1832 F. SEI", 
        "LU74 - LAM. FORMICA K 1238 UN", "LU75 - LAM. LEGNOPAN 111 FIN ROV 19POR NAT", 
        "L035 - LAM. PRINT 421 SEI NERO", "L036 - LAM. ABET PRINT FIN. 460 SEI VERDE", 
        "L039 - LAM. PRINT 871 SEI GRIGIO CENE", "L040 - LAM. PRINT 475 SEI GRIGIO SILICIO", 
        "L041 - LAM. PRINT 411 SEI BIANCO", "L386 - LAM. OLMO LEONE PLEID.R37009 MO", 
        "L406 - LAM. PRINT 406 BIANCO", "L410 - LAM. ABET PRINT 410 SEI BIANCO", 
        "L418 - LAM. PRINT 418 SEI BIANCO", "L428 - LAM. PRINT 428 SEI BLU", 
        "L466 - LAM. PHOENIX F76026 MARRONE CR PFL", "L469 - LAM. PRINT 469 SEI GIALLO", 
        "L559 - LAM. FUNDERMAX 0921 SU BROWN SILVER", "L563 - LAM. PRINT 563 MANDARIN GRIGIO", 
        "L578 - LAM. ROVERE BARDOLINO", "L579 - LAM. PFLEID.R20128 ROVERE SON.F.RU", 
        "L590 - LAM. EGGER U332 ARANCIO", "L641 - LAM. THERMOPAL SR 209/01 B.LUC", 
        "L696 - LAM. THERM.F21/005 OLIVO SPAGN CHIA", "L716 - LAM. THERMOPAL U018(47) GRIGIO", 
        "L745 - LAM. THER R20031RU L745", "L752 - LAM. PFLEIDERER W10003 MP BIANCO", 
        "L767 - LAM. EGGER ROV.HALIFAX H1180 ST37", "L786 - LAM. PRINT 1677 ACERO EX PURICELLI", 
        "L814 - LAM. ABET 1666 FIN SEI DUE FAGGIO", "L833 - LAM. PRINT 2810 CLIMB", 
        "L835 - LAM. PRINT 835 SEI ARANCIO", "L852 - LAM. PRINT 852 SEI BLU", 
        "L873 - LAM. PRINT 873 FIN SATINATA", "L879 - LAM. PRINT 879 SEI GRIGIO ANTRACITE"
    ],
    "NOBILITATO": [
        "", "LU70 - NOB. KRONO ABETE D79841", "NE05 - NOB. PFLEIDERER U16002W TORTORA", 
        "NE12 - NOB. KASTAMONU A847 ALASKA", "NE19 - NOB. EGGER W911 BIANCO ST15", 
        "NE28 - NOB. CLEAF SHERWOOD S073 S.J.P.", "NE38 - NOB. KAINDL 34140 RV ROV.SANREMO CL", 
        "NE41 - NOB. KAINDL 37777 FRASSINO COIMBRA", "NE46 - NOB. PFLEIDERER U19008 VERDE SCURO", 
        "NE62 - NOB. 256 H1145 ST10 CHENE BARDOLINO", "NE67 - NOB. ROVERE GLADST H3309 ST28", 
        "NE70 - NOB. GRAPHITE U961 ST9", "NE74 - NOB. ROVERE KRONO D4225 OV A", 
        "NE75 - NOB. EGGER H3156 ROV.CORB.GR", "NE88 - NOB. CLEAF UA32 TALCO GRIGIO", 
        "NE91 - NOB. PFLEIDERER PHOENIX F76026", "NE99 - NOB. PFLEIDERER R20099", 
        "NH01 - NOB. R20065 ROVERE MONTAGNA SCURO", "NH03 - NOB. EGGER GLADSTONE BIANCO H3335", 
        "NH04 - NOB. FUNDER 0290 NA ROVERE SBIA", "NH07 - NOB. FUNDER 0260 AREZZO", 
        "NH22 - NOB. CLEAF SABLE' VALLEY LR22", "NH26 - NOB. CLEAF ARES FB11 BETON", 
        "NH28 - NOB. PFLEIDERER R42033 ML", "NH33 - NOB. KAINDL K4949 AT SPRUCE ANT EXP", 
        "NH34 - NOB. PFLEIDERER U11209ML", "NH35 - NOB. LEGNOPAN 09 ROVERE SEGATO", 
        "NH36 - NOB. NERO PFLEIDERER U12000 MP", "NH39 - NOB. CLEAF MILLENIUM S083 NAGOLD", 
        "NH64 - NOB. EGGER W1000ST19 B.CO PREMIUM", "NH68 - NOB. FUNDERMAX 0921 SU BROWN SILVER", 
        "NH69 - NOB. PFLEIDERER U12018SD GRIGIO B.", "NH82 - NOB. BIANCO TRAFFICO SDW10140", 
        "NH85 - NOB. CLEAF S160 OKOBO", "NH92 - NOB. ROV.MILANO R20095 NW", 
        "NH94 - NOB. FUNDERMAX VERDE MEDIO 0041", "NH97 - NOB. PFLEIDERER BLU CRISTAL U18003", 
        "NU50 - NOB. EGGER U504 ST BLU", "NU60 - NOB. EGGER H3303", 
        "NU65 - NOB. EGGER H3152 ROV VICEN SBIA ST19", "NU66 - NOB. PFLEIDERER U15190 SD-CUVO", 
        "NU67 - NOB. PFLEIDERER U16000 SD-GR.TARTUFO", "NU68 - NOB. SM'ART 4565 OLMO MIELE", 
        "NU69 - NOB. KRONO ABETE D79841", "NU71 - NOB. KRONOSPAN D4823VL", 
        "NU76 - NOB. LEGNOPAN 111 FIN ROV 19POR NAT", "N001 - NOB. NOCE PADANO", 
        "N003 - NOB. GRIGIO CENERE O335", "N004 - NOB. GRIGIO SILICIO 0357", 
        "N005 - NOB. GRIG ANTRACIT PFLEIDERER U12231", "N006 - NOB. BIANCO", 
        "N013 - NOB. ACERO NATURALE", "N018 - NOB. NERO FIN CERA", "N391 - NOB. OLMO LEONE N391", 
        "N457 - NOB. PFLEIDERER U12115", "N500 - NOB. PFLEIDERER R42006 ML CIL.HAVAN", 
        "N538 - NOB. PFLEID.R20128 ROVERE SON.F.RU", "N554 - NOB. THERMOPAL U508 GRIGIO", 
        "N585 - NOB. THERMO U506 ANTR.MP CERA OPACO", "N589 - NOB. EGGER U332 ARANCIO", 
        "N594 - NOB. EGGER H1145 ROVERE BARDOL", "N640 - NOB. THERMOPAL SR 209/01 B.LUC", 
        "N656 - NOB. THERMOPAL SV 140 BIANCO LUCIDO", "N675 - NOB. THERM.U018(47) GRIGIO", 
        "N698 - NOB. THERM.F21/005 OLIVO SPAGNA", "N744 - NOB. THERM R20031 RU", 
        "N748 - NOB. PFLEIDERER U12179 GRIGIO", "N750 - NOB. R20038 ROVERE CHALET NAT.P", 
        "N759 - NOB. EGGER ROV. HALIFAX H1180 ST37", "N765 - NOB. EGGER H1487 ST22 ABETE", 
        "N768 - NOB. ROV. MILANO R20095MO (ex NH92)", "N769 - NOB. OLMO LEONE PLEID.R37009 MW", 
        "N897 - NOB. THERMOPAL U00059 BLU", "N946 - NOB. TERMOPAL U00225 47 PERL ROSSO", 
        "N957 - NOB. MAGNOLIA LIGNOLUX 312 ANNOVATI", "N963 - NOB. GRIGIO CHIARO THERM.U1131"
    ],
    "TRUCIOLARE": ["", "RAW - TRUCIOLARE GREZZO", "IDRO - TRUCIOLARE IDROFUGO"]
}

COPPIE_INCOMPATIBILI = [
    {"Statico", "Antisismico"}, {"Angolo aperto", "Angolo chiuso"}, {"Portante", "Non portante"},
    {"Singolo", "Doppio"}, {"Per ripiano in vetro", "Per ripiano in legno"}, {"Con serratura", "Senza serratura"},
    {"Passo 25", "Passo 50"}, {"L50", "L55"}, {"Scorrevoli", "A saracinesca"},
    {"Per attacco montante", "Per attacco fiancata"}, {"Superiore", "Tra ripiani di base"},
    {"Dritto", "Inclinato"}, {"Cromato", "Verniciato"}, {"Multibarra", "Multilame", "In rete"},
    {"Profilo a L", "Profilo a U"}, {"Per ripiano di base", "Per fiancata"},
    {"Liscio", "Liscia", "Forato", "Forata", "In filo"}, {"Terminale", "Centrale"}, {"Zincato", "Verniciata"},
]

GLOSSARIO_TECNICO = {
    "mensola": "BRACKET", "mensole": "BRACKETS", "gondola": "GONDOLA", "spalla": "FRAME",
    "innesto": "COUPLING", "montante": "UPRIGHT", "per": "FOR", "losanga": "LOSANGA"
}

SUB_OPTIONS_CONFIG = {
    "VPA (+)": {"Serie S": "S SERIES", "Serie SS": "SS SERIES", "Serie M": "M SERIES", "Serie L": "L SERIES"},
    "Con distanziale (+)": {"L100": "L100", "L150": "L150", "L200": "L200", "L250": "L250"},
    "Numero diagonali (+)": {"Doppie": "DD", "Triple": "TD", "Quadruple": "QD"},
    "Sezione (+)": {"L55": "L55", "L80 Z/S": "L80 Z/S", "L80 Z/M": "L80 Z/M", "L100 Z/S": "L100 Z/S", "L100 Z/M": "L100 Z/M", "L120 Z/S": "L120 Z/S", "70X30": "70X30", "90X30": "90X30"},
    "Tipologia di mensola (+)": {"Mensola saldata a filo superiore": "UPPER BRACKET", "Mensola saldata a filo inferior": "LOWER BRACKET"},
    "Compatibilità piede di base (+)": {"Per piede H90": "FOR H90 BASE FOOT", "Per piede H100": "FOR H100 BASE FOOT", "Per piede H150": "FOR H150 BASE FOOT"},
    "Attacco gancio (+)": {"Attacco barra": "HOOK FOR BAR", "Attacco multilame": "HOOK FOR MULTISRIP", "Attacco pannello forato": "HOOK FOR SLOTTED PANEL"},
    "Orientamento (+)": {"Destra": "RIGHT", "Sinistra": "LEFT"},
    "Posizioni multiple (+)": {"1 posizione": "1 POSITION", "2 posizioni": "2 position", "3 posizioni": "3 POSITION"},
    "Altezza piede (+)": {"H90": "H90", "H100": "H100", "H150": "H150"},
    "Predisposto per montante (+)": {"L80": "FOR L80 UPRIGHT", "L100/L120": "FOR L100/L120 UPRIGHT"},
    "Numero tasche (+)": {"1 Tasca": "1 POCKET", "2 Tasche": "2 POCKETS"}   
}

EXTRA_CON_INPUT_MANUALE = ["Sezione circolare", "Sezione quadrata"]

MATERIALI_CONFIG = {
    "METAL COMP": {"METAL": "METAL", "ZINCATO": "GALVANIZED", "INOX": "STAINLESS STEEL", "ALLUMINIO": "ALUMINIUM"},
    "WOOD COMP": {"LAMINATO": "LAMINATED", "NOBILITATO": "MELAMINE", "TRUCIOLARE": "OSB"},
    "PLASTIC COMP": {"POLICARBONATO": "POLYCARBONATE", "PVC": "PVC", "GOMMA": "RUBBER"},
    "GLASS COMP": {"VETRO TEMPRATO": "TEMPERED", "VETRO SATINATO": "SATIN"},
    "FASTENER": {"ZINCATO": "GALVANIZED", "BRUNITO": "BURNISHED", "NERO": ""}
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
            "Pannello frontale": ["FRONT PANEL", {"Forato": "PERFORATED", "Aggangio montante": "HOOK ONTO UPFRIGHT"}, "PANEL"],
            "Adattatore": ["ADAPTER", {"Forato": "PERFORATED", "Aggangio montante": "HOOK ONTO UPFRIGHT", "Passo 25": "PITCH 25", "Passo 50": "PITCH 50", "L50": "L50", "L55": "L55"}, "ADAPTER"],
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
    "ASSEMBLY": {
        "macro_en": "ASSEMBLY",
        "Particolari": {
            "Vetrina": ["SHOWCASE", {"Terminale": "END", "Centrale": "CENTRAL", "Con illuminazione": "WITH LIGHTING", "Con ante scorrevoli": "WITH SLIDING DOOR"}, "SHOWCASE"],
            "Espositore": ["DISPLAY", {"Mobile": "MOBILE", "Per alimenti": "FOR FOOD"}, "DISPLAY"],
            "Totem": ["TOTEM", {"Mobile": "MOBILE", "Rotante": "ROTATING", "Per casse automatiche": "FOR SELF PAY"}, "DISPLAY"],
            "Spalla": ["FRAME", {"Numero diagonali (+)": "", "Antisismico": "SEISMIC-RESISTANT", "Sezione (+)": "", "Zincato": "GALVANIZED", "Verniciata": "POWEDR COATED"}, "FRAME"],
            "Controventatura": ["CROSS-BRACING", {"Gondola": "GONDOLA", "Sezione (+)": "", "Su due livelli": "TWO LEVELS", "Numero diagonali (+)": "", "Con distanziale (+)": "WITH SPACER"}, "CROSS-BRACING"],
            "Banco espositore di legno": ["WOODEN DESK", {"Con cassetto": "WITH DRAWER", "Con ruote": "WITH WHEELS"}, "DESK"],
            "Avancassa": ["IMPULSE UNIT", {"Con ripiani": "WITH SHELF", "Con ripiani inclinati": "WITH INCLINATED SHELF", "Con rete divisoria": "WITH DIVIDING NET", "Con ruote": "WITH WHEELS", "Con ganci": "WITH HOOKS", "Con batticarrello": "WITH TROLLEY BEATER"}, "DISPLAY"],
            "Cassettiera": ["CHEST OF DRAWERS", {"Con guide RAM": "WITH RAM GUIDE", "Attacco montante": "HOOK ONTO UPRIGHT"}, "DRAWER"],
            "Espositore riviste": ["DISPLAY FOR MAGAZINE", {"Numero tasche (+)": "", "Con portaprezzo in filo": "WITH PRIZE-HOLDER WIRE"}, "DISPLAY", "BOOK AND MAGAZINE"],
            "Cassa pagamento automatico": ["SELF CHECKOUT", {"Con macchine di pagamento": "WITH GLORY MACHINES PAYMENT"}, "SELF CHECKOUT (SCO)"]
        }
    }
}

OPZIONI_COMPATIBILITA = ["", "F25", "F25 BESPOKE", "F25 READY", "F50", "F50 BESPOKE", "F50 READY", "UNIVERSAL", "BC", "FORTISSIMO", "MINIRACK", "UNIMOB"]
TERMINI_ANTICIPATI = ["CENTRAL", "LEFT", "RIGHT", "REINFORCED", "INTERNAL", "EXTERNAL", "STATIC", "ADJUSTABLE", "SEISMIC", "MULTIBAR", "MULTISTRIP", "TOP", "INTER-BASE SHELF", "ROUNDED", "SLOPING", "SHAPED", "CONNECTING", "SHUTTER", "COUPLING", "WIRE", "GRIPPED", "CHROMED", "PAINTED", "MESH", "SLIDING", "CURVED", "STRAIGHT", "MILLING", "WIRE-BASKET", "SEMICIRCULAR", "SINGLE", "DOUBLE", "END", "L-SHAPED", "U-SHAPED", "SERRATED LOCK", "ROTATING", "CTR", "UPRIGHT-GRAFT"]

# =========================================================
# 3. INTERFACCIA UTENTE
# =========================================================

st.title("⚙️ REG - Title Generator & Classification")

# Tasto Azzera
c1, c2, c3 = st.columns([2, 1, 2])
with c2: st.button("🔄 AZZERA TUTTO", on_click=activate_reset, use_container_width=True)

st.markdown("---")
col_left, col_workarea = st.columns([1, 3], gap="large")

with col_left:
    st.subheader("📂 1. Categoria")
    macro_it = st.radio("Seleziona categoria:", options=list(DATABASE.keys()), key="radio_macro", label_visibility="collapsed")
    st.markdown("---")
    st.info("**NOTE:**\n* Prefissi L-P-H automatici.\n* Max 100 caratteri.")

with col_workarea:
    st.subheader("🛠️ 2. Materiale e Compatibilità")
    c_mat, c_comp = st.columns([1, 1.5])
    
    with c_mat:
        mat_en = ""
        if macro_it == "ASSEMBLY":
            st.toggle("ASSEMBLATO", key="check_assembled")
            # --- NUOVA MODIFICA: SPUNTA PER FINITURE ---
            show_finishes = st.toggle("Configura finiture legno per assieme", key="show_finishes_assembly")
        else:
            materiali_disponibili = MATERIALI_CONFIG.get(macro_it, {})
            if materiali_disponibili:
                mat_it = st.radio(f"Materiale:", options=list(materiali_disponibili.keys()), horizontal=True)
                mat_en = materiali_disponibili[mat_it]
            show_finishes = (macro_it == "WOOD COMP")

    with c_comp:
        comp_selezionata = st.pills("Modello Compatibilità:", options=[opt for opt in OPZIONI_COMPATIBILITA if opt], selection_mode="single", key="comp_tags")
        if any(m == comp_selezionata for m in ["FORTISSIMO", "MINIRACK"]):
            st.warning("⚡ Strutturale")
            st.checkbox("Certificazione UNI EN-1090", key="check_1090")

    st.markdown("---")
    part_dict = DATABASE[macro_it]["Particolari"]
    scelta_part_it = st.selectbox("Dettaglio Particular:", options=sorted(list(part_dict.keys())), index=None, placeholder="Seleziona particolare...", key="selectbox_part")

    # SEZIONE FINITURE CONDIZIONALE
    finitura_finale = ""
    if show_finishes:
        st.markdown("---")
        st.subheader("🎨 2b. Finiture Legno")
        if macro_it == "WOOD COMP":
            fcol1, fcol2 = st.columns(2)
            with fcol1: cat_f = st.selectbox("Categoria", list(DB_FINITURE_LEGNO.keys()), key="cat_wood")
            with fcol2:
                finitura_scelta = st.selectbox("Dettaglio", DB_FINITURE_LEGNO[cat_f], key="fin_wood")
                if finitura_scelta: finitura_finale = finitura_scelta
        else: # Se ASSEMBLY con spunta attiva
            scelte_finali_as = []
            acol1, acol2, acol3 = st.columns(3)
            with acol1:
                c1_cat = st.selectbox("Cat. 1", ["-"] + list(DB_FINITURE_LEGNO.keys()), key="cat_as_1")
                if c1_cat != "-":
                    c1_fin = st.selectbox("Finitura 1", DB_FINITURE_LEGNO[c1_cat], key="fin_as_1")
                    if c1_fin: scelte_finali_as.append(c1_fin)
            with acol2:
                c2_cat = st.selectbox("Cat. 2", ["-"] + list(DB_FINITURE_LEGNO.keys()), key="cat_as_2")
                if c2_cat != "-":
                    c2_fin = st.selectbox("Finitura 2", DB_FINITURE_LEGNO[c2_cat], key="fin_as_2")
                    if c2_fin: scelte_finali_as.append(c2_fin)
            with acol3:
                c3_cat = st.selectbox("Cat. 3", ["-"] + list(DB_FINITURE_LEGNO.keys()), key="cat_as_3")
                if c3_cat != "-":
                    c3_fin = st.selectbox("Finitura 3", DB_FINITURE_LEGNO[c3_cat], key="fin_as_3")
                    if c3_fin: scelte_finali_as.append(c3_fin)
            if scelte_finali_as: finitura_finale = " | ".join(scelte_finali_as)

    st.markdown("---")
    st.subheader("✨ 3. Extra e Dimensioni")
    extra_selezionati = []
    if scelta_part_it:
        dati_part = part_dict[scelta_part_it]
        part_en = dati_part[0]
        extra_dedicati_dict = dati_part[1]
        extra_options = list(extra_dedicati_dict.keys())
        if extra_options:
            extra_selezionati = st.pills("Opzioni:", options=extra_options, selection_mode="multi", key="extra_tags")
            for ex in extra_selezionati:
                if ex in SUB_OPTIONS_CONFIG:
                    st.selectbox(f"↳ Variante {ex}:", options=list(SUB_OPTIONS_CONFIG[ex].keys()), key=f"sub_{ex}")
                elif ex in EXTRA_CON_INPUT_MANUALE:
                    st.text_input(f"↳ Valore {ex}:", key=f"manual_{ex}")

    extra_libero = st.text_input("Note libere (IT):", key="extra_text").strip()
    
    c_d1, c_d2, c_d3, c_d4 = st.columns(4)
    with c_d1: dim_l = st.text_input("L", key="dim_l")
    with c_d2: dim_p = st.text_input("P", key="dim_p")
    with c_d3: dim_h = st.text_input("H", key="dim_h")
    with c_d4: dim_dia = st.text_input("Ø", key="dim_dia_gen")

# =========================================================
# 4. GENERAZIONE
# =========================================================

if st.button("🚀 GENERA STRINGA FINALE", use_container_width=True):
    if not scelta_part_it:
        st.error("Seleziona un particolare!")
    else:
        # Dimensioni
        d_parts = []
        if dim_l: d_parts.append(f"L{dim_l}")
        if dim_p: d_parts.append(f"P{dim_p}")
        if dim_h: d_parts.append(f"H{dim_h}")
        dim_str = " ".join(d_parts)
        if dim_dia: dim_str += f" Ø{dim_dia}"
        
        # Extra
        extra_pills_list = []
        for ex in (extra_selezionati or []):
            base_trans = extra_dedicati_dict.get(ex, ex.upper())
            if ex in SUB_OPTIONS_CONFIG:
                v_sub = st.session_state.get(f"sub_{ex}", "")
                extra_pills_list.append(f"{base_trans} {SUB_OPTIONS_CONFIG[ex].get(v_sub, '')}".strip())
            elif ex in EXTRA_CON_INPUT_MANUALE:
                v_man = st.session_state.get(f"manual_{ex}", "").strip().upper()
                extra_pills_list.append(f"{base_trans} {v_man}".strip())
            else:
                extra_pills_list.append(base_trans)
        
        pref = [ex for ex in extra_pills_list if ex in TERMINI_ANTICIPATI]
        suff = [ex for ex in extra_pills_list if ex not in pref]
        
        # Traduzione note
        note_tr = ""
        if extra_libero:
            try: note_tr = GoogleTranslator(source='it', target='en').translate(extra_libero).upper()
            except: note_tr = extra_libero.upper()

        # Composizione
        corpo = f"{mat_en} {' '.join(pref)} {part_en} {dim_str} {' '.join(suff)}".strip()
        if finitura_finale: corpo += f" {finitura_finale}"
        if note_tr: corpo += f", {note_tr}"
        
        final = f"{corpo} - {comp_selezionata}" if comp_selezionata else corpo
        st.code(final.upper().replace("  ", " "), language="text")
