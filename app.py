# app.py – Kniha hostů | Modernizovaná verze
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

# --- Google Sheets připojení ---
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

# --- Poděkování ---
if st.session_state.get('odeslano', False):
    st.success("✅ Děkujeme! Vaše údaje byly uloženy.")
    st.stop()

# --- Nadpis ---
st.markdown("<h2 style='text-align:center;'>Kniha hostů – Apartmán Tyršova</h2>", unsafe_allow_html=True)

# --- Paměť formuláře ---
if 'form_data' not in st.session_state:
    st.session_state.form_data = {
        'pocet_osob': 1, 'prichod': datetime.today(), 'odjezd': datetime.today(),
        'telefon': '', 'email': '',
        'j1': '', 'n1': '', 'a1': '', 'd1': '',
        'j2': '', 'n2': '', 'a2': '', 'd2': '',
        'souhlas': False
    }

# --- Výběr počtu osob ---
pocet_osob = st.selectbox("Počet osob", [1, 2], index=0 if st.session_state.form_data['pocet_osob']==1 else 1)

with st.form("checkin", clear_on_submit=False):
    # --- Datum příjezdu a odjezdu vedle sebe ---
    col1, col2 = st.columns(2)
    with col1:
        prichod = st.date_input("Příjezd", st.session_state.form_data['prichod'])
    with col2:
        odjezd = st.date_input("Odjezd", st.session_state.form_data['odjezd'])

    # --- Kontakt vedle sebe ---
    col1, col2 = st.columns(2)
    with col1:
        telefon = st.text_input("Telefon", st.session_state.form_data['telefon'], placeholder="+420 777 123 456")
    with col2:
        email = st.text_input("Email", st.session_state.form_data['email'], placeholder="jan@seznam.cz")

    st.markdown("### 1. Osoba")
    col1, col2 = st.columns(2)
    with col1:
        j1 = st.text_input("Jméno a příjmení", st.session_state.form_data['j1'], key="j1")
        n1 = st.text_input("Datum narození", st.session_state.form_data['n1'], key="n1", placeholder="1. 1. 1985")
    with col2:
        a1 = st.text_input("Adresa", st.session_state.form_data['a1'], key="a1")
        d1 = st.text_input("Doklad", st.session_state.form_data['d1'], key="d1")

    # --- Druhá osoba pokud je počet 2 ---
    if pocet_osob == 2:
        st.markdown("### 2. Osoba")
        col1, col2 = st.columns(2)
        with col1:
            j2 = st.text_input("Jméno a příjmení", st.session_state.form_data['j2'], key="j2")
            n2 = st.text_input("Datum narození", st.session_state.form_data['n2'], key="n2", placeholder="1. 1. 1985")
        with col2:
            a2 = st.text_input("Adresa", st.session_state.form_data['a2'], key="a2")
            d2 = st.text_input("Doklad", st.session_state.form_data['d2'], key="d2")
    else:
        j2 = n2 = a2 = d2 = ""

    st.markdown("---")
    souhlas = st.checkbox("Souhlasím se zpracováním osobních údajů", value=st.session_state.form_data['souhlas'])

    submitted = st.form_submit_button("Odeslat", use_container_width=True)

    if submitted:
        st.session_state.form_data.update({
            'pocet_osob': pocet_osob, 'prichod': prichod, 'odjezd': odjezd,
            'telefon': telefon, 'email': email,
            'j1': j1, 'n1': n1, 'a1': a1, 'd1': d1,
            'j2': j2 if pocet_osob==2 else '', 'n2': n2 if pocet_osob==2 else '',
            'a2': a2 if pocet_osob==2 else '', 'd2': d2 if pocet_osob==2 else '',
            'souhlas': souhlas
        })

        errors = []
        if prichod >= odjezd: errors.append("Odjezd musí být po příjezdu.")
        if not telefon.strip(): errors.append("Vyplňte telefon.")
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email.strip()): errors.append("Vyplňte platný email.")
        def valid_narozeni(n): return bool(re.match(r"^\s*\d{1,2}\.\s*\d{1,2}\.\s*\d{4}\s*$", n))
        if not valid_narozeni(n1): errors.append("Špatný formát data narození 1. osoby.")
        if pocet_osob==2 and not valid_narozeni(n2): errors.append("Špatný formát data narození 2. osoby.")
        if not d1.strip(): errors.append("Vyplňte doklad 1. osoby.")
        if pocet_osob==2 and not d2.strip(): errors.append("Vyplňte doklad 2. osoby.")
        required = [j1, n1, a1, email]
        if pocet_osob==2: required += [j2, n2, a2]
        if not all(field.strip() for field in required): errors.append("Vyplňte všechna povinná pole.")
        if not souhlas: errors.append("Souhlas je povinný.")

        if errors:
            for e in errors: st.error(e)
            st.stop()

        # --- Uložit do Sheets ---
        o2_data = {"jmeno": j2, "narozeni": n2, "adresa": a2, "doklad": d2} if pocet_osob==2 else {}
        row = [
            prichod.strftime("%d.%m.%Y"), odjezd.strftime("%d.%m.%Y"), pocet_osob,
            j1.strip(), n1.strip(), a1.strip(), d1.strip(),
            o2_data.get("jmeno", ""), o2_data.get("narozeni", ""),
            o2_data.get("adresa", ""), o2_data.get("doklad", ""),
            telefon.strip(), email.strip(), datetime.now().strftime("%d.%m.%Y %H:%M")
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
