# app.py – Přesná kopie https://kniha-tyrsova.onrender.com
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import re

# === Nastavení ===
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "hoste.csv")
os.makedirs(DATA_DIR, exist_ok=True)

# Vytvořit soubor, pokud neexistuje
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Příjezd", "Jméno 1", "Datum narození 1", "Jméno 2", "Datum narození 2"]).to_csv(DATA_FILE, index=False)

# Validace data
def validate_date(text):
    pattern = r'^\d{1,2}\.\s*\d{1,2}\.\s*\d{4}$'
    if not re.match(pattern, text.strip()):
        return False
    try:
        d, m, y = map(int, [x.strip() for x in text.split('.')])
        datetime(y, m, d)
        return True
    except:
        return False

# Uložení
def save(prichod, j1, d1, j2, d2):
    df = pd.read_csv(DATA_FILE)
    new = pd.DataFrame([{
        "Příjezd": prichod,
        "Jméno 1": j1,
        "Datum narození 1": d1,
        "Jméno 2": j2 or "",
        "Datum narození 2": d2 or ""
    }])
    pd.concat([df, new], ignore_index=True).to_csv(DATA_FILE, index=False)

# === UI – PŘESNĚ JAKO NA RENDERU ===
st.set_page_config(page_title="Apartmán Tyršova", layout="centered")

st.markdown("""
<style>
    .big-font { font-size: 32px !important; font-weight: bold; text-align: center; }
    .small-font { font-size: 16px; text-align: center; color: #555; }
    .form-box { background: #f9f9f9; padding: 20px; border-radius: 10px; border: 1px solid #ddd; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">Apartmán Tyršova – Kniha hostů</p>', unsafe_allow_html=True)
st.markdown('<p class="small-font">Tyršova 1239/1, 669 02 Znojmo</p>', unsafe_allow_html=True)

st.markdown("---")

with st.container():
    st.markdown("**Vyplňte prosím údaje o ubytovaných osobách:**")
    st.markdown("*Datum narození ve formátu: 15. 6. 1985*")

    with st.form("reg_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.date_input("Datum příjezdu", value=datetime.today(), key="prichod")
            st.text_input("Jméno a příjmení 1. osoby", placeholder="Jan Novák", key="j1")
            st.text_input("Datum narození 1. osoby", placeholder="15. 6. 1985", key="d1")
        
        with col2:
            st.text_input("Jméno a příjmení 2. osoby (pokud je)", placeholder="Anna Nováková", key="j2")
            st.text_input("Datum narození 2. osoby (pokud je)", placeholder="22. 9. 1988", key="d2")
        
        submitted = st.form_submit_button("Zaregistrovat", use_container_width=True)
        
        if submitted:
            j1 = st.session_state.j1.strip()
            d1 = st.session_state.d1.strip()
            j2 = st.session_state.j2.strip() if st.session_state.j2 else ""
            d2 = st.session_state.d2.strip() if st.session_state.d2 else ""
            prichod = st.session_state.prichod.strftime("%d.%m.%Y")
            
            if not j1 or not d1:
                st.error("Vyplňte prosím údaje 1. osoby.")
            elif not validate_date(d1):
                st.error("Datum narození 1. osoby musí být ve formátu 15. 6. 1985")
            elif j2 and not validate_date(d2):
                st.error("Datum narození 2. osoby musí být ve formátu 15. 6. 1985")
            else:
                save(prichod, j1, d1, j2, d2)
                st.success("Hosté byli úspěšně zaregistrováni. Děkujeme!")
                st.balloons()

st.markdown("---")
st.markdown("""
<p style="text-align:center; color:#777; font-size:14px;">
    Data jsou ukládána pouze pro účely evidence ubytování dle zákona č. 326/1999 Sb.<br>
    Nejsou sdílena s třetími stranami.
</p>
""", unsafe_allow_html=True)
