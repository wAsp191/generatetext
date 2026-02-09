import streamlit as st
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Technical Description Generator v1.0", layout="wide")

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
            "Punzonatura": "PUNCHING"
        }
    },
    "2. Plastic Comp": {
        "macro_en": "PLASTIC COMPONENT",
        "Particolari": {
            "Stampaggio a iniezione": "INJECTION MOLDED",
            "Termoformato": "THERMOFORMED",
            "Resistente UV": "UV RESISTANT",
            "Polimero rinforzato": "REINFORCED POLYMER"
        }
    },
    "3. Glass Comp": {
        "macro_en": "GLASS COMPONENT",
        "Particolari": {
            "Vetro temprato": "TEMPERED GLASS",
            "Vetro stratificato": "LAMINATED GLASS",
            "Finitura acidata": "ACID-ETCHED FINISH",
            "Bordo filo lucido": "POLISHED EDGE"
        }
    },
    "4. Wood Comp": {
        "macro_en": "WOOD COMPONENT",
        "Particolari": {
            "Legno di Rovere": "OAK WOOD",
            "Multistrato": "PLYWOOD",
            "Finitura naturale": "NATURAL FINISH",
            "Verniciatura opaca": "MATTE PAINTING"
        }
    },
    "5. Electric Comp": {
        "macro_en": "ELECTRIC COMPONENT",
        "Particolari": {
            "Cablaggio standard": "STANDARD WIRING",
            "Grado IP65": "IP65 RATING",
            "Protezione termica": "THERMAL PROTECTION",
            "Modulo LED": "LED MODULE"
        }
    },
    "6. Fastner": {
        "macro_en": "FASTENER",
        "Particolari": {
            "Acciaio zincato": "ZINC PLATED STEEL",
            "Acciaio Inox A2": "STAINLESS STEEL A2",
            "Classe 8.8": "8.8 GRADE",
            "Filettatura metrica": "METRIC THREAD"
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
col_macro, col_dettagli = st.columns([1, 2], gap="large")

with col_macro:
    st.subheader("📂 1. Macro Categoria")
    # Selezione singola con titoli per esteso (Radio button)
    macro_it = st.radio(
        "Scegli una categoria (la selezione esclude le altre):",
        options=list(database.keys()),
        index=0
    )
    macro_en = database[macro_it]["macro_en"]

with col_dettagli:
    st.subheader("🔍 2. Dettagli e Input")
    
    # Sotto-menu che "esplodono" in base alla scelta sopra
    opzioni_part = list(database[macro_it]["Particolari"].keys())
    part_it = st.selectbox(f"Seleziona Particolare per {macro_it}:", opzioni_part)
    part_en = database[macro_it]["Particolari"][part_it]
    
    # Campi fissi e manuali
    comp_scelta = st.selectbox("5. Seleziona Compatibilità:", opzioni_compatibilita)
    
    dim_input = st.text_input("3. DIMENSIONI (es. 500X200 MM):").strip().upper()
    extra_it = st.text_input("4. EXTRA (Traduzione Automatica):", placeholder="Scrivi in italiano...").strip()

st.divider()

# --- LOGICA DI GENERAZIONE ---
if st.button("🚀 GENERA E TRADUCI STRINGA FINALE", use_container_width=True):
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
    st.markdown("### 📋 Risultato (English - Uppercase):")
    st.code(final_string, language=None)
    st.text_area("Copia rapida:", value=final_string, height=70)

# Sidebar informativa
st.sidebar.markdown(f"**Categoria Attiva:**\n{macro_it}")
st.sidebar.markdown("---")
st.sidebar.write("L'interfaccia a sinistra ti permette di cambiare categoria velocemente senza dover aprire menu a tendina.")
