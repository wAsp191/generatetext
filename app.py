import streamlit as st

st.set_page_config(page_title="Technical Description Generator", layout="wide")

# --- LISTA COMPATIBILITÀ FISSA ---
opzioni_compatibilita = [
    "F25", 
    "F25 BESPOKE", 
    "F50", 
    "F50 BESPOKE", 
    "UNIVERSAL", 
    "FORTISSIMO"
]

# --- DATABASE SOTTOASSIEMI (Etichetta IT -> Valore EN) ---
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

# --- INTERFACCIA APP ---
st.title("⚙️ Universal Technical Description Generator")
st.markdown("Generazione stringhe tecniche in lingua inglese - Formato Stampatello")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🛠️ Selezione")
    
    # 1. Selezione Macro
    macro_it = st.selectbox("Seleziona Macro Categoria:", list(database.keys()))
    macro_en = database[macro_it]["macro_en"]
    
    # 2. Selezione Particolare dinamica
    opzioni_part = list(database[macro_it]["Particolari"].keys())
    part_it = st.selectbox("Seleziona Particolare (2):", opzioni_part)
    part_en = database[macro_it]["Particolari"][part_it]
    
    # 5. Selezione Compatibilità (FISSA come richiesto)
    comp_scelta = st.selectbox("Seleziona Compatibilità (5):", opzioni_compatibilita)

with col2:
    st.subheader("✍️ Input Manuale")
    # Campi manuali
    dim_input = st.text_input("3. DIMENSIONI (es. 500X200 MM):").strip().upper()
    extra_input = st.text_input("4. EXTRA (es. COLOR RAL 9005):").strip().upper()

st.divider()

# --- GENERAZIONE STRINGA ---
if st.button("🚀 GENERA STRINGA FINALE", use_container_width=True):
    # Gestione valori vuoti
    dim_final = dim_input if dim_input else "N/A"
    extra_final = extra_input if extra_input else "NONE"
    
    # Assemblaggio finale: MACRO - PARTICOLARE - DIMENSIONI - EXTRA - COMPATIBILITÀ
    # Nota: comp_scelta è già in inglese/stampatello nel menu
    final_string = f"{macro_en} - {part_en} - {dim_final} - {extra_final} - {comp_scelta}"
    final_string = final_string.upper()

    # Visualizzazione
    st.success("Stringa tecnica generata correttamente!")
    
    st.markdown("### 📋 Risultato da copiare:")
    st.code(final_string, language=None)
    
    st.text_area("Copia rapida:", value=final_string, height=70)

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.info("L'output è configurato per essere sempre in lingua inglese e in stampatello.")
