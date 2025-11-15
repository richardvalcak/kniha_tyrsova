# app.py – Kniha hostů | VOLNÝ DOKLAD | VERZE 7.6 | © 2025
import streamlit as st
from datetime import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

st.set_page_config(
    page_title="Kniha hostů – Apartmán Tyršova",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# === GOOGLE SHEETS ===
sheet = None
try:
    if "GSPREAD_CREDENTIALS" in st.secrets:
        creds_dict = json.loads(st.secrets["GSPREAD_CREDENTIALS"])
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(st.secrets["SHEET_ID"]).worksheet(st.secrets["SHEET_NAME"])
except:
    pass

# === PO ODESLÁNÍ ===
if 'odeslano' in st.session_state and st.session_state.odeslano:
    st.markdown("<h2 style='text-align:center; color:#28a745;'>Děkujeme za vyplnění!</h2>", unsafe_allow_html=True)
    st.stop()

# ==============================
#  1) POČET OSOB (mimo formulář)
# ==============================
if "pocet_osob" not in st.session_state:
    st.session_state.pocet_osob = 1

st.session_state.pocet_osob = st.selectbox(
    "Počet osob *",
    [1, 2],
    index=0 if st.session_state.pocet_osob == 1 else 1,
)

pocet_osob = st.session_state.pocet_osob

st.markdown("---")

# ==========================
#  2) FORMULÁŘ
# ==========================
with st.form("checkin"):

    col1, col2 = st.columns(2)
    with col1:
        prichod = st.date_input("Příjezd *", value=datetime.today())
    with col2:
        odjezd = st.date_input("Odjezd *", value=datetime.today())

    col_t, col_e = st.columns(2)
    with col_t:
        telefon = st.text_input("Telefon *", placeholder="+420 777 123 456")
    with col_e:
        email = st.text_input("Email *", placeholder="jan@seznam.cz")

    st.markdown("---")
    st.subheader("1. Osoba")
    c1a, c1b = st.columns(2)
    with c1a:
        j1 = st.text_input("Jméno a příjmení *", placeholder="Jan Novák")
        n1 = st.text_input("Narození *", placeholder="15. 6. 1985")
    with c1b:
        a1 = st.text_input("Adresa *", placeholder="Hlavní 123, Brno")
        d1 = st.text_input("Doklad *", placeholder="123456789 (OP)")

    # ======== 2. OSOBA ========
    j2 = n2 = a2 = d2 = ""
    if pocet_osob == 2:
        st.markdown("---")
        st.subheader("2. Osoba")
        c2a, c2b = st.columns(2)
        with c2a:
            j2 = st.text_input("Jméno *", key="j2", placeholder="Marie Nováková")
            n2 = st.text_input("Narození *", key="n2", placeholder="20. 8. 1990")
        with c2b:
            a2 = st.text_input("Adresa *", key="a2", placeholder="Hlavní 123, Brno")
            d2 = st.text_input("Doklad *", key="d2", placeholder="987654321 (OP)")

    st.markdown("---")
    souhlas = st.checkbox("Souhlasím se zpracováním osobních údajů")

    submitted = st.form_submit_button("ODESLAT ZÁZNAM")

    # =======================================
    # VALIDACE
    # =======================================
    if submitted:

        errors = []

        if prichod >= odjezd:
            errors.append("Odjezd musí být po příjezdu.")

        if not telefon.strip():
            errors.append("Zadejte telefon.")

        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email.strip()):
            errors.append("Zadejte platný email.")

        # Volnější formát pro datum narození
        def valid_narozeni(n):
            return bool(re.match(r"^\s*\d{1,2}\.\s*\d{1,2}\.\s*\d{4}\s*$", n))

        if not valid_narozeni(n1):
            errors.append("Narození 1. osoby není správně.")

        if pocet_osob == 2 and not valid_narozeni(n2):
            errors.append("Narození 2. osoby není správně.")

        if not d1.strip():
            errors.append("Zadejte doklad 1. osoby.")

        if pocet_osob == 2 and not d2.strip():
            errors.append("Zadejte doklad 2. osoby.")

        # Povinná pole
        required = [j1, n1, a1, email]
        if pocet_osob == 2:
            required += [j2, n2, a2]

        if not all(x.strip() for x in required):
            errors.append("Vyplňte všechna povinná pole.")

        if not souhlas:
            errors.append("Souhlas je povinný.")

        if errors:
            for e in errors:
                st.error(e)
            st.stop()

        # ULOŽENÍ
        row = [
            prichod.strftime("%d. %m. %Y"),
            odjezd.strftime("%d. %m. %Y"),
            pocet_osob,
            j1, n1, a1, d1,
            j2, n2, a2, d2,
            telefon, email,
            datetime.now().strftime("%d. %m. %Y %H:%M")
        ]

        if sheet:
            try:
                sheet.append_row(row)
                st.session_state.odeslano = True
                st.rerun()
            except Exception as e:
                st.error(f"Chyba ukládání: {e}")
        else:
            st.error("Chyba připojení k Google Sheets.")
