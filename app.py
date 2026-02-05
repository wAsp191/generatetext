import streamlit as st

st.set_page_config(page_title="Generatore Tecnico Universale", layout="wide")

# --- DATABASE SOTTOASSIEMI (Etichetta Italiana: Valore Inglese) ---
database = {
    "Componente Plastico": {
        "macro_en": "PLASTIC COMPONENT",
        "Particolari": {
            "Stampato a iniezione": "INJECTION MOLDED",
            "Termoformato": "THERMOFORMED",
            "Resistente ai raggi UV": "UV RESISTANT",
            "Polimero rinforzato": "REINFORCED POLYMER"
        },
        "Compatibilità": {
            "Aggancio a scatto": "SNAP-FIT MOUNTING",
            "Saldatura a ultrasuoni": "ULTRASONIC WELDING",
            "Sede per vite autofilettante": "SELF-TAPPING SCREW SEAT"
        }
    },
    "Componente in Vetro": {
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
    "Componente in Legno": {
        "macro_en": "WOOD COMPONENT",
        "Particolari": {
            "Legno di Rovere": "OAK WOOD",
            "Multistrato di pioppo": "POPLAR PLYWOOD",
            "Finitura naturale": "NATURAL FINISH",
            "Trattamento ignifugo": "FIRE RETARDANT TREATMENT"
        },
        "Compatibilità": {
            "Incastro a coda di rondine": "DOVETAIL JOINT",
            "Ferramenta standard": "STANDARD HARDWARE",
            "Fissaggio a scomparsa": "HIDDEN FIXING"
        }
    },
    "Componente Elettrico": {
        "macro_en": "ELECTRIC COMPONENT",
        "Particolari": {
            "Cablaggio UL/CSA": "UL/CSA WIRING",
            "Grado IP65": "IP65 RATING",
            "Protezione termica": "THERMAL PROTECTION",
            "Contatti dorati": "GOLD PLATED CONTACTS"
        },
        "Compatibilità": {
            "Tensione 220V": "220V VOLTAGE",
            "Montaggio su guida DIN": "DIN RAIL MOUNT",
            "Segnale 4-20mA": "4-20MA SIGNAL"
        }
    },
    "Elemento di Fissaggio": {
        "macro_en": "FASTENER",
        "Particolari": {
            "Acciaio zincato": "ZINC PLATED STEEL",
            "Classe 8.8": "8.8 GRADE",
            "Testa esagonale": "HEXAGONAL HEAD",
            "Filettatura parziale": "PARTIAL THREAD"
        },
        "Compatibilità": {
            "Foro pre-filettato": "PRE-THREADED HOLE",
            "Compatibile con chiavi fisse": "WRENCH/SOCKET COMPATIBLE",
            "Rondella piana": "FLAT WASHER"
        }
    },
    "Raccordo/Fitting": {
        "macro_en": "FITTING",
        "Particolari": {
            "Ottone nichelato": "NICKEL-PLATED BRASS",
            "Innesto rapido": "QUICK COUPLING",
            "Tenuta O-ring": "O-RING SEAL",
            "Filettatura Gas": "GAS THREAD"
        },
        "Compatibilità": {
            "Tubi Rilsan": "RILSAN HOSES",
            "Pressione max 10 bar": "MAX PRESSURE 10 BAR",
            "Fluidi idraulici": "HYDRAULIC FLUIDS"
        }
    }
}

st.title("🛠️ Generatore Descrizioni (IT -> EN)")
st.subheader("I menu sono in Italiano, il risultato sarà in Inglese Stampatello")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📌 Selezione (Italiano)")
    # Selezione Macro (mostra IT, salva EN)
    macro_it = st.selectbox("1. Categoria Macro", list(database.keys()))
    macro_en = database[macro_it]["macro_en"]
    
    # Selezione Particolare (mostra IT, salva EN)
    opzioni_part_it = list(database[macro_it]["Particolari"].keys())
    part_it = st.selectbox("2. Dettaglio Particolare", opzioni_part_it)
    part_en = database[macro_it]["Particolari"][part_it]
    
    # Selezione Compatibilità (mostra IT, salva EN)
    opzioni_comp_it = list(database[macro_it]["Compatibilità"].keys())
    comp_it = st.selectbox("5. Compatibilità", opzioni_comp_it)
    comp_en = database[macro_it]["Compatibilità"][comp_it]

with col2:
    st.markdown("### ✍️ Inserimento Manuale")
    dimensioni = st.text_input("3. DIMENSIONI (es. 10x20x5)", placeholder="Inserisci misure...").upper()
    extra = st.text_input("4. EXTRA / NOTE", placeholder="es. Certificato CE...").upper()

st.divider()

if st.button("🚀 GENERA STRINGA INGLESE", use_container_width=True):
    # Gestione valori vuoti
    dim_val = dimensioni if dimensioni else "N/A"
    extra_val = extra if extra else "NONE"
    
    # Composizione stringa finale (Tutto in Maiuscolo)
    stringa_finale = f"{macro_en} - {part_en} - {dim_val} - {extra_val} - {comp_en}"
    stringa_finale = stringa_finale.upper()

    st.subheader("✅ Risultato Finale (English - Uppercase):")
    st.code(stringa_finale, language=None)
    st.text_area("Copia da qui:", value=stringa_finale, height=70)

st.sidebar.info(f"""
**INFO TRADUZIONE:**
- Macro selezionata: {macro_en}
- Dettaglio: {part_en}
- Compatibilità: {comp_en}
""")
