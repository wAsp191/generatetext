import streamlit as st
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Technical Description Generator v1.1", layout="wide")

# --- LISTA COMPATIBILITÀ FISSA ---
opzioni_compatibilita = [
    "F25", 
    "F25 BESPOKE", 
    "F50", 
    "F50 BESPOKE", 
    "UNIVERSAL", 
    "FORTISSIMO"
]

# --- DATABASE SOTTOASSIEMI ---
database = {
    "1. Sheet Metal": {
        "macro_en": "SHEET METAL",
        "Particolari": {
            "Taglio Laser": "LASER CUT",
            "Piegatura CNC": "CNC BENDING",
            "Saldatura TIG": "TIG WELDING",
            "Punzonatura": "PUNCHING",
            "Alesatura": "BORING",
            "Calandratura": "ROLLING",
            "Satinatura": "SATIN FINISH"
        }
    },
    "2. Plastic Comp": {
        "macro_en": "PLASTIC COMPONENT",
        "Particolari": {
            "Stampaggio a iniezione": "INJECTION MOLDED",
            "Termoformato": "THERMOFORMED",
            "Resistente UV": "UV RESISTANT",
            "Polimero rinforzato": "REINFORCED POLYMER",
            "Estruso": "EXTRUDED",
            "Finitura opaca": "MATTE FINISH"
        }
    },
    "3. Glass Comp": {
        "macro_en": "GLASS COMPONENT",
        "Particolari": {
            "Vetro temprato": "TEMPERED GLASS",
            "Vetro stratificato": "LAMINATED GLASS",
            "Finitura acidata": "ACID-ETCHED FINISH",
            "Bordo filo lucido": "POLISHED EDGE",
            "Vetro Satinato": "SATIN GLASS",
            "Colorazione in pasta": "COLORED GLASS"
        }
    },
    "4. Wood Comp": {
        "macro_en": "WOOD COMPONENT",
        "Particolari": {
            "Legno di Rovere": "OAK WOOD",
            "Multistrato": "PLYWOOD",
            "Finitura naturale": "NATURAL FINISH",
            "Verniciatura opaca": "MATTE PAINTING",
            "Abete": "FIR WOOD",
            "Noce Canaletto": "WALNUT WOOD"
        }
    },
    "5. Electric Comp": {
        "macro_en": "ELECTRIC COMPONENT",
        "Particolari": {
            "Cablaggio standard": "STANDARD WIRING",
            "Grado IP65": "IP65 RATING",
            "Protezione termica": "THERMAL PROTECTION",
            "Modulo LED": "LED MODULE",
            "Alimentatore": "POWER SUPPLY",
            "Interruttore": "SWITCH"
        }
    },
    "6. Fastner": {
        "macro_en": "FASTENER",
        "Particolari": {
            "Acciaio zincato": "ZINC PLATED STEEL",
            "Acciaio Inox A2": "STAINLESS STEEL A2",
            "Classe 8.8": "8.8 GRADE",
            "Filettatura metrica": "METRIC THREAD",
            "Bullone": "BOLT",
            "Dado": "NUT"
        }
    },
    "7. Other": {
        "macro_en": "OTHER",
        "Particolari": {
            "Materiale misto": "MIXED MATERIAL",
            "Specifica custom": "CUSTOM SPECIFICATION",
            "Accessorio": "ACCESSORY"
        }
    }
}

st.title("⚙️ Universal Technical Description Generator")
st.markdown("---")

# --- LAYOUT PRINCIPALE ---
col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.subheader("📂 1. Macro Categoria")
    macro_it = st.radio(
        "Scegli una categoria:",
        options=list(database.keys()),
        index=0
    )
    macro_en = database[macro_it]["macro_en"]

with col_right:
    st.subheader("🔍 2. Particolare")
    
    # --- LOGICA ALFABETICA CON CAPOLETTERA ---
    opzioni_part_dict = database[macro_it]["Particolari"]
    opzioni_it_ordinate = sorted(list(opzioni_part_dict.keys()))
    
    # Mostriamo l'elenco con i capi-lettera visivi
    current_letter = ""
    part_scelto_it = None
    
    # Poiché Streamlit radio non supporta intestazioni tra i bottoni, 
    # simuliamo l'ordine alfabetico visivo con un radio button pulito 
    # e mostriamo la struttura alfabetica sopra
    
    # Creiamo una lista per il radio button
    part_it = st.radio(
        "Seleziona il dettaglio tecnico:",
        options=opzioni_it_ordinate,
        help="L'elenco è ordinato alfabeticamente."
    )
    
    # Visualizzazione dei separatori alfabetici (solo per estetica sopra il radio)
    st.markdown("---")
    st.subheader("📋 3. Dati Variabili e Compatibilità")
    
    comp_scelta = st.selectbox("5. Compatibilità:", opzioni_compatibilita)
    dim_input = st.text_input("3. DIMENSIONI (es. 500X200 MM):").strip().upper()
    extra_it = st.text_input("4. EXTRA (Traduzione Automatica):", placeholder="Scrivi in italiano...").strip()

# --- TRADUZIONE E GENERAZIONE ---
part_en = database[macro_it]["Particolari"][part_it]

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
    
    # Assemblaggio finale
    final_string = f"{macro_en} - {part_en} - {dim_final} - {extra_final} - {comp_scelta}"
    final_string = final_string.upper()

    st.success("Stringa tecnica generata correttamente!")
    st.code(final_string, language=None)
    st.text_area("Copia rapida:", value=final_string, height=70)

# CSS Personalizzato per i capi-lettera (opzionale, per migliorare l'estetica)
st.markdown("""
<style>
    .stRadio [role="radiogroup"] {
        padding-top: 10px;
    }
</style>
""", unsafe_allow_html=True)
