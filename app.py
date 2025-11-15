# app.py – Ubytování Tyršova | GOOGLE SHEETS | VERZE 3.0 | © 2025
import streamlit as st
import pandas as pd
from datetime import datetime
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

st.set_page_config(page_title="Apartmán Tyršova – Check-in", layout="centered")

# === GOOGLE SHEETS NASTAVENÍ ===
try:
    creds_dict = json.loads(st.secrets["GSPREAD_CREDENTIALS"])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(st.secrets["SHEET_ID"]).worksheet(st.secrets["SHEET_NAME"])
except Exception as e:
    st.error("Chyba připojení k Google Sheets. Zkontroluj secrets.toml")
    st.stop()

# === DESIGN ===
st.markdown("<h1 style='text-align:center;'>Apartmán Tyršova</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Tyršova 1239/1, 669 02 Znojmo</p>", unsafe_allow_html=True)
st.markdown("---")

# === POČET OSOB ===
if 'pocet_osob' not in st.session_state:
    st.session_state.pocet_osob = 1

def update_pocet():
    st.session_state.pocet_osob = st.session_state.pocet_temp

st.selectbox(
    "Počet osob *",
    [1, 2],
    key="pocet_temp",
    on_change=update_pocet,
    help="Po výběru 2 osob se objeví formulář pro druhou osobu."
)
pocet_osob = st.session_state.pocet_osob

# === FORMULÁŘ ===
with st.form("checkin", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        prichod = st.date_input("Příjezd *", value=datetime.today(), key="prichod")
    with col2:
        odjezd = st.date_input("Odjezd *", value=datetime.today(), key="odjezd")

    col_t, col_e = st.columns(2)
    with col_t:
        telefon = st.text_input("Telefon *", placeholder="+420 777 123 456", key="tel")
    with col_e:
        email = st.text_input("Email *", placeholder="jan@seznam.cz", key="email")

    st.markdown("---")
    st.subheader("1. Osoba")
    c1a, c1b = st.columns(2)
    with c1a:
        j1 = st.text_input("Jméno a příjmení *", placeholder="Jan Novák", key="j1")
        n1 = st.text_input("Narození * (15. 6. 1985)", placeholder="15. 6. 1985", key="n1")
        stat1 = st.selectbox("Stát *", ["Česko", "Slovensko", "Německo", "Rakousko", "Polsko", "Ukrajina", "Rusko", "USA", "Jiná"], key="stat1")
    with c1b:
        a1 = st.text_input("Adresa *", placeholder="Hlavní 123, Brno", key="a1")
        d1 = st.text_input("Doklad *", placeholder="123456789", key="d1")
        ucel1 = st.selectbox("Účel *", ["turismus", "zaměstnání", "studium", "rodinné důvody", "jiný"], key="ucel1")

    o2_data = {}
    if pocet_osob == 2:
        st.markdown("---")
        st.subheader("2. Osoba")
        c2a, c2b = st.columns(2)
        with c2a:
            j2 = st.text_input("Jméno *", key="j2")
            n2 = st.text_input("Narození *", key="n2")
            stat2 = st.selectbox("Stát *", ["Česko", "Slovensko", "Německo", "Rakousko", "Polsko", "Ukrajina", "Rusko", "USA", "Jiná"], key="stat2")
        with c2b:
            a2 = st.text_input("Adresa *", key="a2")
            d2 = st.text_input("Doklad *", key="d2")
            ucel2 = st.selectbox("Účel *", ["turismus", "zaměstnání", "studium", "rodinné důvody", "jiný"], key="ucel2")
        o2_data = {
            "jmeno": j2, "narozeni": n2, "stat": stat2,
            "ucel": ucel2, "adresa": a2, "doklad": d2
        }

    st.markdown("---")
    st.markdown("**Souhlasím se zpracováním osobních údajů dle GDPR a zákona č. 326/1999 Sb.**")
    souhlas = st.checkbox("**Souhlasím**", value=False, key="souhlas")

    submitted = st.form_submit_button("ODESLAT ZÁZNAM")

    if submitted:
        # --- VALIDACE ---
        errors = []
        if prichod >= odjezd:
            errors.append("Odjezd musí být po příjezdu.")
        if not all([j1.strip(), n1.strip(), a1.strip(), d1.strip(), telefon.strip(), email.strip()]):
            errors.append("Vyplňte všechny povinné údaje u 1. osoby.")
        if pocet_osob == 2 and not all([v.strip() for v in o2_data.values()]):
            errors.append("Vyplňte všechny údaje u 2. osoby.")
        if not souhlas:
            errors.append("Musíte souhlasit se zpracováním údajů.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            # --- PŘÍPRAVA ŘÁDKU (KAŽDÝ ÚDAJ ZVLÁŠŤ!) ---
            row = [
                prichod.strftime("%d. %m. %Y"),    # Příjezd
                odjezd.strftime("%d. %m. %Y"),     # Odjezd
                pocet_osob,                        # Počet osob
                j1.strip(),                        # Jméno 1
                n1.strip(),                        # Narození 1
                stat1,                             # Stát 1
                ucel1,                             # Účel 1
                a1.strip(),                        # Adresa 1
                d1.strip(),                        # Doklad 1
                o2_data.get("jmeno", "").strip(),  # Jméno 2
                o2_data.get("narozeni", "").strip(), # Narození 2
                o2_data.get("stat", ""),           # Stát 2
                o2_data.get("ucel", ""),           # Účel 2
                o2_data.get("adresa", "").strip(), # Adresa 2
                o2_data.get("doklad", "").strip(), # Doklad 2
                telefon.strip(),                   # Telefon
                email.strip(),                     # Email
                datetime.now().strftime("%d. %m. %Y %H:%M")  # Zapsáno
            ]

            # --- ULOŽENÍ DO GOOGLE SHEETS ---
            try:
                sheet.append_row(row)
                st.success("Záznam úspěšně uložen do Google Sheets!")
                st.balloons()
            except Exception as e:
                st.error(f"Chyba při ukládání: {e}")

# === INFO O GOOGLE SHEETS ===
sheet_url = f"https://docs.google.com/spreadsheets/d/{st.secrets['SHEET_ID']}"
st.markdown("---")
st.markdown(f"""
<p style='text-align:center; font-size:14px;'>
    <strong>Data se automaticky ukládají do:</strong><br>
    <a href='{sheet_url}' target='_blank'>Otevřít Google Sheets</a>
</p>
""", unsafe_allow_html=True)
