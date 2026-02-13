import streamlit as st
from deep_translator import GoogleTranslator

# =========================================================
# 0. CONFIGURAZIONE PAGINA
# =========================================================
st.set_page_config(page_title="Technical Generator v7.7", layout="wide")

st.markdown("""
    <style>
        div[data-testid="stWidgetLabel"] { margin-bottom: 5px !important; }
        .stRadio div[role="radiogroup"] { gap: 5px !important; }
        .stRadio label p, .stPills label p { font-size: 1.0rem !important; font-weight: 450 !important; }
        h3 { font-size: 2.0rem !important; margin-top: 25px !important; margin-bottom: 20px !important; }
        [data-testid="column"] { padding: 15px !important; }
        .stRadio > div { flex-wrap: wrap; display: flex; gap: 10px; }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 1. DATI E CONFIGURAZIONI
# =========================================================
MATERIALI_CONFIG = {
    "METAL COMP": {"METAL": "SHEET METAL", "ZINCATO": "GALVANIZED", "INOX": "STAINLESS STEEL", "ALLUMINIO": "ALUMINIUM"},
    "WOOD COMP": {"LAMINATO": "LAMINATED", "NOBILITATO": "MELAMINE", "TRUCIOLARE": "OSB"},
    "PLASTIC COMP": {"POLICARBONATO": "POLYCARBONATE", "PVC": "PVC", "GOMMA": "RUBBER"},
    "GLASS COMP": {"VETRO TEMPRATO": "TEMPERED GLASS", "VETRO SATINATO": "SATIN GLASS"},
    "FASTENER": {"ZINCATO": "GALVANIZED", "BRUNITO": "BURNISHED", "NERO": "BLACK"},
    "ASSEMBLY": {"MONTATO": "ASSEMBLED", "NON MONTATO": "NOT-ASSEMBLED"}
}

DATABASE = {
    "METAL COMP": {
        "macro_en": "METAL COMPONENT",
        "Particolari": {
            "Piede di base": ["BASE FOOT", {"H90": "H90", "H100": "H100", "H150": "H150", "Con piedino regolabile": "WITH ADJUSTABLE FOOT", "Estensione": "- EXTENSION", "Innesto montante": "UPRIGHT GRAFT"}, "FOOT"],
            "Zoccolatura": ["PLINTH", {"H90": "FOR H90 BASE FOOT", "H100": "FOR BASE FOOT H100", "H150": "FOR BASE FOOT H150", "Liscia": "PLAIN", "Angolo aperto": "EXTERNAL CORNER", "Angolo chiuso": "INNER CORNER", "Inclinata": "INCLINATED", "Forata": "PERFORATED", "Stondata": "ROUNDED", "Completa di paracolpo ABS": "WITH ABS BUFFER"}, "PLINTH"],
            "Pannello rivestimento": ["BACK PANEL", {"Scantonato": "NOTCHED", "Forato": "PERFORATED", "Multibarra": "MULTIBAR", "Multilame": "MULTISTRIP", "In rete": "MESH", "Forato rombo": "RUMBLE PERFORATED", "Nervato": "RIBBED", "Attacco montante": "HOOK ONTO UPRIGHT"}, "PANEL"],
            "Copripiede": ["FOOT COVER", {"H90": "FOR H90 FOOT", "H100": "FOR H100 FOOT", "H150": "FOR H150 FOOT"}, "COVER"],
            "Chiusura": ["COVER", {"Superiore": "TOP", "Tra ripiani di base": "INTER-BASE SHELF", "Con scasso": "WITH RECESS"}, "COVER"],
            "Fiancata laterale": ["SIDE PANEL", {"Portante": "LOAD-BEARING", "Non portante": "NON LOAD-BEARING", "Stondata": "ROUNDED", "Trapezoidale": "SLOPING", "Sagomata": "SHAPED"}, "SIDE-PANEL"],
            "Mensola": ["BRACKET", {"SX": "LEFT", "DX": "RIGHT", "Rinforzata": "REINFORCED", "Nervata": "RIBBED", "Per ripiano in vetro": "FOR GLASS SHELF", "Per ripiano in legno": "FOR WOODEN SHELF", "A pinza": "GRIPPED", "Minirack": "MINIRACK", "1 Posizione": "ONE POSIION", "2 Posizioni": "TWO POSITION"}, "BRACKET"],
            "Ripiano": ["SHELF", {"Liscio": "PLAIN", "Forato": "PERFORATED", "Stondato": "ROUNDED", "In filo": "WIRE", "Semicircolare": "SEMICIRCULAR", "Con rinforzo": "REINFORCED", "Con inserti filettati": "WITH RIVET", "Con portaprezzo": "WITH TICKET-HOLDER", "Scantonato": "NOTCHED"}, "SHELF"],
            "Cesto in filo": ["WIRE BASKET", {"Per attacco montante": "FOR UPRIGHT", "Per attacco fiancata": "FOR SIDE-PANEL", "Impilabile": "STACKABLE"}, "BASKET"],
            "Cielino": ["CANOPY", {"Dritto": "STRAIGHT", "Inclinato": "SLOPING", "Con finestra": "WITH WINDOW", "Stondato": "CURVED", "Centrale": "CENTRAL", "Frontale in lamiera": "SHEET METAL FASCIA", "Con illuminazione": "WITH LIGHTING"}, "CANOPY"],
            "Corrente": ["BEAM", {"Con mensole saldate": "WITH WELDING BRACKET", "Con spinotto di sicurrezza": "WITH SAFETY PIN"}, "BEAM"],
            "Diagonale": ["DIAGONAL", {"Forata": "PERFORATED", "Per crociera verticale": "FOR VERTICAL CROSS-WALL"}, "DIAGONAL"],
            "Distanziali": ["SPACER", {"Per controventatura": "FOR CROSS-WALL"}, "SPACER"],
            "Ganci": ["HOOK", {"Singolo": "SINGLE", "Predisposto per portaprezzo": "ACCEPTS TICKET-HOLDER", "Doppio": "DOUBLE", "Rovescio": "REVERSE", "Attacco barra": "HOOK FOR BAR", "Attacco multilame": "HOOK FOR MULTISTRIP", "Attacco pannello forato": "HOOK FOR SLOTTED PANEL"}, "HOOK"],
            "Profilo": ["PROFILE", {"Profilo a L": "L-SHAPED", "Profilo a U": "U-SHAPED"}, "PROFILE"],
            "Rinforzo": ["STIFFENER", {"Asolato": "SLOTTED", "Per ripiano di base": "FOR BASE SHELF", "Per fiancata": "FOR SIDE PANEL"}, "STIFFENER"],
            "Staffa": ["PLATE", {"Con viteria": "WITH SCREWS", "Di collegamento": "CONNECTING"}, "PLATE"],
            "Ante": ["SHEET METAL DOOR", {"Scorrevoli": "SLIDING", "Con foro serratura": "WITH LOCK HOLE"}, "DOOR"],
            "Piastra di fissaggio": ["FIXING PLATE", {"Con viti": "COMPLETE WITH SCREW"}, "PLATE"],
            "Cassetto estraibile": ["PULL-OUT DRAWER", {"Su ruote": "ON WHEELS", "Per piede H100": "FOR BASE FOOT H100", "Per piede H150": "FOR BASE FOOT H150", "Con serratura": "WITH LOCK", "Senza serratura": "WITHOUT LOCK"}, "DRAWER"],
            "Coprimontante": ["UPRIGHT-COVER", {"Per montante H70": "FOR H70 UPRIGHT", "Per montante H90": "FOR H90 UPRIGHT"}, "COVER"],
            "Pedana di base": ["BASE PLATFORM", {"Con rinforzi": "WITH REINFORCEMENT"}, "BASE"],
            "Divisorio": ["DIVIDER", {"In filo": "WIRE", "Trapezoidale": "SLOPING", "Per ripiano": "FOR SHELF"}, "DIVIDER"],
            "Frontalino": ["RISER", {"In filo": "WIRE", "Per ripiano": "FOR SHELF", "Cromato": "CHROMED", "Verniciato": "PAINTED"}, "RISER"],
            "Compensazione": ["FILLER PIECE", {"Per piede di base": "FOR BASE FOOT", "Per spalle L100/L120": "FOR L100/L120 FRAME"}, "SPACER"],
            "Controventatura": ["BRACING", {"Per montante": "FOR UPRIGHT", "Con mensole saldate": "WITH WELDING BRACKET", "Passo 25": "PITCH 25", "Passo 50": "PITCH 50"}, "BRACING"],
            "Traversini": ["CROSS BAR", {"Forato": "PERFORATED", "Con mensole saldate": "WITH WELDING BRACKET", "Con viteria": "WITH SCREWS"}, "CROSS BAR"],
            "Tubolare": ["TUBULAR", {"Piegato-saldato": "BENT AND WELDED", "Con mensole saldate": "WITH WELDING BRACKET", "Con viteria": "WITH SCREWS"}, "BAR"],
            "Filo": ["WIRE", {"Piegato": "BENT", "Piegato-saldato": "BENT AND WELDED", "Con viteria saldata": "WITH WELDING SCREWS"}, "WIRE"],
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
            "Controventatura": ["CROSS-BRACING", {"Sezione L120": "L120 SECTION", "Su due livelli": "ON TWO LEVELS", "Diagonali doppie": "DOUBLE DIAGONALS", "Diangonali triple": "TRIPLE DIAGONALS", "Diagonali quadruple": "QUADRUPLE DIAGONALS", "Con distanziale": "WITH SPACER"}, "CROSS-BRACING"],
            "Banco espositore di legno": ["WOODEN DESK", {"Con cassetto": "WITH DRAWER", "Con ruote": "WITH WHEELS"}, "DESK"],
            "Avancassa": ["IMPULSE UNIT", {"Con ripiani": "WITH SHELF", "Con ripiani inclinati": "WITH INCLINATED SHELF", "Con rete divisoria": "WITH DIVIDING NET", "Con ruote": "WITH WHEELS", "Con ganci": "WITH HOOKS", "Con batticarrello": "WITH TROLLEY BEATER"}, "DISPLAY"],
        }
    }
}

OPZIONI_COMPATIBILITA = ["", "F25", "F25 BESPOKE", "F25 READY", "F50", "F50 BESPOKE", "F50 READY", "UNIVERSAL", "FORTISSIMO"]

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

OPZIONI_SPESSORE_STD = ["", "0.5", "0.6", "0.75", "0.8", "1", "1.2", "1.5", "2", "2.5", "3", "3.5", "4", "4.5", "5"]
OPZIONI_SPESSORE_WOOD = ["", "18mm", "20mm", "25mm", "30mm", "35mm"]

TERMINI_ANTICIPATI = [
    "CENTRAL", "LEFT", "RIGHT", "REINFORCED", "INTERNAL", "EXTERNAL", "UPPER", "LOWER", 
    "MULTIBAR", "MULTISTRIP", "TOP", "INTER-BASE SHELF", "ROUNDED", "SLOPING", "SHAPED", "CONNECTING",
    "WIRE", "GRIPPED", "CHROMED", "PAINTED", "MESH", "SLIDING", "CURVED", "STRAIGHT", "MILLING", 
    "SEMICIRCULAR", "SINGLE", "DOUBLE", "END", "L-SHAPED", "U-SHAPED", "SERRATED LOCK", "UPRIGHT GRAFT"
]

# =========================================================
# 2. FUNZIONI
# =========================================================
def reset_all():
    keys_to_reset = ["dim_l", "dim_p", "dim_h", "dim_s", "dim_dia", "extra_text", "extra_tags", "comp_tags"]
    for k in keys_to_reset:
        if k in st.session_state:
            st.session_state[k] = [] if "tags" in k else ""

# =========================================================
# 3. INTERFACCIA
# =========================================================
st.title("⚙️ REG - Title Generator & Classification")

col_t, col_btn = st.columns([4, 1])
with col_btn:
    st.button("🔄 AZZERA TUTTO", on_click=reset_all, use_container_width=True)

st.markdown("---")

col_macro, col_workarea = st.columns([1, 3], gap="large")

with col_macro:
    st.subheader("📂 1. Categoria")
    macro_it = st.radio("Seleziona categoria:", options=list(DATABASE.keys()))
    
    if macro_it != "FASTENER":
        st.markdown("---")
        st.subheader("🔗 Compatibilità")
        pills_compatibilita = [opt for opt in OPZIONI_COMPATIBILITA if opt]
        comp_selezionate = st.pills("Modelli:", options=pills_compatibilita, selection_mode="multi", key="comp_tags")
    else:
        comp_selezionate = []

with col_workarea:
    st.subheader("🛠️ 2. Materiale e Particolare")
    materiali_disponibili = MATERIALI_CONFIG.get(macro_it, {})
    mat_en = ""
    if materiali_disponibili:
        mat_it = st.radio(f"Materiale:", options=list(materiali_disponibili.keys()), horizontal=True)
        mat_en = materiali_disponibili[mat_it]
    
    part_dict = DATABASE[macro_it]["Particolari"]
    scelta_part_it = st.radio("Seleziona dettaglio:", options=sorted(list(part_dict.keys())), horizontal=True)
    
    dati_part = part_dict[scelta_part_it]
    part_en, extra_dedicati_dict, tag_suggerimento = dati_part[0], dati_part[1], dati_part[2]

    st.markdown("---")
    st.subheader(f"✨ 3. Extra per {scelta_part_it}")
    
    extra_options = list(extra_dedicati_dict.keys())
    if extra_options:
        extra_selezionati = st.pills("Opzioni:", options=extra_options, selection_mode="multi", key="extra_tags")
    else:
        extra_selezionati = []
        st.info("Nessuna opzione extra disponibile per questo elemento.")

    extra_libero = st.text_input("Note libere (IT):", key="extra_text").strip()

    st.subheader("📏 4. Dimensioni e Normative")
    
    if macro_it == "FASTENER":
        c1, c2, c3 = st.columns(3)
        with c1: dim_l = st.text_input("Lunghezza (L)", key="dim_l")
        with c2: dim_dia = st.text_input("Diametro (D)", key="dim_dia")
        
        opzioni_filtrare = MAPPA_NORMATIVE_FASTENER.get(scelta_part_it, {"": ""})
        with c3: 
            norma_scelta_estesa = st.selectbox(f"Normativa {scelta_part_it}", options=list(opzioni_filtrare.keys()))
            normativa = opzioni_filtrare[norma_scelta_estesa]
            
        dim_p, dim_h, dim_s = "", "", "" 
    else:
        if macro_it == "ASSEMBLY":
            c1, c2, c3 = st.columns(3)
            dim_s = "" 
        else:
            c1, c2, c3, c4 = st.columns(4)
        
        with c1: dim_l = st.text_input("Lunghezza (L)", key="dim_l")
        with c2: dim_p = st.text_input("Profondità (P)", key="dim_p")
        with c3: dim_h = st.text_input("Altezza (H)", key="dim_h")
        
        if macro_it != "ASSEMBLY":
            lista_spessori = OPZIONI_SPESSORE_WOOD if macro_it == "WOOD COMP" else OPZIONI_SPESSORE_STD
            with c4: dim_s = st.selectbox("Spessore (S)", options=lista_spessori, key="dim_s")
        
        dim_dia, normativa = "", ""

# =========================================================
# 4. GENERAZIONE
# =========================================================

st.divider()

if 'stringa_editabile' not in st.session_state:
    st.session_state['stringa_editabile'] = ""

if st.button("🚀 GENERA STRINGA FINALE", use_container_width=True):
    dim_final_parts = []
    
    if macro_it == "FASTENER":
        d_val = dim_dia.strip().upper()
        l_val = dim_l.strip().upper()
        if d_val:
            prefix_d = "" if d_val.startswith('M') else "D"
            dim_final_parts.append(f"{prefix_d}{d_val}")
        if l_val:
            dim_final_parts.append(f"L{l_val}")
        dim_final = "X".join(dim_final_parts)
        if normativa: dim_final += f" {normativa}"
    else:
        if dim_l.strip(): dim_final_parts.append(f"L{dim_l.strip().upper()}")
        if dim_p.strip(): dim_final_parts.append(f"P{dim_p.strip().upper()}")
        if dim_h.strip(): dim_final_parts.append(f"H{dim_h.strip().upper()}")
        lph_str = "X".join(dim_final_parts)
        
        s_val = dim_s.strip()
        if lph_str and s_val: dim_final = f"{lph_str} S{s_val}"
        elif lph_str: dim_final = lph_str
        elif s_val: dim_final = f"S{s_val}"
        else: dim_final = ""

    extra_totali = [extra_dedicati_dict[ex] for ex in extra_selezionati]
    if extra_libero:
        try:
            extra_tradotto = GoogleTranslator(source='it', target='en').translate(extra_libero).upper()
            extra_totali.append(extra_tradotto)
        except:
            extra_totali.append(extra_libero.upper())

    prefissi = [ex for ex in extra_totali if ex in TERMINI_ANTICIPATI]
    suffissi = [ex for ex in extra_totali if ex not in TERMINI_ANTICIPATI]
    
    prefix_str = " ".join(prefissi) if prefissi else ""
    extra_str = ", ".join(suffissi) if suffissi else ""
    
    comp_list = [c for c in (comp_selezionate or []) if c.strip()]
    comp_str = ", ".join(comp_list) if comp_list else ""

    descrizione_centrale = f"{mat_en} {prefix_str} {part_en} {dim_final}".strip().replace("  ", " ")
    final_segments = [descrizione_centrale]
    if extra_str: final_segments.append(extra_str)
    if comp_str: final_segments.append(comp_str)
    
    temp_str = " - ".join(final_segments).upper().replace("  ", " ")
    temp_str = temp_str.replace("WITH WITH", "WITH")
    
    if temp_str.count("WITH") > 1:
        first_with_end = temp_str.find("WITH") + 4
        parte_iniziale = temp_str[:first_with_end]
        parte_restante = temp_str[first_with_end:].replace("WITH", "AND")
        temp_str = parte_iniziale + parte_restante
    
    st.session_state['stringa_editabile'] = temp_str.replace("  ", " ")

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
    all_tags = [tag_suggerimento.upper()] + [c.upper() for c in comp_list_tags]
    if normativa:
        all_tags.append(normativa.upper())
    st.info(f"**TAGS:** {' | '.join(all_tags)}")

# =========================================================
# 5. SISTEMA FEEDBACK PER BETA TEST (Aggiungi in fondo)
# =========================================================

st.sidebar.markdown("---")
st.sidebar.header("📢 Beta Test Feedback")

# Area per i colleghi
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
            # Formattazione riga: Data/Ora (opzionale), Tipo, Messaggio
            import datetime
            ora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            # Pulizia del testo per evitare problemi col CSV (rimozione punti e virgola)
            nota_pulita = nota_feedback.replace(";", ",").replace("\n", " ")
            nuova_riga = f"{ora};{tipo_segnalazione};{nota_pulita}\n"
            
            # Scrittura su file (Append mode)
            try:
                with open("feedback.csv", "a", encoding="utf-8") as f:
                    f.write(nuova_riga)
                st.success("✅ Ricevuto! Grazie per l'aiuto.")
            except Exception as e:
                st.error(f"Errore nel salvataggio: {e}")
        else:
            st.warning("Inserisci un messaggio prima di inviare.")

# Area riservata a te per il recupero dati
st.sidebar.markdown("---")
with st.sidebar.expander("🛠️ Area Admin (Download)"):
    pw = st.text_input("Password accesso dati", type="password")
    # Puoi scegliere una password semplice, es: "admin2024"
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
