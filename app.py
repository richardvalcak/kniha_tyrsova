# app.py – Opravená kniha hostů Apartmán Tyršova (pouze Streamlit!)
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import re

# Nastavení souboru
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "hoste.csv")

os.makedirs(DATA_DIR, exist_ok=True)

if not os.path.exists(DATA_FILE):
    columns = ["Příjezd", "Jméno 1", "Datum narození 1", "Jméno 2", "Datum narození 2"]
    pd.DataFrame(columns=columns).to_csv(DATA_FILE, index=False)

def validate_date(date_str):
    pattern = r'^\d{1,2}\.\s*\d{1,2}\.\s*\d{4}$'
    if re.match(pattern, date_str):
        try:
            parts = [int(p.strip()) for p in date_str.split('.')]
            datetime(day=parts[0], month=parts[1], year=parts[2])
            return True
        except ValueError:
            return False
    return False

@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)

def save_entry(prichod, jmeno1, datum1, jmeno2, datum2):
    df = load_data()
    new_entry = pd.DataFrame([{
        "Příjezd": prichod,
        "Jméno 1": jmeno1,
        "Datum narození 1": datum1,
        "Jméno 2": jmeno2 if jmeno2 else "",
        "Datum narození 2": datum2 if datum2 else ""
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# Streamlit UI
st.set_page_config(page_title="Apartmán Tyršova – Kniha hostů", page_icon="🏠", layout="wide")
st.title("🏠 Apartmán Tyršova – Kniha hostů")

st.markdown("""
**Adresa: Tyršova 1239/1, 669 02 Znojmo**  
*Tato kniha slouží k registraci hostů podle zákona č. 326/1999 Sb. Data jsou ukládána pouze pro legální účely.*
""")

with st.form("host_form", clear_on_submit=True):
    st.subheader("📝 Registrace hostů")
    col1, col2 = st.columns(2)
    
    with col1:
        prichod = st.date_input("Datum příjezdu *", value=datetime.now())
        jmeno1 = st.text_input("1. Osoba – Jméno *", placeholder="Jan Novák")
        datum1 = st.text_input("1. Osoba – Datum narození * (DD. MM. YYYY)", placeholder="15. 6. 1985")
    
    with col2:
        jmeno2 = st.text_input("2. Osoba – Jméno", placeholder="Anna Nováková")
        datum2 = st.text_input("2. Osoba – Datum narození (DD. MM. YYYY)", placeholder="22. 9. 1988")
    
    submitted = st.form_submit_button("Zaregistrovat hosty")
    
    if submitted:
        errors = []
        if not jmeno1.strip():
            errors.append("Vyplňte jméno 1. osoby.")
        if not validate_date(datum1):
            errors.append("Datum 1. osoby: formát DD. MM. YYYY")
        if jmeno2.strip() and not validate_date(datum2):
            errors.append("Datum 2. osoby: formát DD. MM. YYYY.")
        
        if not errors:
            save_entry(prichod.strftime("%d.%m.%Y"), jmeno1.strip(), datum1.strip(), jmeno2.strip() if jmeno2 else "", datum2.strip() if datum2 else "")
            st.success("Hosté zaregistrováni!")
            st.rerun()
        else:
            for e in errors: st.error(e)

st.markdown("---")
st.subheader("📊 Seznam hostů")
df = load_data()
if not df.empty:
    st.dataframe(df[::-1].reset_index(drop=True), use_container_width=True, hide_index=True)
    if st.button("📥 Stáhnout CSV"):
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Stáhnout", csv, "hoste.csv", "text/csv")
else:
    st.info("Zatím žádní hosté.")
