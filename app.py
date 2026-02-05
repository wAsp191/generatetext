import streamlit as st

st.set_page_config(page_title="Product Description Generator", layout="wide")

# --- DATABASE SOTTOASSIEMI (Testi in Inglese) ---
database = {
    "PLASTIC COMPONENT": {
        "Particolari": ["INJECTION MOLDED", "THERMOFORMED", "UV RESISTANT", "REINFORCED POLYMER"],
        "Compatibilità": ["SNAP-FIT MOUNTING", "ULTRASONIC WELDING", "SELF-TAPPING SCREW SEAT"]
    },
    "GLASS COMPONENT": {
        "Particolari": ["TEMPERED GLASS", "LAMINATED GLASS", "ACID-ETCHED FINISH", "POLISHED EDGE"],
        "Compatibilità": ["CLAMP SUPPORT", "UV GLUING", "SILICONE GASKET"]
    },
    "WOOD COMPONENT": {
        "Particolari": ["OAK WOOD", "POPLAR PLYWOOD", "NATURAL FINISH", "FIRE RETARDANT TREATMENT"],
        "Compatibilità": ["DOVETAIL JOINT", "STANDARD HARDWARE", "HIDDEN FIXING"]
    },
    "ELECTRIC COMPONENT": {
        "Particolari": ["UL/CSA WIRING", "IP65 RATING", "THERMAL PROTECTION", "GOLD PLATED CONTACTS"],
        "Compatibilità": ["220V VOLTAGE", "DIN RAIL MOUNT", "4-20MA SIGNAL"]
    },
    "FASTNER": {
        "Particolari": ["ZINC PLATED STEEL", "8.8 GRADE", "HEXAGONAL HEAD", "PARTIAL THREAD"],
        "Compatibilità": ["PRE-THREADED HOLE", "WRENCH/SOCKET COMPATIBLE", "FLAT WASHER"]
    },
    "FITTING": {
        "Particolari": ["NICKEL-PLATED BRASS", "QUICK COUPLING", "O-RING SEAL", "GAS THREAD"],
        "Compatibilità": ["RILSAN HOSES", "MAX PRESSURE 10 BAR", "HYDRAULIC FLUIDS"]
    }
}

st.title("🏭 Universal Description Generator")
st.subheader("Output format: UPPERCASE - ENGLISH - DASH SEPARATED")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🛠 selection")
    macro = st.selectbox("1. MACRO CATEGORY", list(database.keys()))
    particolare = st.selectbox("2. PARTICULAR DETAIL", database[macro]["Particolari"])
    compatibilita = st.selectbox("5. COMPATIBILITY", database[macro]["Compatibilità"])

with col2:
    st.markdown("### 📝 Manual Input")
    # Usiamo .upper() per assicurarci che anche l'input manuale sia stampatello
    dimensioni = st.text_input("3. DIMENSIONS", placeholder="e.g. 100X50MM").upper()
    extra = st.text_input("4. EXTRA/NOTES", placeholder="e.g. ISO CERTIFIED").upper()

st.divider()

if st.button("🚀 GENERATE STRING", use_container_width=True):
    # Gestione campi vuoti per evitare trattini doppi inutili
    dim_val = dimensioni if dimensioni else "N/A"
    extra_val = extra if extra else "NONE"
    
    # Creazione della stringa finale concatenata
    # Tutto viene convertito in .upper() per sicurezza
    stringa_finale = f"{macro} - {particolare} - {dim_val} - {extra_val} - {compatibilita}"
    stringa_finale = stringa_finale.upper()

    st.subheader("✅ Final Universal Description:")
    
    # Area di testo per il copia-incolla rapido
    st.text_area("Ready to copy:", value=stringa_finale, height=100)
    
    # Visualizzazione pulita
    st.code(stringa_finale, language=None)

st.sidebar.warning("""
**RULES:**
1. All output is in **UPPERCASE**.
2. Language is **ENGLISH**.
3. Fields are separated by **" - "** symbol.
""")
