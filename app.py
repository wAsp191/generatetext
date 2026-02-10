import streamlit as st
from deep_translator import GoogleTranslator

# Configurazione Pagina
st.set_page_config(page_title="Technical Generator v7.5", layout="wide")

# =========================================================
# 1. CONFIGURAZIONE MATERIALI
# =========================================================
MATERIALI_CONFIG = {
    "METAL COMP": {
        "FERRO": "IRON",
        "ZINCATO": "GALVANIZED",
        "INOX": "STAINLESS STEEL",
        "ALLUMINIO": "ALUMINIUM"
    },
    "WOOD COMP": {
        "LAMINATO": "LAMINATED",
        "NOBILITATO": "MELAMINE",
        "TRUCIOLARE": "OSB"
    },
    "PLASTIC COMP": {
        "POLICARBONATO": "POLYCARBONATE",
        "PVC": "PVC",
        "GOMMA": "RUBBER"
    },
    "GLASS COMP": {
        "VETRO TEMPRATO": "TEMPERED GLASS"
    },
    "FASTENER": {}, 
    "ASSEMBLY": {}
}

# =========================================================
# 2. DATABASE INTEGRALE
# =========================================================
DATABASE = {
    "METAL COMP": {
        "macro_en": "METAL COMPONENT",
        "Particolari": {
            "Montante": ["UPRIGHT", {
                "70x30": "70X30", "90x30": "90X30", "Monoasolato": "WITH SLOTS ON ONE SIDE", 
                "Biasolato": "WITH SLOTS ON TWO SIDE", "Con rinforzo": "WITH REINFORCEMENT", 
                "Estensione": "-EXTENSION", "Minirack": "MINIRACK",
                "L120": "L120", "L100": "L100", "Z/S Basso carico": "Z/S", "Z/M Alto carico": "Z/M"
            }, "UPRIGHT"],
            "Piede di base": ["BASE FOOT", {
                "H90": "H90", "H100": "H100", "H150": "H150", 
                "Con piedino regolabile": "WITH ADJUSTABLE FOOT", "Estensione": "-EXTENSION"
            }, "FOOT"],
            "Zoccolatura": ["PLINTH", {
                "H90": "FOR H90 BASE FOOT", "H100": "FOR BASE FOOT H100", "H150": "FOR BASE FOOT H150", 
                "Liscia": "PLAIN", "Angolo aperto": "EXTERNAL CORNER", "Angolo chiuso": "INNER CORNER", 
                "Inclinata": "INCLINATED", "Forata": "PERFORATED", "Stondata": "ROUNDED", 
                "Completa di paracolpo ABS": "WITH ABS BUFFER"
            }, "PLINTH"],
            "Pannello rivestimento": ["BACK PANEL", {
                "Scantonato": "NOTCHED", "Forato euro": "EURO PERFORATED", "Multibarra": "MULTIBAR", "Multilame": "MULTISTRIP",
                "Forato rombo": "RUMBLE PERFORATED", "Nervato": "RIBBED"
            }, "PANEL"],
            "Copripiede": ["FOOT COVER", {
                "H90": "FOR H90 FOOT", "H100": "FOR H100 FOOT", "H150": "FOR H150 FOOT"
            }, "COVER"],
            "Chiusura": ["COVER", {"Superiore": "TOP", "Tra ripiani di base": "INTER-BASE SHELF", "Con scasso": "WITH RECESS"}, "COVER"],
            "Fiancata laterale": ["SIDE PANEL", {
                "Portante": "LOAD-BEARING", "Non portante": "NON LOAD-BEARING"
            }, "SIDE-PANEL"],
            "Mensola": ["BRACKET", {
                "SX": "LEFT", "DX": "RIGHT", "Rinforzata": "REINFORCED"
            }, "BRACKET"],
            "Ripiano": ["SHELF", {
                "Liscio": "PLAIN", "Forato": "PERFORATED", 
                "Con rinforzo": "REINFORCED", "Con inserti filettati": "WITH RIVET"
            }, "SHELF"],
            "Cesto in filo": ["WIRE BASKET", {}, "BASKET"],
            "Cielino": ["CANOPY", {}, "CANOPY"],
            "Corrente": ["BEAM", {}, "BEAM"],
            "Diagonale": ["DIAGONAL", {}, "DIAGONAL"],
            "Distanziali": ["SPACER", {}, "SPACER"],
            "Divisori": ["DIVIDER", {}, "DIVIDER"],
            "Ganci": ["HOOK", {}, "HOOK"],
            "Profilo": ["PROFILE", {}, "PROFILE"],
            "Rinforzo": ["STIFFENER", {}, "STIFFENER"],
            "Staffa": ["PLATE", {}, "PLATE"],
            "Ante scorrevoli": ["SLIDING DOOR", {}, "DOOR"],
            "Piastra di fissaggio": ["FIXING PLATE", {"Con viti": "COMPLETE WITH SCREW"}, "PLATE"],
            "Cassetto estraibile": ["PULL-OUT DRAWER", {
                "Su ruote": "ON WHEELS", "Per piede H100": "FOR BASE FOOT H100", 
                "Per piede H150": "FOR BASE FOOT H150", "Con serratura": "WITH LOCK", 
                "Senza serratura": "WITHOUT LOCK"}, "DRAWER"]
            "Coprimontante": ["UPRIGHT-COVER", {}, "COVER"],
        }
    },
    "WOOD COMP": {
        "macro_en": "WOOD COMPONENT",
        "Particolari": {
            "Ripiano Legno": ["WOODEN SHELF", {}, "SHELF"],
            "Schienale Legno": ["WOODEN BACK", {}, "PANEL"],
            "Cielino": ["CANOPY", {}, "CANOPY"],
            "Zoccolatura": ["WOODEN PLINTH", {"H100": "H100", "H150": "H150"}, "PLINTH"]
            "Fiancata": ["WOODEN SIDE PANEL", {}, "SIDE PANEL"]
            "Copripiede": ["WOODEN FOOT-COVER", {"H100": "FOR H100 BASE FOOT", "H150": "FOR H150 BASE FOOT"}, "COVER"]
            "Coprimontante": ["WOODEN UPRIGHT-COVER", {}, "COVER"],
        }
    },
    "PLASTIC COMP": {
        "macro_en": "PLASTIC COMPONENT",
        "Particolari": {
            "Tappo": ["PLASTIC CAP", {}, "CAP"],
            "Guarnizione": ["GASKET", {}, "ACCESSORY"]
        }
    },
    "GLASS COMP": {
        "macro_en": "GLASS COMPONENT",
        "Particolari": {
            "Ripiano": ["GLASS SHELF", {}, "SHELF"]
        }
    },
    "FASTENER": {
        "macro_en": "FASTENER",
        "Particolari": {
            "Vite": ["SCREW", {}, "FASTENER"],
            "Bullone": ["BOLT", {}, "FASTENER"],
            "Rondella": ["WASHER", {}, "FASTENER"],
            "Dado": ["NUT", {}, "FASTENER"],
            "Inserti filettati": ["RIVET", {}, "FASTENER"],
        }
    },
    "ASSEMBLY": {
        "macro_en": "ASSEMBLY",
        "Particolari": {
            "Assieme Mobile": ["CABINET ASSEMBLY", {"Pre-montato": "PRE-ASSEMBLED"}, "ASSEMBLY"],
            "Assieme generale": ["GENERAL ASSEMBLY", {}, "ASSEMBLY"]
        }
    }
}

OPZIONI_COMPATIBILITA = ["", "F25", "F25 BESPOKE", "F50", "F50 BESPOKE", "UNIVERSAL", "FORTISSIMO"]
OPZIONI_SPESSORE = ["", "5/10", "6/10", "8/10", "10/10", "12/10", "15/10", "20/10", "25/10", "30/10", "35/10", "40/10", "45/10", "50/10"]
OPZIONI_NORMATIVA = ["", "DIN 912", "DIN 933"]

# ELENCO TERMINI DA ANTICIPARE (PREFISSI)
# Se una voce extra è in questa lista, verrà messa PRIMA del nome del particolare
TERMINI_ANTICIPATI = ["CENTRAL", "LEFT", "RIGHT", "REINFORCED", "INTERNAL", "EXTERNAL", "UPPER", "LOWER", "MULTIBAR", "MULTISTRIP", "TOP", "INTER-BASE SHELF"]

# =========================================================
# FUNZIONI
# =========================================================
def reset_all():
    for k in ["dim_l", "dim_p", "dim_h", "dim_s", "dim_dia", "extra_text", "extra_tags", "comp_tags"]:
        if k in st.session_state: st.session_state[k] = "" if "tags" not in k else []

# =========================================================
# INTERFACCIA
# =========================================================
st.title("⚙️ Technical Generator & Classification")

col_t, col_btn = st.columns([4, 1])
with col_btn:
    st.button("🔄 AZZERA TUTTO", on_click=reset_all, use_container_width=True)

st.markdown("---")
col_macro, col_workarea = st.columns([1, 3], gap="large")

with col_macro:
    st.subheader("📂 1. Macro Categoria")
    # La Macro viene selezionata qui per filtrare, ma non sarà stampata
    macro_it = st.radio("Seleziona categoria:", options=list(DATABASE.keys()))

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
    col_ex1, col_ex2 = st.columns([2, 1])
    with col_ex1:
        # Ora mostra SOLO gli extra specifici del database
        extra_selezionati = st.multiselect("Opzioni:", options=list(extra_dedicati_dict.keys()), key="extra_tags")
    with col_ex2:
        extra_libero = st.text_input("Note libere (IT):", key="extra_text").strip()

    st.subheader("📏 4. Dimensioni e Normative")
    if macro_it == "FASTENER":
        c1, c2, c3 = st.columns(3)
        with c1: dim_l = st.text_input("Lunghezza (L)", key="dim_l")
        with c2: dim_dia = st.text_input("Diametro (D)", key="dim_dia")
        with c3: normativa = st.selectbox("Normativa", options=OPZIONI_NORMATIVA)
        dim_p, dim_h, dim_s = "", "", "" 
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1: dim_l = st.text_input("Lunghezza (L)", key="dim_l")
        with c2: dim_p = st.text_input("Profondità (P)", key="dim_p")
        with c3: dim_h = st.text_input("Altezza (H)", key="dim_h")
        with c4: dim_s = st.selectbox("Spessore (S)", options=OPZIONI_SPESSORE, key="dim_s")
        dim_dia, normativa = "", ""

    st.subheader("🔗 5. Compatibilità")
    comp_selezionate = st.multiselect("Modelli:", options=OPZIONI_COMPATIBILITA, key="comp_tags")

# =========================================================
# GENERAZIONE STRINGA FINALE
# =========================================================
st.divider()

if st.button("🚀 GENERA STRINGA FINALE", use_container_width=True):
    # Logica Dimensioni con prefissi (L, P, H, D, S)
    dim_final_parts = []
    
    if macro_it == "FASTENER":
        d_val = dim_dia.strip().upper()
        l_val = dim_l.strip().upper()
        
        if d_val:
            # Se ha M (es. M8) non mette D, altrimenti mette D
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
        
        if lph_str and s_val:
            dim_final = f"{lph_str} S{s_val}"
        elif lph_str:
            dim_final = lph_str
        elif s_val:
            dim_final = f"S{s_val}"
        else:
            dim_final = ""

    # --- INIZIO MODIFICA PREFISSI/SUFFISSI ---
    
    # 1. Raccogliamo tutti gli extra tradotti in una lista
    extra_totali = [extra_dedicati_dict[ex] for ex in extra_selezionati]
    if extra_libero:
        try:
            extra_tradotto = GoogleTranslator(source='it', target='en').translate(extra_libero).upper()
            extra_totali.append(extra_tradotto)
        except:
            extra_totali.append(extra_libero.upper())

    # 2. Separiamo quelli che devono stare DAVANTI (Prefissi) da quelli che stanno DIETRO (Suffissi)
    prefissi = [ex for ex in extra_totali if ex in TERMINI_ANTICIPATI]
    suffissi = [ex for ex in extra_totali if ex not in TERMINI_ANTICIPATI]
    
    prefix_str = " ".join(prefissi) if prefissi else ""
    extra_str = ", ".join(suffissi) if suffissi else "" # Questi sono i suffissi (Extra veri e propri)

    # Compatibilità
    comp_list = [c for c in comp_selezionate if c.strip()]
    comp_str = ", ".join(comp_list) if comp_list else ""

    # Composizione finale: MAT_EN + PREFISSI + PART_EN + DIMENSIONI
    # Il replace serve a togliere doppi spazi se qualche campo è vuoto
    descrizione_centrale = f"{mat_en} {prefix_str} {part_en} {dim_final}".strip().replace("  ", " ").replace("  ", " ")
    
    final_segments = [descrizione_centrale]
    if extra_str: final_segments.append(extra_str)
    if comp_str: final_segments.append(comp_str)
        
    res = " - ".join(final_segments).upper()
    
    # --- FINE MODIFICA ---

    st.success("Stringa tecnica generata!")
    st.code(res, language=None)

    st.markdown("### 💡 Suggerimenti per la classificazione")
    all_tags = [tag_suggerimento.upper()] + [c.upper() for c in comp_list]
    st.info(f"**TAGS:** {' | '.join(all_tags)}")

st.markdown("<style>.stRadio > div { flex-wrap: wrap; display: flex; gap: 10px; }</style>", unsafe_allow_html=True)
