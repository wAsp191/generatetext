import streamlit as st

# 1. Configurazione della pagina
st.set_page_config(page_title="Technical Generator", page_icon="🚀", layout="wide")

# 2. Definiamo i puntatori ai file reali nelle cartelle
# app.py farà solo da vigile urbano, reindirizzando subito ai file corretti
pagina_generatore = st.Page("pages/0_Technical_Generator.py", title="Technical Generator", icon="🚀", default=True)
pagina_analytics = st.Page("pages/1_Analytics.py", title="Analytics", icon="📊")

# 3. Avvia la navigazione
pg = st.navigation([pagina_generatore, pagina_analytics])
pg.run()
