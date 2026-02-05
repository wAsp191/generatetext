import streamlit as st

st.set_page_config(page_title="Technical Description Generator", layout="wide")

# --- DATABASE SOTTOASSIEMI (Etichetta IT -> Valore EN) ---
database = {
    "1. Sheet Metal": {
        "macro_en": "SHEET METAL",
        "Particolari": {
            "Ripiano": "SHELF",
            "Piegatura CNC": "CNC BENDING",
            "Saldatura TIG": "TIG WELDING",
            "Punzonatura": "PUNCHING"
        },
        "Compatibilità": {
            "Fissaggio a rivetto": "RIVET FIXING",
            "Sede per inserto filettato": "THREADED INSERT SEAT",
            "Accoppiamento a vite": "SCREW COUPLING"
        }
    },
    "2. Plastic Comp": {
        "macro_en": "PLASTIC COMPONENT",
        "Particolari": {
            "Stampaggio a iniezione": "INJECTION MOLDED",
            "Termoformato": "THERMOFORMED",
            "Resistente UV": "UV RESISTANT",
            "Polimero rinforzato": "REINFORCED POLYMER"
        },
        "Compatibilità": {
            "Aggancio a scatto": "SNAP-FIT MOUNTING",
            "Saldatura a ultrasuoni": "ULTRASONIC WELDING",
            "Sede per vite autofilettante": "SELF-TAPPING SCREW SEAT"
        }
    },
    "3. Glass Comp": {
        "macro_en": "GLASS COMPONENT",
        "Particolari": {
            "Vetro temprato": "TEMPERED GLASS",
            "Vetro stratificato": "LAMINATED GLASS",
            "Finitura acidata": "ACID-ETCHED FINISH",
            "Bordo filo lucido": "POLISHED EDGE"
        },
        "Compatibilità": {
            "Supporti a pinza": "CLAMP SUPPORT",
            "Incollaggio UV": "UV GLUING",
            "Guarnizione in silicone": "SILICONE GASKET"
        }
    },
    "4. Wood Comp": {
        "macro_en": "WOOD COMPONENT",
        "Particolari": {
            "Legno di Rovere": "OAK WOOD",
            "Multistrato": "PLYWOOD",
            "Finitura naturale": "NATURAL FINISH",
            "Verniciatura opaca": "MATTE PAINTING"
        },
        "Compatibilità": {
            "Incastro a coda di rondine": "DOVETAIL JOINT",
            "Ferramenta standard": "STANDARD HARDWARE",
            "Viti da legno": "WOOD SCREWS"
        }
    },
    "5. Electric Comp": {
        "macro_en": "ELECTRIC COMPONENT",
        "Particolari": {
            "Cablaggio standard": "STANDARD WIRING",
            "Grado IP65": "IP65 RATING",
            "Protezione termica": "THERMAL PROTECTION",
            "Modulo LED": "LED MODULE"
        },
        "Compatibilità": {
            "Tensione 220-240V": "220-240V VOLTAGE",
            "Attacco DIN": "DIN RAIL MOUNT",
            "Plug and Play": "PLUG AND PLAY"
        }
    },
    "6. Fastner": {
        "macro_en": "FASTENER",
        "Particolari": {
            "Acciaio zincato": "ZINC PLATED STEEL",
            "Acciaio Inox A2": "STAINLESS STEEL A2",
            "Classe 8.8": "8.8 GRADE",
            "Filettatura metrica": "METRIC THREAD"
        },
        "Compatibilità": {
            "Foro pre-filettato": "PRE-THREADED HOLE",
            "Chiave esagonale": "ALLEN KEY COMPATIBLE",
            "Rondella piana": "FLAT WASHER"
        }
    },
    "7. Other": {
        "macro_en": "OTHER",
        "Particolari": {
            "Materiale misto": "MIXED MATERIAL",
            "Specifica custom": "CUSTOM SPECIFICATION",
            "Accessorio": "ACCESSORY"
        },
        "Compatibilità": {
            "Verificare disegno": "CHECK TECHNICAL DRAWING",
            "Universale": "UNIVERSAL",
            "Non specificato": "NOT SPECIFIED"
        }
    }
}

# --- INTERFACCIA ---
st.title("⚙️ Universal Technical Description Generator")
st.markdown("Compila i campi in italiano per ottenere la stringa tecnica in inglese.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🛠️ Configurazione Selezionabile")
    # Selezione Macro
    macro_it = st.selectbox("Seleziona Macro Categoria:", list(database.keys()))
    macro_en = database[macro_it]["macro_en"]
    
    # Selezione Particolare dinamica
    opzioni_part = list(database[macro_it]["Particolari"].keys())
    part_it = st.selectbox("Seleziona Particolare (2):", opzioni_part)
    part_en = database[macro_it]["Particolari"][part_it]
    
    # Selezione Compatibilità dinamica
    opzioni_comp = list(database[macro_it]["Compatibilità"].keys())
    comp_it = st.selectbox("Seleziona Compatibilità (5):", opzioni_comp)
    comp_en = database[macro_it]["Compatibilità"][comp_it]

with col2:
    st.subheader("✍️ Input Manuale")
    # Campi manuali con conversione automatica in maiuscolo e rimozione spazi inutili
    dim_input = st.text_input("3. DIMENSIONI (es. 500X200 MM):").strip().upper()
    extra_input = st.text_input("4. EXTRA (es. COLOR RAL 9005):").strip().upper()

st.divider()

# --- GENERAZIONE STRINGA ---
if st.button("🚀 GENERA STRINGA FINALE", use_container_width=True):
    # Logica per gestire i campi vuoti
    dim_final = dim_input if dim_input else "N/A"
    extra_final = extra_input if extra_input else "NONE"
    
    # Assemblaggio finale
    # Formato: MACRO - PARTICOLARE - DIMENSIONI - EXTRA - COMPATIBILITÀ
    final_string = f"{macro_en} - {part_en} - {dim_final} - {extra_final} - {comp_en}"
    final_string = final_string.upper()

    # Visualizzazione Risultati
    st.success("Stringa tecnica generata con successo!")
    
    st.markdown("### 📋 Risultato da copiare:")
    st.code(final_string, language=None)
    
    # Area di testo per copia rapida da mobile/desktop
    st.text_area("Seleziona e copia:", value=final_string, height=70)

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.info("""
**Istruzioni:**
1. Scegli la categoria.
2. Seleziona i dettagli dai menu.
3. Inserisci misure e note extra.
4. Copia la stringa inglese pronta.
""")
