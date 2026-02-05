import streamlit as st

st.set_page_config(page_title="Technical Description Generator", layout="wide")

# --- DATABASE SOTTOASSIEMI (Etichetta IT -> Valore EN) ---
database = {
    "1. Sheet Metal": {
        "macro_en": "SHEET METAL",
        "Particolari": {
            "Taglio Laser": "LASER CUT",
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
    "7. Accessori": {
        "macro_en": "ACCESSORIES",
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

st.title("⚙️ Generatore Stringa Tecnica")
st.write("Scegli le opzioni in italiano, la stringa finale sarà in inglese.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Configurazione")
    # Menu Macro con i nomi richiesti
    macro_it = st.selectbox("Seleziona Macro Categoria:", list(database.keys()))
    macro_en = database[macro_it]["macro_en"]
    
    # Sotto-menu dinamici
    part_it = st.selectbox("Seleziona Particolare:", list(database[macro_it]["Particolari"].keys()))
    part_en = database[macro_it]["Particolari"][part_it]
    
    comp_it = st.selectbox("Seleziona Compatibilità:", list(database[macro_it]["Compatibilità"].keys()))
    comp_en = database[macro_it]["Compatibilità"][comp_it]

with col2:
    st.subheader("Campi Manuali")
    dim = st.text_input("3. DIMENSIONI (Stampatello)", placeholder="es. 500X200X2 MM").upper()
    extra = st.text_input("4. EXTRA (Stampatello)", placeholder="es. COLORE NERO").upper()

st.divider()

if st.button("🚀 GENERA DESCRIZIONE INGLESE", use_container_width=True):
    # Gestione valori vuoti
    dim_val = dim if dim else "N/A"
    extra_val = extra if extra else "NONE"
    
    # Composizione stringa finale: MACRO - PARTICOLARE - DIMENSIONI - EXTRA - COMPATIBILITA
    risultato = f"{macro_en} - {part_en} - {dim_val} - {extra_val} - {comp_en}"
    risultato = risultato.upper()

    st.success("Testo generato con successo!")
    st.code(risultato, language=None)
    st.text_area("Copia da qui:", value=risultato, height=70)
