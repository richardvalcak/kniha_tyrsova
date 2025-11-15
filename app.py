# app.py – Kniha hostů | Moderní verze s instrukcemi a souhlasem
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

# --- Připojení k Google Sheets ---
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

# --- Poděkování po odeslání ---
if st.session_state.get('odeslano', False):
    st.success("✅ Děkujeme! Vaše údaje byly uloženy.")
    st.stop()

# --- Nadpis ---
st.markdown("<h1 style='text-align:center; color:#1a1a1a;'>Kniha hostů</h1>", unsafe_allow_html=True)

# --- Úvodní text ---
st.markdown("""
<div style="padding:15px; background-color:#f8f9fa; border-radius:12px;">
<p>Prosíme vás o vyplnění této knihy hostů.</p>
<p>Vyplněním formuláře nám pomáháte splnit zákonem stanovené povinnosti vedení evidence ubytovaných osob a platby místního poplatku z pobytu.</p>
<p>Vaše údaje jsou uchovávány v souladu s platnými právními předpisy a slouží výhradně k evidenci pobytu.</p>
<p><b>Apartmán Tyršova, Tyršova 1239/1, 669 02 Znojmo</b></p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

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
    # --- Datum příjezdu a odjezdu ---
    col1, col2 = st.columns(2)
    with col1:
        prichod = st.date_input("Příjezd", st.session_state.form_data['prichod'])
    with col2:
        odjezd = st.date_input("Odjezd", st.session_state.form_data['odjezd'])

    # --- Kontakt ---
    col1, col2 = st.columns(2)
    with col1:
        telefon = st.text_input("Telefon", st.session_state.form_data['telefon'], placeholder="+420 777 123 456")
    with col2:
        email = st.text_input("Email", st.session_state.form_data['email'], placeholder="jan@seznam.cz")

    # --- 1. Osoba ---
    st.markdown("### 1. Osoba")
    col1, col2 = st.columns(2)
    with col1:
        j1 = st.text_input("Jméno a příjmení", st.session_state.form_data['j1'], placeholder="Jan Novák")
        n1 = st.text_input("Datum narození", st.session_state.form_data['n1'], placeholder="15. 6. 1985")
    with col2:
        a1 = st.text_input("Adresa", st.session_state.form_data['a1'], placeholder="Hlavní 123, Brno")
        d1 = st.text_input("Doklad", st.session_state.form_data['d1'], placeholder="123456789 (OP)")

    # --- 2. Osoba ---
    if pocet_osob == 2:
        st.markdown("### 2. Osoba")
        col1, col2 = st.columns(2)
        with col1:
            j2 = st.text_input("Jméno a příjmení", st.session_state.form_data['j2'], placeholder="Marie Nováková")
            n2 = st.text_input("Datum narození", st.session_state.form_data['n2'], placeholder="20. 8. 1990")
        with col2:
            a2 = st.text_input("Adresa", st.session_state.form_data['a2'], placeholder="Hlavní 123, Brno")
            d2 = st.text_input("Doklad", st.session_state.form_data['d2'], placeholder="987654321 (OP)")
    else:
        j2 = n2 = a2 = d2 = ""

    st.markdown("---")

    # --- Souhlas s osobními údaji ---
    st.markdown("""
    <div style="padding:10px; background-color:#f1f1f1; border-radius:8px; font-size:14px;">
    <b>Souhlasím se zpracováním mých osobních údajů</b> (jméno, příjmení, adresa, datum narození a údaje o pobytu) 
    pro účely evidence ubytování v Apartmánu Tyršova, v souladu se zákonem č. 101/2000 Sb., o ochraně osobních údajů, 
    a nařízení GDPR (EU) 2016/679. Souhlas je udělen dobrovolně a lze jej kdykoli odvolat. 
    Tyto údaje budou uchovávány po dobu zákonem stanovenou pro evidenci pobytu hostů.
    </div>
    """, unsafe_allow_html=True)

    souhlas = st.checkbox("Souhlasím se zpracováním osobních údajů podle výše uvedeného textu.", value=st.session_state.form_data['souhlas'])

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Odeslat tlačítko ---
    submitted = st.form_submit_button(
        "ODESLAT ZÁZNAM",
        use_container_width=True
    )
    st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #28a745;
        color: white;
        font-weight: bold;
        height: 50px;
        font-size: 16px;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Validace a uložení ---
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
