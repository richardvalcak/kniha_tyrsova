# app.py – Apartmán Tyršova | ÚVODNÍ TEXT + SOUHLAS | VERZE 4.2 | © 2025
import streamlit as st
from datetime import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(
    page_title="Apartmán Tyršova – Check-in",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# === TICHÉ PŘIPOJENÍ K GOOGLE SHEETS (bez hlášek) ===
sheet = None
try:
    if "GSPREAD_CREDENTIALS" in st.secrets:
        creds_dict = json.loads(st.secrets["GSPREAD_CREDENTIALS"])
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(st.secrets["SHEET_ID"]).worksheet(st.secrets["SHEET_NAME"])
except:
    pass  # Ticho

# === ÚVODNÍ TEXT ===
st.markdown("""
<div style='text-align:center; margin-bottom:30px; padding:20px; background:#f8f9fa; border-radius:12px;'>
<h2 style='margin:0; color:#1a1a1a;'>Kniha hostů</h2>
<p style='margin:10px 0 0; color:#555; font-size:16px;'>
Vyplněním formuláře nám pomáháte splnit zákonem stanovené povinnosti vedení evidence ubytovaných osob a platby místního poplatku z pobytu.<br>
Vaše údaje jsou uchovávány v souladu s platnými právními předpisy a slouží výhradně k evidenci pobytu.
</p>
<p style='margin:15px 0 0; font-weight:bold; color:#1a1a1a;'>
📍 Apartmán Tyršova, Tyršova 1239/1, 669 02 Znojmo
</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# === POČET OSOB ===
if 'pocet_osob' not in st.session_state:
    st.session_state.pocet_osob = 1

def update_pocet():
    st.session_state.pocet_osob = st.session_state.pocet_temp

st.selectbox("Počet osob *", [1, 2], key="pocet_temp", on_change=update_pocet)
pocet_osob = st.session_state.pocet_osob

# === FORMULÁŘ ===
with st.form("checkin", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1: prichod = st.date_input("Příjezd *", datetime.today())
    with col2: odjezd = st.date_input("Odjezd *", datetime.today())

    col_t, col_e = st.columns(2)
    with col_t: telefon = st.text_input("Telefon *", placeholder="+420 777 123 456")
    with col_e: email = st.text_input("Email *", placeholder="jan@seznam.cz")

    st.markdown("---")
    st.subheader("1. Osoba")
    c1a, c1b = st.columns(2)
    with c1a:
        j1 = st.text_input("Jméno a příjmení *", placeholder="Jan Novák")
        n1 = st.text_input("Narození * (15. 6. 1985)", placeholder="15. 6. 1985")
        stat1 = st.selectbox("Stát *", ["Česko", "Slovensko", "Německo", "Rakousko", "Polsko", "Ukrajina", "Rusko", "USA", "Jiná"])
    with c1b:
        a1 = st.text_input("Adresa *", placeholder="Hlavní 123, Brno")
        d1 = st.text_input("Doklad *", placeholder="123456789")
        ucel1 = st.selectbox("Účel *", ["turismus", "zaměstnání", "studium", "rodinné důvody", "jiný"])

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
        o2_data = {"jmeno": j2, "narozeni": n2, "stat": stat2, "ucel": ucel2, "adresa": a2, "doklad": d2}

    st.markdown("---")
    
    # === SOUHLAS ===
    st.markdown("""
    **Souhlasím se zpracováním mých osobních údajů (jméno, příjmení, adresa, datum narození a údaje o pobytu) pro účely evidence ubytování v Apartmánu Tyršova, v souladu se zákonem č. 101/2000 Sb., o ochraně osobních údajů, a nařízení GDPR (EU) 2016/679.**  
    Souhlas je udělen dobrovolně a lze jej kdykoli odvolat. Tyto údaje budou uchovávány po dobu zákonem stanovenou pro evidenci pobytu hostů.
    """, unsafe_allow_html=True)
    
    souhlas = st.checkbox("**Souhlasím se zpracováním osobních údajů podle výše uvedeného textu**", value=False)

    submitted = st.form_submit_button("ODESLAT ZÁZNAM")

    if submitted:
        errors = []
        if prichod >= odjezd: errors.append("Odjezd musí být po příjezdu.")
        if not all([j1.strip(), n1.strip(), a1.strip(), d1.strip(), telefon.strip(), email.strip()]): 
            errors.append("Vyplňte vše u 1. osoby.")
        if pocet_osob == 2 and not all([v.strip() for v in o2_data.values()]): 
            errors.append("Vyplňte vše u 2. osoby.")
        if not souhlas: errors.append("Souhlas je povinný.")

        if errors:
            for e in errors: st.error(e)
        else:
            row = [
                prichod.strftime("%d. %m. %Y"), odjezd.strftime("%d. %m. %Y"), pocet_osob,
                j1.strip(), n1.strip(), stat1, ucel1, a1.strip(), d1.strip(),
                o2_data.get("jmeno", ""), o2_data.get("narozeni", ""), o2_data.get("stat", ""), 
                o2_data.get("ucel", ""), o2_data.get("adresa", ""), o2_data.get("doklad", ""),
                telefon.strip(), email.strip(), datetime.now().strftime("%d. %m. %Y %H:%M")
            ]
            if sheet:
                try:
                    sheet.append_row(row)
                    st.success("Záznam uložen!")
                    st.balloons()
                except:
                    st.error("Chyba ukládání – kontaktuj správce.")
            else:
                st.error("Chyba ukládání – kontaktuj správce.")

