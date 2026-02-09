import streamlit as st
from deep_translator import GoogleTranslator

# Configurazione Pagina
st.set_page_config(page_title="Technical Description Generator", layout="wide")

# =========================================================
# DATABASE PRODOTTI (Modifica qui per aggiungere/togliere)
# Schema -> "Nome in Italiano": "TECHNICAL ENGLISH NAME"
# =========================================================
DATABASE = {
    "1. Sheet Metal": {
        "macro_en": "SHEET METAL",
        "Particolari": {
            "Alesatura": "BORING",
            "Calandratura": "ROLLING",
            "Piegatura CNC": "CNC BENDING",
            "Punzonatura": "PUNCHING",
            "Satinatura": "SATIN FINISH",
            "Saldatura TIG": "TIG WELDING",
            "Taglio Laser": "LASER CUT",
            "Zincatura a caldo": "HOT-DIP GALVANIZED"
        }
    },
    "2. Plastic Comp": {
        "macro_en": "PLASTIC COMPONENT",
        "Particolari": {
            "Estruso": "EXTRUDED",
            "Finitura opaca": "MATTE FINISH",
            "Polimero rinforzato": "REINFORCED POLYMER",
            "Resistente UV": "UV RESISTANT",
            "Stampaggio a iniezione": "INJECTION MOLDED",
            "Termoformato": "THERMOFORMED"
        }
    },
    "3. Glass Comp": {
        "macro_en": "GLASS COMPONENT",
        "Particolari": {
            "Bordo filo lucido": "POLISHED EDGE",
            "Colorazione in pasta": "COLORED GLASS",
            "Finitura acidata": "ACID-ETCHED FINISH",
            "Vetro Satinato": "SATIN GLASS",
            "Vetro stratificato": "LAMINATED GLASS",
            "Vetro temprato": "TEMPERED GLASS"
        }
    },
    "4. Wood Comp": {
        "macro_en": "WOOD COMPONENT",
        "Particolari": {
            "Abete": "FIR WOOD",
            "Finitura naturale": "NATURAL FINISH",
            "Legno di Rovere": "OAK WOOD",
            "Multistrato": "PLYWOOD",
            "Noce Canaletto": "WALNUT WOOD",
            "Verniciatura opaca": "MATTE PAINTING"
        }
    },
    "5. Electric Comp": {
        "macro_en": "ELECTRIC COMPONENT",
        "Particolari": {
            "Alimentatore": "POWER SUPPLY",
            "Cablaggio standard": "STANDARD WIRING",
            "Grado IP65": "IP65 RATING",
            "Interruttore": "SWITCH",
            "Modulo LED": "LED MODULE",
            "Protezione termica": "THERMAL PROTECTION"
        }
    },
    "6. Fastener": {
        "macro_en": "FASTENER",
        "Particolari": {
            "Acciaio Inox A2": "STAINLESS STEEL A2",
            "Acciaio zincato": "ZINC PLATED STEEL",
            "Bullone": "BOLT",
            "Classe 8.8": "8.8 GRADE",
            "Dado": "NUT",
            "Filettatura metrica": "METRIC THREAD"
        }
    },
    "7. Other": {
        "macro_en": "OTHER",
        "Particolari": {
            "Accessorio": "ACCESSORY",
            "Materiale misto": "MIXED MATERIAL",
            "Specifica custom": "CUSTOM SPECIFICATION"
        }
    }
}

OPZIONI_COMPATIBILITA = ["F25", "F25 BESPOKE", "F50", "F50 BESPOKE", "UNIVERSAL", "FORTISSIMO"]

# =========================================================
# LOGICA INTERFACCIA
# =========================================================

st.title("🛠️ Universal Description Generator")
st.markdown("---")

# 1. SELEZIONE MACRO (Sempre visibile a sinistra)
col_macro, col_workarea = st.columns([1, 3], gap="large")

with col_macro:
    st.subheader("📂 1. Macro Categoria")
    macro_it = st.radio("Seleziona una categoria:", options=list(DATABASE.keys()))
    macro_en = DATABASE[macro_it]["macro_en"]

with col_workarea:
    st.subheader("🔍 2. Particolare (Ordine Alfabetico)")
    
    # Recupero i particolari e li ordino alfabeticamente
    part_dict = DATABASE[macro_it]["Particolari"]
    nomi_it_ordinati = sorted(list(part_dict.keys()))
    
    # CREAZIONE GRIGLIA: Visualizziamo i particolari in 3 colonne per risparmiare spazio
    scelta_part_it = st.radio(
        "Scegli il dettaglio tecnico:",
        options=nomi_it_ordinati,
        horizontal=True, # Questa opzione li mette uno di fianco all'altro!
    )
    part_en = part_dict[scelta_part_it]

    st.markdown("---")
    
    # 3. COMPATIBILITÀ, DIMENSIONI, EXTRA
    st.subheader("📝 Dati Finali")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        comp_scelta = st.selectbox("5. Compatibilità:", OPZIONI_COMPATIBILITA)
    with c2:
        dim_input = st.text_input("3. Dimensioni:", placeholder="es. 500X200 MM").strip().upper()
    with c3:
        extra_it = st.text_input("4. Extra (IT):", placeholder="es. verniciato nero").strip()

# =========================================================
# GENERAZIONE RISULTATO
# =========================================================
st.divider()

if st.button("🚀 GENERA STRINGA FINALE", use_container_width=True):
    # Traduzione automatica campo Extra
    if extra_it:
        try:
            extra_en = GoogleTranslator(source='it', target='en').translate(extra_it)
            extra_final = extra_en.upper()
        except:
            extra_final = extra_it.upper()
    else:
        extra_final = "NONE"

    dim_final = dim_input if dim_input else "N/A"
    
    # COSTRUZIONE STRINGA: MACRO - PARTICOLARE - DIMENSIONI - EXTRA - COMPATIBILITÀ
    res = f"{macro_en} - {part_en} - {dim_final} - {extra_final} - {comp_scelta}"
    res = res.upper()

    st.success("Stringa generata con successo!")
    st.code(res, language=None)
    st.text_area("Copia rapida:", value=res, height=70)

# Stile CSS per rendere i radio button orizzontali più compatti
st.markdown("""
<style>
    div[data-testid="stMarkdownContainer"] hr { margin: 1rem 0; }
    .stRadio > div { flex-wrap: wrap; display: flex; gap: 10px; }
</style>
""", unsafe_allow_html=True)
