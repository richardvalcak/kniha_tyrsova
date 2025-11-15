# app.py – Kniha hostů Apartmán Tyršova (CZ zákon)
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import re

# === Nastavení ===
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "hoste.csv")
os.makedirs(DATA_DIR, exist_ok=True)

# Vytvořit soubor
if not os.path.exists(DATA_FILE):
    columns = [
        "Příjezdu", "Počet osob",
        "Jméno 1", "Narození 1", "Adresa 1", "Doklad 1",
        "Jméno 2", "Narození 2", "Adresa 2", "Doklad 2"
    ]
    pd.DataFrame(columns=columns).to_csv(DATA_FILE, index=False)

# Validace data narození
def valid_date(text):
    if not re.match(r'^\d{1,2}\.\s*\d{1,2}\.\s*\d{4}$', text.strip()):
        return False
    try:
        d, m, y = map(int, [x.strip() for x in text.split('.')])
        datetime(y, m, d)
        return True
    except:
        return False

# Uložení
def save_data(prichod, pocet, data1, data2):
    df = pd.read_csv(DATA_FILE)
    row = {
        "Příjezdu": prichod,
        "Počet osob": pocet,
        "Jméno 1": data1["jmeno"], "Narození 1": data1["narozeni"],
        "Adresa 1": data1["adresa"], "Doklad 1": data1["doklad"],
        "Jméno 2": data2["jmeno"] if pocet == 2 else "",
        "Narození 2": data2["narozeni"] if pocet == 2 else "",
        "Adresa 2": data2["adresa"] if pocet == 2 else "",
        "Doklad 2": data2["doklad"] if pocet == 2 else ""
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# === UI – Přesně jako na Renderu, ale chytře ===
st.set_page_config(page_title="Apartmán Tyršova", layout="centered")

st.markdown("""
<style>
    .big { font-size: 32px !important; font-weight: bold; text-align: center; }
    .small { font-size: 16px; text-align: center; color: #555; }
    .box { background: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big">Apartmán Tyršova – Kniha hostů</p>', unsafe_allow_html=True)
st.markdown('<p class="small">Tyršova 1239/1, 669 02 Znojmo</p>', unsafe_allow_html=True)
st.markdown("---")

with st.container():
    st.markdown("**Vyplňte prosím údaje o ubytovaných osobách:**")
    st.markdown("*Datum narození: 15. 6. 1985 | Doklad: číslo OP nebo pasu*")

    with st.form("reg_form", clear_on_submit=True):
        # --- Počet osob ---
        pocet_osob = st.selectbox("Počet ubytovaných osob *", [1, 2], index=0)

        # --- Datum příjezdu ---
        prichod = st.date_input("Datum příjezdu *", value=datetime.today())

        st.markdown("---")

        # --- Osoba 1 (vždy) ---
        st.subheader("1. Osoba")
        col1a, col1b = st.columns(2)
        with col1a:
            j1 = st.text_input("Jméno a příjmení *", key="j1", placeholder="Jan Novák")
            n1 = st.text_input("Datum narození *", key="n1", placeholder="15. 6. 1985")
        with col1b:
            a1 = st.text_input("Adresa bydliště *", key="a1", placeholder="Hlavní 123, Brno")
            d1 = st.text_input("Číslo dokladu *", key="d1", placeholder="123456789")

        # --- Osoba 2 (jen pokud 2 osoby) ---
        if pocet_osob == 2:
            st.markdown("---")
            st.subheader("2. Osoba")
            col2a, col2b = st.columns(2)
            with col2a:
                j2 = st.text_input("Jméno a příjmení", key="j2", placeholder="Anna Nováková")
                n2 = st.text_input("Datum narození", key="n2", placeholder="22. 9. 1988")
            with col2b:
                a2 = st.text_input("Adresa bydliště", key="a2", placeholder="Hlavní 123, Brno")
                d2 = st.text_input("Číslo dokladu", key="d2", placeholder="987654321")

        submitted = st.form_submit_button("Zaregistrovat hosty", use_container_width=True)

        if submitted:
            # Získat data
            data1 = {"jmeno": j1.strip(), "narozeni": n1.strip(), "adresa": a1.strip(), "doklad": d1.strip()}
            data2 = {"jmeno": j2.strip() if pocet_osob == 2 else "", "narozeni": n2.strip() if pocet_osob == 2 else "",
                     "adresa": a2.strip() if pocet_osob == 2 else "", "doklad": d2.strip() if pocet_osob == 2 else ""}

            # Validace
            errors = []
            if not all([data1["jmeno"], data1["narozeni"], data1["adresa"], data1["doklad"]]):
                errors.append("Vyplňte všechny údaje 1. osoby.")
            if not valid_date(data1["narozeni"]):
                errors.append("Datum narození 1. osoby: formát 15. 6. 1985")
            if pocet_osob == 2 and not all([data2["jmeno"], data2["narozeni"], data2["adresa"], data2["doklad"]]):
                errors.append("Vyplňte všechny údaje 2. osoby.")
            if pocet_osob == 2 and not valid_date(data2["narozeni"]):
                errors.append("Datum narození 2. osoby: formát 15. 6. 1985")

            if errors:
                for e in errors: st.error(e)
            else:
                save_data(prichod.strftime("%d.%m.%Y"), pocet_osob, data1, data2)
                st.success("Hosté úspěšně zaregistrováni! Děkujeme za spolupráci.")
                st.balloons()

st.markdown("---")
st.markdown("""
<p style="text-align:center; color:#777; font-size:14px;">
    Vaše údaje jsou zpracovávány pouze pro účely evidence ubytování dle zákona č. 326/1999 Sb.<br>
    Nejsou předávány třetím stranám a jsou chráněny.
</p>
""", unsafe_allow_html=True)
