import streamlit as st
from deep_translator import GoogleTranslator

# Configurazione Pagina
st.set_page_config(page_title="Technical Generator v7.0", layout="wide")

# =========================================================
# 1. CONFIGURAZIONE MATERIALI PER MACRO
# =========================================================
# Modifica qui per aggiungere o cambiare materiali in futuro
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
    "FASTENER": {}, # Lasciare vuoto se non serve materiale
    "ASSEMBLY": {}
}

# =========================================================
# 2. DATABASE PARTICOLARI (Dal tuo Excel)
# =========================================================
DATABASE = {
    "METAL COMP": {
        "macro_en": "METAL COMPONENT",
        "Particolari": {
            "Montante": ["UPRIGHT", {"70x30": "70X30", "90x30": "90X30", "Minirack": "MINIRACK"}, "UPRIGHT"],
            "Piede di base": ["BASE FOOT", {"H90": "H90", "H100": "H100"}, "FOOT"],
            "Zoccolatura": ["PLINTH", {"Liscia": "PLAIN", "Forata": "PERFORATED"}, "PLINTH"],
            "Pannello rivestimento": ["BACK PANEL", {"Forato euro": "EURO PERFORATED"}, "PANEL"],
            "Copripiede": ["FOOT COVER", {}, "COVER"],
            "Chiusura": ["TOP COVER", {"Con scasso": "WITH RECESS"}, "COVER"],
            "Fiancata laterale": ["SIDE PANEL", {"Portante": "LOAD-BEARING"}, "PANEL"],
            "Mensola": ["BRACKET", {"Rinforzata": "REINFORCED", "Sinistra": "LEFT", "Destra": "RIGHT"}, "BRACKET"],
            "Coprifessura": ["JOINT COVER", {"Standard": "STANDARD"}, "ACCESSORY"],
            "Ripiano": ["SHELF", {"H30": "H30", "H20": "H20"}, "SHELF"]
        }
    },
    "WOOD COMP": {
        "macro_en": "WOOD COMPONENT",
        "Particolari": {
            "Ripiano legno": ["WOODEN SHELF", {}, "SHELF"],
            "Schienale": ["WOODEN BACK", {}, "PANEL"]
        }
    },
    "PLASTIC COMP": {
        "macro_en": "PLASTIC COMPONENT",
        "Particolari": {
            "Tappo": ["PLASTIC CAP", {}, "ACCESSORY"],
            "Guarnizione": ["GASKET", {}, "ACCESSORY"]
        }
    },
    "GLASS COMP": {
        "macro_en": "GLASS COMPONENT",
        "Particolari": {
            "Vetro": ["GLASS PANEL", {}, "GLASS"]
        }
    },
    "FASTENER": {
        "macro_en": "FASTENER",
        "Particolari": {
            "Vite": ["SCREW", {}, "FASTENER"],
            "Bullone": ["BOLT", {}, "FASTENER"]
        }
    },
    "ASSEMBLY": {
        "macro_en": "ASSEMBLY",
        "Particolari": {
            "Assieme Mobile": ["CABINET ASSEMBLY", {"Pre-montato": "PRE-ASSEMBLED"}, "ASSEMBLY"]
        }
    }
}

OPZIONI_COMPATIBILITA = ["F25", "F25 BESPOKE", "F50", "F50 BESPOKE", "UNIVERSAL", "FORTISSIMO"]
EXTRA_COMUNI = {"Certificato CE": "CE CERTIFIED", "Ignifugo": "FIRE RETARDANT"}
OPZIONI_SPESSORE = ["", "5/10", "6/10", "8/10", "10/10", "12/10", "15/10", "20/10", "25/10", "30/10", "35/10", "40/10", "45/10", "50/10"]

# =========================================================
# FUNZIONI DI SUPPORTO
# =========================================================
def reset_all():
    for key in ["dim_l", "dim_p", "dim_h", "dim_s", "extra_text", "extra_tags", "comp_tags"]:
        st.session_state[key] = "" if "dim" in key or "text" in key else []

# =========================================================
# INTERFACCIA UTENTE
# =========================================================
st.title("⚙️ Technical Generator v7.0")

col_t, col_btn = st.columns([4, 1])
with col_btn:
    st.button("🔄 AZZERA TUTTO", on_click=reset_all, use_container_width=True)

st.markdown("---")
col_macro, col_workarea = st.columns([1, 3], gap="large")

with col_macro:
    st.subheader("📂 1. Macro Categoria")
    macro_selezionata = st.radio("Seleziona categoria:", options=list(DATABASE.keys()))
    macro_en = DATABASE[macro_selezionata]["macro_en"]

with col_workarea:
    # SEZIONE MATERIALE (Dinamica in base alla Macro)
    st.subheader("🛠️ 2. Materiale e Particolare")
    materiali_disponibili = MATERIALI_CONFIG.get(macro_selezionata, {})
    
    mat_en = ""
    if materiali_disponibili:
        mat_it = st.radio(f"Materiale per {macro_selezionata}:", options=list(materiali_disponibili.keys()), horizontal=True)
        mat_en = materiali_disponibili[mat_it]
    
    st.write("") # Spaziatore
    
    # SEZIONE PARTICOLARE
    part_dict = DATABASE[macro_selezionata]["Particolari"]
    nomi_it = sorted(list(part_dict.keys()))
    scelta_part_it = st.radio("Seleziona dettaglio:", options=nomi_it, horizontal=True)
    
    part_en = part_dict[scelta_part_it][0]
    extra_dedicati = part_dict[scelta_part_it][1]
    tag_base = part_dict[scelta_part_it][2]

    st.markdown("---")
    
    # EXTRA (PUNTO 3)
    st.subheader(f"✨ 3. Extra per {scelta_part_it}")
    col_ex1, col_ex2 = st.columns([2, 1])
    with col_ex1:
        opzioni_extra = {**EXTRA_COMUNI, **extra_dedicati}
        extra_selezionati = st.multiselect("Opzioni:", options=list(opzioni_extra.keys()), key="extra_tags")
    with col_ex2:
        extra_libero = st.text_input("Note libere (Traduzione Automatica):", key="extra_text").strip()

    # DIMENSIONI (PUNTO 4)
    st.subheader("📏 4. Dimensioni (mm)")
    c1, c2, c3, c4 = st.columns(4)
    with c1: dim_l = st.text_input("Lunghezza", key="dim_l")
    with c2: dim_p = st.text_input("Profondità", key="dim_p")
    with c3: dim_h = st.text_input("Altezza", key="dim_h")
    with c4: dim_s = st.selectbox("Spessore", options=OPZIONI_SPESSORE, key="dim_s")

    # COMPATIBILITÀ (PUNTO 5)
    st.subheader("🔗 5. Compatibilità")
    comp_selezionate = st.multiselect("Modelli:", options=OPZIONI_COMPATIBILITA, key="comp_tags")

# =========================================================
# LOGICA DI GENERAZIONE
# =========================================================
st.divider()

if st.button("🚀 GENERA STRINGA FINALE", use_container_width=True):
    # Unione Dimensioni con X
    dims = [d.strip().upper() for d in [dim_l, dim_p, dim_h, dim_s] if d.strip()]
    dim_final = "X".join(dims) if dims else ""
    
    # Traduzione Extra
    lista_extra_en = [opzioni_extra[ex] for ex in extra_selezionati]
    if extra_libero:
        try:
            extra_tradotto = GoogleTranslator(source='it', target='en').translate(extra_libero).upper()
            lista_extra_en.append(extra_tradotto)
        except:
            lista_extra_en.append(extra_libero.upper())
    
    extra_final_str = ", ".join(lista_extra_en) if lista_extra_en else "NONE"
    comp_final_str = ", ".join(comp_selezionate) if comp_selezionate else "UNIVERSAL"
    
    # COSTRUZIONE STRINGA: MACRO - MATERIALE NOME DIMENSIONI, EXTRA - COMPATIBILITA
    # Mat_en viene messo prima di part_en se presente
    corpo_centrale = f"{mat_en} {part_en} {dim_final}".strip().replace("  ", " ")
    stringa_finale = f"{macro_selezionata} - {corpo_centrale}, {extra_final_str} - {comp_final_str}".upper()

    st.success("Stringa tecnica generata!")
    st.code(stringa_finale, language=None)

    # Box Suggerimenti Tag
    st.markdown("### 💡 Suggerimenti per la classificazione")
    tags = [tag_base.upper()] + [c.upper() for c in comp_selezionate]
    st.info(f"**TAGS:** {' | '.join(tags)}")

st.markdown("<style>.stRadio > div { flex-wrap: wrap; display: flex; gap: 10px; }</style>", unsafe_allow_html=True)
