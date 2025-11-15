# app.py – FINÁLNÍ: GDPR + pamatování dat + barevné tlačítko
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import re

# === Nastavení ===
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "hoste.csv")
os.makedirs(DATA_DIR, exist_ok=True)

if not os.path.exists(DATA_FILE):
    columns = [
        "Příjezd", "Odjezd", "Počet osob",
        "Jméno 1", "Narození 1", "Adresa 1", "Doklad 1",
        "Jméno 2", "Narození 2", "Adresa 2", "Doklad 2",
        "Telefon", "Email"
    ]
    pd.DataFrame(columns=columns).to_csv(DATA_FILE, index=False)

def valid_date(text):
    if not text.strip(): return False
    if not re.match(r'^\d{1,2}\.\s*\d{1,2}\.\s*\d{4}$', text.strip()):
        return False
    try:
        d, m, y = map(int, [x.strip() for x in text.split('.')])
        datetime(y, m, d)
        return True
    except:
        return False

def save(prichod, odjezd, pocet, o1, o2, tel, email):
    df = pd.read_csv(DATA_FILE)
    row = {
        "Příjezd": prichod, "Odjezd": odjezd, "Počet osob": pocet,
        "Jméno 1": o1["jmeno"], "Narození 1": o1["narozeni"],
        "Adresa 1": o1["adresa"], "Doklad 1": o1["doklad"],
        "Jméno 2": o2["jmeno"] if pocet == 2 else "",
        "Narození 2": o2["narozeni"] if pocet == 2 else "",
        "Adresa 2": o2["adresa"] if pocet == 2 else "",
        "Doklad 2": o2["doklad"] if pocet == 2 else "",
        "Telefon": tel, "Email": email
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# === UI ===
st.set_page_config(page_title="Apartmán Tyršova", layout="centered")

st.markdown("""
<style>
    .big { font-size: 32px !important; font-weight: bold; text-align: center; }
    .small { font-size: 16px; text-align: center; color: #555; }
    .stButton>button {
        background-color: #28a745 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
    }
    .stButton>button:hover {
        background-color: #218838 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big">Apartmán Tyršova – Kniha hostů</p>', unsafe_allow_html=True)
st.markdown('<p class="small">Tyršova 1239/1, 669 02 Znojmo</p>', unsafe_allow_html=True)
st.markdown("---")

# === VÝBĚR POČTU OSOB (mimo formulář) ===
st.markdown("**Vyberte počet ubytovaných osob:**")
pocet_osob = st.selectbox(
    "Počet osob *",
    [1, 2],
    index=st.session_state.get("pocet_osob", 0),
    key="pocet_osob"
)

# === FORMULÁŘ ===
with st.form("reg_form", clear_on_submit=False):  # PAMATUJE SI DATA!

    st.markdown("**Vyplňte údaje o ubytování:**")

    # --- Pobyt ---
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        prichod = st.date_input("Datum příjezdu *", value=datetime.today(), key="prichod")
    with col_date2:
        odjezd = st.date_input("Datum odjezdu *", value=datetime.today(), key="odjezd")

    # --- Kontakt ---
    st.markdown("**Kontaktní údaje:**")
    col_tel, col_mail = st.columns(2)
    with col_tel:
        telefon = st.text_input("Telefon *", placeholder="+420 777 123 456", key="tel")
    with col_mail:
        email = st.text_input("Email *", placeholder="jan@seznam.cz", key="mail")

    st.markdown("---")

    # === Osoba 1 (vždy) ===
    st.subheader("1. Osoba")
    col1a, col1b = st.columns(2)
    with col1a:
        j1 = st.text_input("Jméno a příjmení *", key="j1", placeholder="Jan Novák")
        n1 = st.text_input("Datum narození *", key="n1", placeholder="15. 6. 1985")
    with col1b:
        a1 = st.text_input("Adresa bydliště *", key="a1", placeholder="Hlavní 123, Brno")
        d1 = st.text_input("Číslo dokladu *", key="d1", placeholder="123456789")

    # === Osoba 2 (jen pokud 2 osoby) ===
    if pocet_osob == 2:
        st.markdown("---")
        st.subheader("2. Osoba")
        col2a, col2b = st.columns(2)
        with col2a:
            j2 = st.text_input("Jméno a příjmení *", key="j2", placeholder="Anna Nováková")
            n2 = st.text_input("Datum narození *", key="n2", placeholder="22. 9. 1988")
        with col2b:
            a2 = st.text_input("Adresa bydliště *", key="a2", placeholder="Hlavní 123, Brno")
            d2 = st.text_input("Číslo dokladu *", key="d2", placeholder="987654321")

    # --- GDPR Souhlas ---
    st.markdown("---")
    st.markdown("""
    **Souhlas se zpracováním osobních údajů:**  
    Souhlasím se zpracováním mých osobních údajů (jméno, příjmení, adresa, datum narození a údaje o pobytu) pro účely evidence ubytování v Apartmánu Tyršova, v souladu se zákonem č. 101/2000 Sb., o ochraně osobních údajů, a nařízení GDPR (EU) 2016/679.  
    Souhlas je udělen dobrovolně a lze jej kdykoli odvolat. Tyto údaje budou uchovávány po dobu zákonem stanovenou pro evidenci pobytu hostů.
    """)
    souhlas = st.checkbox("**Souhlasím se zpracováním osobních údajů podle výše uvedeného textu**", key="souhlas")

    # --- TLAČÍTKO ZAREGISTROVAT (ZELENÉ) ---
    submitted = st.form_submit_button("Zaregistrovat hosty", use_container_width=True)

    if submitted:
        o1 = {"jmeno": j1.strip(), "narozeni": n1.strip(), "adresa": a1.strip(), "doklad": d1.strip()}
        o2 = {
            "jmeno": j2.strip() if pocet_osob == 2 else "",
            "narozeni": n2.strip() if pocet_osob == 2 else "",
            "adresa": a2.strip() if pocet_osob == 2 else "",
            "doklad": d2.strip() if pocet_osob == 2 else ""
        }

        errors = []
        if prichod >= odjezd:
            errors.append("Odjezd musí být po příjezdu.")
        if not telefon.strip() or not email.strip():
            errors.append("Vyplňte telefon a email.")
        if not all(o1.values()):
            errors.append("Vyplňte všechny údaje 1. osoby.")
        if not valid_date(o1["narozeni"]):
            errors.append("Datum narození 1. osoby: formát 15. 6. 1985")
        if pocet_osob == 2:
            if not all(o2.values()):
                errors.append("Vyplňte všechny údaje 2. osoby.")
            if not valid_date(o2["narozeni"]):
                errors.append("Datum narození 2. osoby: formát 15. 6. 1985")
        if not souhlas:
            errors.append("Musíte souhlasit se zpracováním osobních údajů.")

        if errors:
            for e in errors: st.error(e)
        else:
            save(
                prichod.strftime("%d.%m.%Y"), odjezd.strftime("%d.%m.%Y"),
                pocet_osob, o1, o2, telefon.strip(), email.strip()
            )
            st.success("Hosté úspěšně zaregistrováni! Děkujeme za spolupráci.")
            st.balloons()

# === TLAČÍTKO PRO ZMĚNU POČTU OSOB ===
if st.button("Změnit počet osob a aktualizovat formulář"):
    st.rerun()

st.markdown("---")
st.markdown("""
<p style="text-align:center; color:#777; font-size:14px;">
    Apartmán Tyršova – evidence ubytování dle zákona č. 326/1999 Sb.<br>
    Kontakt: +420 XXX XXX XXX | info@tyrsova.cz
</p>
""", unsafe_allow_html=True)
