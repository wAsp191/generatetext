import streamlit as st
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Technical Description Generator", layout="wide")

# =========================================================
# DATABASE CON EXTRA DEDICATI
# Struttura: "Voce IT": ["Traduzione EN", {"Extra IT": "Extra EN"}]
# =========================================================
DATABASE = {
    "1. Sheet Metal": {
        "macro_en": "SHEET METAL",
        "Particolari": {
            "Montante": ["UPRIGHT", {
                "Passo 25mm": "PITCH 25MM",
                "Passo 50mm": "PITCH 50MM",
                "Asola singola": "SINGLE SLOT",
                "Asola doppia": "DOUBLE SLOT"
            }],
            "Ripiano": ["SHELF", {
                "Carico pesante": "HEAVY LOAD",
                "Slim": "SLIM VERSION",
                "Anticaduta": "ANTI-FALL SYSTEM"
            }],
            "Corrente": ["BEAM", {
                "Senza ganci": "WITHOUT HOOKS",
                "Rinforzato": "REINFORCED"
            }],
            "Pannello di rivestimento": ["BACK PANEL", {
                "Forato": "PERFORATED",
                "Liscio": "SMOOTH"
            }]
            # Aggiungi qui gli altri seguendo lo schema sopra
        }
    }
}

OPZIONI_COMPATIBILITA = ["F25", "F25 BESPOKE", "F50", "F50 BESPOKE", "UNIVERSAL", "FORTISSIMO"]
EXTRA_COMUNI = {"Certificato CE": "CE CERTIFIED", "Ignifugo": "FIRE RETARDANT"}

# =========================================================
# LOGICA SESSIONE E RESET
# =========================================================
if 'reset_trigger' not in st.session_state:
    st.session_state.reset_trigger = False

def reset_all():
    st.session_state["dim_val"] = ""
    st.session_state["extra_text"] = ""
    st.session_state["extra_tags"] = []
    st.session_state["comp_tags"] = []

# =========================================================
# INTERFACCIA
# =========================================================
st.title("🛠️ Smart Technical Generator")

col_t, col_btn = st.columns([4, 1])
with col_btn:
    if st.button("🔄 AZZERA TUTTO", on_click=reset_all, use_container_width=True):
        st.rerun()

st.markdown("---")

col_macro, col_workarea = st.columns([1, 3], gap="large")

with col_macro:
    st.subheader("📂 1. Macro Categoria")
    macro_it = st.radio("Seleziona categoria:", options=list(DATABASE.keys()))
    macro_en = DATABASE[macro_it]["macro_en"]

with col_workarea:
    # 2. PARTICOLARE
    st.subheader("🔍 2. Particolare")
    part_dict = DATABASE[macro_it]["Particolari"]
    nomi_it_ordinati = sorted(list(part_dict.keys()))
    scelta_part_it = st.radio("Seleziona dettaglio:", options=nomi_it_ordinati, horizontal=True)
    
    # Recupero i dati del particolare scelto
    part_en = part_dict[scelta_part_it][0]
    extra_dedicati_dict = part_dict[scelta_part_it][1]

    st.markdown("---")
    
    # 3. DIMENSIONI
    st.subheader("📏 3. Dimensioni")
    dim_input = st.text_input("Inserisci misure:", key="dim_val").strip().upper()

    # 4. EXTRA (Dinamici in base al particolare)
    st.subheader(f"✨ 4. Extra specifici per: {scelta_part_it}")
    col_ex1, col_ex2 = st.columns([2, 1])
    
    with col_ex1:
        # Uniamo gli extra fissi comuni a quelli specifici del particolare
        opzioni_extra_totali = {**EXTRA_COMUNI, **extra_dedicati_dict}
        extra_selezionati = st.multiselect(
            "Seleziona opzioni dedicate:", 
            options=list(opzioni_extra_totali.keys()), 
            key="extra_tags"
        )
    with col_ex2:
        extra_libero = st.text_input("Note libere (Traduzione IT->EN):", key="extra_text").strip()

    # 5. COMPATIBILITÀ
    st.subheader("🔗 5. Compatibilità")
    comp_selezionate = st.multiselect("Seleziona modelli:", options=OPZIONI_COMPATIBILITA, key="comp_tags")

# =========================================================
# GENERAZIONE
# =========================================================
st.divider()

if st.button("🚀 GENERA STRINGA FINALE", use_container_width=True):
    # Recupero traduzioni extra (sia comuni che specifici)
    extra_final_list = [opzioni_extra_totali[ex] for ex in extra_selezionati]
    
    if extra_libero:
        try:
            extra_tradotto = GoogleTranslator(source='it', target='en').translate(extra_libero).upper()
            extra_final_list.append(extra_tradotto)
        except:
            extra_final_list.append(extra_libero.upper())
    
    extra_str = ", ".join(extra_final_list) if extra_final_list else "NONE"
    comp_str = ", ".join(comp_selezionate) if comp_selezionate else "UNIVERSAL"
    dim_final = dim_input if dim_input else "N/A"
    
    res = f"{macro_en} - {part_en} - {dim_final} - {extra_str} - {comp_str}".upper()

    st.success("Stringa tecnica generata!")
    st.code(res, language=None)
    st.text_area("Copia rapida:", value=res, height=70)

st.markdown("<style>.stRadio > div { flex-wrap: wrap; display: flex; gap: 10px; }</style>", unsafe_allow_html=True)
