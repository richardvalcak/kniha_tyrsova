# app.py – Kniha hostů | VOLNÝ TELEFON | VERZE 7.3 | © 2025
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

# === PŘIPOJENÍ K GOOGLE SHEETS ===
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

# === PODĚKOVÁNÍ PO ODESLÁNÍ ===
if 'odeslano' in st.session_state and st.session_state.odeslano:
    st.markdown("<h2 style='text-align:center; color:#28a745;'>Děkujeme za vyplnění!</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center; margin:30px 0; padding:20px; background:#f8f9fa; border-radius:12px;'>
    <p style='font-size:18px; color:#333; margin:10px 0;'>
    Vaše údaje byly úspěšně uloženy.
    </p>
    <p style='font-size:16px; color:#555;'>
    Přejeme vám příjemný pobyt v Apartmánu Tyršova!
    </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# === NADPIS ===
st.markdown("<h1 style='text-align:center; color:#1a1a1a; margin-bottom:20px;'>Kniha hostů</h1>", unsafe_allow_html=True)

# === ÚVODNÍ TEXT ===
st.markdown("""
Vyplněním formuláře nám pomáháte splnit zákonem stanovené povinnosti vedení evidence ubytovaných osob a platby místního poplatku z pobytu.  
Vaše údaje jsou uchovávány v souladu s platnými právními předpisy a slouží výhradně k evidenci pobytu.  
**Apartmán Tyršova, Tyršova 1239/1, 669 02 Znojmo**
""")

st.markdown("---")

# === PAMĚŤ FORMULÁŘE ===
if 'form_data' not in st.session_state:
    st.session_state.form_data = {
        'pocet_osob': 1, 'prichod': datetime.today(), 'odjezd': datetime.today(),
        'telefon': '', 'email': '',
        'j1': '', 'n1': '', 'a1': '', 'd1': '',
        'j2': '', 'n2': '', 'a2': '', 'd2': '',
        'souhlas': False
    }

# === FORMULÁŘ S VALIDACÍ (telefon VOLNÝ) ===
with st.form("checkin", clear_on_submit=False):
    pocet_osob = st.selectbox("Počet osob *", [1, 2], index=0 if st.session_state.form_data['pocet_osob'] == 1 else 1)

    col1, col2 = st.columns(2)
    with col1: prichod = st.date_input("Příjezd *", st.session_state.form_data['prichod'])
    with col2: odjezd = st.date_input("Odjezd *", st.session_state.form_data['odjezd'])

    col_t, col_e = st.columns(2)
    with col_t:
        telefon = st.text_input("Telefon *", value=st.session_state.form_data['telefon'], placeholder="+420 777 123 456 nebo +49 151 1234567")
    with col_e:
        email = st.text_input("Email *", value=st.session_state.form_data['email'], placeholder="jan@seznam.cz")

    st.markdown("---")
    st.subheader("1. Osoba")
    c1a, c1b = st.columns(2)
    with c1a:
        j1 = st.text_input("Jméno a příjmení *", value=st.session_state.form_data['j1'], placeholder="Jan Novák")
        n1 = st.text_input("Narození * (15. 6. 1985)", value=st.session_state.form_data['n1'], placeholder="15. 6. 1985")
    with c1b:
        a1 = st.text_input("Adresa *", value=st.session_state.form_data['a1'], placeholder="Hlavní 123, Brno")
        d1 = st.text_input("Doklad *", value=st.session_state.form_data['d1'], placeholder="123456789")

    o2_data = {}
    if pocet_osob == 2:
        st.markdown("---")
        st.subheader("2. Osoba")
        c2a, c2b = st.columns(2)
        with c2a:
            j2 = st.text_input("Jméno *", value=st.session_state.form_data['j2'], key="j2", placeholder="Marie Nováková")
            n2 = st.text_input("Narození *", value=st.session_state.form_data['n2'], key="n2", placeholder="20. 8. 1990")
        with c2b:
            a2 = st.text_input("Adresa *", value=st.session_state.form_data['a2'], key="a2", placeholder="Hlavní 123, Brno")
            d2 = st.text_input("Doklad *", value=st.session_state.form_data['d2'], key="d2", placeholder="987654321")
        o2_data = {"jmeno": j2, "narozeni": n2, "adresa": a2, "doklad": d2}

    st.markdown("---")
    st.markdown("""
    **Souhlasím se zpracováním mých osobních údajů (jméno, příjmení, adresa, datum narození a údaje o pobytu) pro účely evidence ubytování v Apartmánu Tyršova, v souladu se zákonem č. 101/2000 Sb., o ochraně osobních údajů, a nařízení GDPR (EU) 2016/679.**  
    Souhlas je udělen dobrovolně a lze jej kdykoli odvolat. Tyto údaje budou uchovávány po dobu zákonem stanovenou pro evidenci pobytu hostů.
    """, unsafe_allow_html=True)
    souhlas = st.checkbox("**Souhlasím se zpracováním osobních údajů podle výše uvedeného textu**", value=st.session_state.form_data['souhlas'])

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_mid, col_right = st.columns([1, 1, 1])
    with col_mid:
        submitted = st.form_submit_button("ODESLAT ZÁZNAM", use_container_width=True, type="primary")
    st.markdown("<style>.stButton>button {background-color:#28a745 !important; color:white; font-weight:bold;}</style>", unsafe_allow_html=True)

    # === VALIDACE (telefon = jen vyplnit) ===
    if submitted:
        st.session_state.form_data.update({
            'pocet_osob': pocet_osob, 'prichod': prichod, 'odjezd': odjezd,
            'telefon': telefon, 'email': email,
            'j1': j1, 'n1': n1, 'a1': a1, 'd1': d1,
            'j2': j2 if pocet_osob == 2 else '', 'n2': n2 if pocet_osob == 2 else '',
            'a2': a2 if pocet_osob == 2 else '', 'd2': d2 if pocet_osob == 2 else '',
            'souhlas': souhlas
        })

        errors = []

        # 1. Datum
        if prichod >= odjezd:
            errors.append("Odjezd musí být po příjezdu.")

        # 2. Telefon – jen vyplněný (žádný formát)
        if not telefon.strip():
            errors.append("Zadejte telefonní číslo.")

        # 3. Email
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email.strip()):
            errors.append("Zadejte platný email (např. **jan@seznam.cz**)")

        # 4. Narození
        def valid_narozeni(n):
            return bool(re.match(r"^\d{1,2}\. \d{1,2}\. \d{4}$", n.strip()))
        if not valid_narozeni(n1):
            errors.append("Narození 1. osoby: **15. 6. 1985**")
        if pocet_osob == 2 and not valid_narozeni(n2):
            errors.append("Narození 2. osoby: **20. 8. 1990**")

        # 5. Doklad – 9 číslic
        if not re.match(r"^\d{9}$", d1.strip()):
            errors.append("Doklad 1. osoby musí mít **9 číslic**")
        if pocet_osob == 2 and not re.match(r"^\d{9}$", d2.strip()):
            errors.append("Doklad 2. osoby musí mít **9 číslic**")

        # 6. Povinná pole
        required = [j1, n1, a1, d1, email]
        if pocet_osob == 2:
            required += [j2, n2, a2, d2]
        if not all(field.strip() for field in required):
            errors.append("Vyplňte všechna povinná pole.")

        # 7. Souhlas
        if not souhlas:
            errors.append("Souhlas je povinný.")

        # === VÝSLEDEK ===
        if errors:
            for e in errors:
                st.error(e)
            st.stop()
        else:
            row = [
                prichod.strftime("%d. %m. %Y"), odjezd.strftime("%d. %m. %Y"), pocet_osob,
                j1.strip(), n1.strip(), a1.strip(), d1.strip(),
                o2_data.get("jmeno", ""), o2_data.get("narozeni", ""), 
                o2_data.get("adresa", ""), o2_data.get("doklad", ""),
                telefon.strip(), email.strip(), datetime.now().strftime("%d. %m. %Y %H:%M")
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
