# app.py – Kniha hostů | Moderní verze | © 2025
import streamlit as st
from datetime import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

st.set_page_config(
    page_title="Kniha hostů – Apartmán Tyršova",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Překlady / Translations ---
TRANSLATIONS = {
    "cs": {
        "page_title": "Kniha hostů",
        "app_title": "Kniha hostů",
        "intro": """
<div style="padding:15px; background-color:#f8f9fa; border-radius:12px;">
<p>Prosíme vás o vyplnění této knihy hostů.</p>
<p>Vyplněním formuláře nám pomáháte splnit zákonem stanovené povinnosti vedení evidence ubytovaných osob a platby místního poplatku z pobytu.</p>
<p>Vaše údaje jsou uchovávány v souladu s platnými právními předpisy a slouží výhradně k evidenci pobytu.</p>
<p><b>Apartmán Tyršova, Tyršova 1239/1, 669 02 Znojmo</b></p>
</div>
""",
        "pocet_osob": "Počet osob *",
        "prichod": "Příjezd *",
        "odjezd": "Odjezd *",
        "telefon": "Telefon *",
        "email": "Email *",
        "osoba_1": "### 1. Osoba",
        "osoba_2": "### 2. Osoba",
        "jmeno": "Jméno a příjmení *",
        "jmeno_2": "Jméno a příjmení 2. osoby *",
        "narozeni": "Datum narození *",
        "narozeni_2": "Datum narození 2. osoby *",
        "adresa": "Adresa *",
        "adresa_2": "Adresa 2. osoby *",
        "doklad": "Doklad *",
        "doklad_2": "Doklad 2. osoby *",
        "ph_jmeno": "Jan Novák",
        "ph_jmeno_2": "Marie Nováková",
        "ph_narozeni": "15. 6. 1985",
        "ph_adresa": "Hlavní 123, Brno",
        "ph_doklad": "123456789 (OP)",
        "ph_telefon": "+420 777 123 456",
        "ph_email": "jan@seznam.cz",
        "gdpr_text": """
<div style="padding:10px; background-color:#f1f1f1; border-radius:8px; font-size:14px;">
<b>Souhlasím se zpracováním mých osobních údajů</b> (jméno, příjmení, adresa, datum narození a údaje o pobytu) 
pro účely evidence ubytování v Apartmánu Tyršova, v souladu se zákonem č. 101/2000 Sb., o ochraně osobních údajů, 
a nařízení GDPR (EU) 2016/679. Souhlas je udělen dobrovolně a lze jej kdykoli odvolat. 
Tyto údaje budou uchovávány po dobu zákonem stanovenou pro evidenci pobytu hostů.
</div>
""",
        "souhlas_label": "Souhlasím se zpracováním osobních údajů podle výše uvedeného textu.",
        "odeslat": "ODESLAT ZÁZNAM",
        "dekujeme": "✅ Děkujeme! Vaše údaje byly uloženy.",
        "err_datum": "Odjezd musí být po příjezdu.",
        "err_telefon": "Vyplňte telefon.",
        "err_email": "Vyplňte platný email.",
        "err_narozeni_1": "Špatný formát data narození 1. osoby.",
        "err_narozeni_2": "Špatný formát data narození 2. osoby.",
        "err_doklad_1": "Vyplňte doklad 1. osoby.",
        "err_doklad_2": "Vyplňte doklad 2. osoby.",
        "err_pole": "Vyplňte všechna povinná pole.",
        "err_souhlas": "Souhlas je povinný.",
        "err_sheets": "Chyba připojení k Google Sheets.",
        "err_ukladani": "Chyba ukládání: ",
        "lang_button": "🇬🇧 English",
        "povinne": "* povinné pole",
    },
    "en": {
        "page_title": "Guest Book",
        "app_title": "Guest Book",
        "intro": """
<div style="padding:15px; background-color:#f8f9fa; border-radius:12px;">
<p>Please fill in this guest book.</p>
<p>By completing this form, you help us fulfil our legal obligations regarding the registration of guests and the payment of the local tourist tax.</p>
<p>Your data is stored in accordance with applicable legal regulations and is used solely for the purpose of recording your stay.</p>
<p><b>Apartmán Tyršova, Tyršova 1239/1, 669 02 Znojmo</b></p>
</div>
""",
        "pocet_osob": "Number of guests *",
        "prichod": "Check-in *",
        "odjezd": "Check-out *",
        "telefon": "Phone *",
        "email": "Email *",
        "osoba_1": "### Guest 1",
        "osoba_2": "### Guest 2",
        "jmeno": "Full name *",
        "jmeno_2": "Full name (Guest 2) *",
        "narozeni": "Date of birth *",
        "narozeni_2": "Date of birth (Guest 2) *",
        "adresa": "Address *",
        "adresa_2": "Address (Guest 2) *",
        "doklad": "ID / Passport *",
        "doklad_2": "ID / Passport (Guest 2) *",
        "ph_jmeno": "John Smith",
        "ph_jmeno_2": "Jane Smith",
        "ph_narozeni": "15. 6. 1985",
        "ph_adresa": "Main St 123, London",
        "ph_doklad": "123456789 (Passport)",
        "ph_telefon": "+44 7700 123 456",
        "ph_email": "john@example.com",
        "gdpr_text": """
<div style="padding:10px; background-color:#f1f1f1; border-radius:8px; font-size:14px;">
<b>I consent to the processing of my personal data</b> (name, surname, address, date of birth, and stay details) 
for the purpose of guest registration at Apartmán Tyršova, in accordance with GDPR Regulation (EU) 2016/679. 
Consent is given voluntarily and may be withdrawn at any time. 
The data will be retained for the period required by law for guest registration records.
</div>
""",
        "souhlas_label": "I consent to the processing of my personal data as described above.",
        "odeslat": "SUBMIT",
        "dekujeme": "✅ Thank you! Your details have been saved.",
        "err_datum": "Check-out must be after check-in.",
        "err_telefon": "Please enter your phone number.",
        "err_email": "Please enter a valid email address.",
        "err_narozeni_1": "Invalid date of birth format for Guest 1.",
        "err_narozeni_2": "Invalid date of birth format for Guest 2.",
        "err_doklad_1": "Please enter the ID / Passport number for Guest 1.",
        "err_doklad_2": "Please enter the ID / Passport number for Guest 2.",
        "err_pole": "Please fill in all required fields.",
        "err_souhlas": "Consent is required.",
        "err_sheets": "Error connecting to Google Sheets.",
        "err_ukladani": "Save error: ",
        "lang_button": "🇨🇿 Česky",
        "povinne": "* required field",
    }
}

# --- Inicializace jazyka ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'cs'

# --- Přepínač jazyka ---
col_lang = st.columns([5, 1])
with col_lang[1]:
    current_lang = st.session_state.lang
    other_lang = 'en' if current_lang == 'cs' else 'cs'
    if st.button(TRANSLATIONS[current_lang]["lang_button"]):
        st.session_state.lang = other_lang
        st.rerun()

T = TRANSLATIONS[st.session_state.lang]

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
    st.success(T["dekujeme"])
    st.stop()

# --- Nadpis ---
st.markdown(f"<h1 style='text-align:center; color:#1a1a1a;'>{T['app_title']}</h1>", unsafe_allow_html=True)

# --- Úvodní text ---
st.markdown(T["intro"], unsafe_allow_html=True)

st.markdown("---")
st.markdown(f"<p style='color:#888; font-size:13px;'>{T['povinne']}</p>", unsafe_allow_html=True)

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
pocet_osob = st.selectbox(T["pocet_osob"], [1, 2], index=0 if st.session_state.form_data['pocet_osob']==1 else 1)

with st.form("checkin", clear_on_submit=False):
    # --- Datum příjezdu a odjezdu ---
    col1, col2 = st.columns(2)
    with col1:
        prichod = st.date_input(T["prichod"], st.session_state.form_data['prichod'], key="prichod")
    with col2:
        odjezd = st.date_input(T["odjezd"], st.session_state.form_data['odjezd'], key="odjezd")

    # --- Kontakt ---
    col1, col2 = st.columns(2)
    with col1:
        telefon = st.text_input(T["telefon"], st.session_state.form_data['telefon'], placeholder=T["ph_telefon"], key="telefon")
    with col2:
        email = st.text_input(T["email"], st.session_state.form_data['email'], placeholder=T["ph_email"], key="email")

    st.markdown("---")

    # --- 1. Osoba ---
    st.markdown(T["osoba_1"])
    col1, col2 = st.columns(2)
    with col1:
        j1 = st.text_input(T["jmeno"], st.session_state.form_data['j1'], placeholder=T["ph_jmeno"], key="j1_input")
        n1 = st.text_input(T["narozeni"], st.session_state.form_data['n1'], placeholder=T["ph_narozeni"], key="n1_input")
    with col2:
        a1 = st.text_input(T["adresa"], st.session_state.form_data['a1'], placeholder=T["ph_adresa"], key="a1_input")
        d1 = st.text_input(T["doklad"], st.session_state.form_data['d1'], placeholder=T["ph_doklad"], key="d1_input")

    # --- 2. Osoba ---
    if pocet_osob == 2:
        st.markdown(T["osoba_2"])
        col1, col2 = st.columns(2)
        with col1:
            j2 = st.text_input(T["jmeno_2"], st.session_state.form_data['j2'], placeholder=T["ph_jmeno_2"], key="j2_input")
            n2 = st.text_input(T["narozeni_2"], st.session_state.form_data['n2'], placeholder=T["ph_narozeni"], key="n2_input")
        with col2:
            a2 = st.text_input(T["adresa_2"], st.session_state.form_data['a2'], placeholder=T["ph_adresa"], key="a2_input")
            d2 = st.text_input(T["doklad_2"], st.session_state.form_data['d2'], placeholder=T["ph_doklad"], key="d2_input")
    else:
        j2 = n2 = a2 = d2 = ""

    st.markdown("---")

    # --- Souhlas s osobními údaji ---
    st.markdown(T["gdpr_text"], unsafe_allow_html=True)

    souhlas = st.checkbox(T["souhlas_label"], value=st.session_state.form_data['souhlas'], key="souhlas")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Odeslat tlačítko ---
    submitted = st.form_submit_button(
        T["odeslat"],
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
        if prichod >= odjezd: errors.append(T["err_datum"])
        if not telefon.strip(): errors.append(T["err_telefon"])
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email.strip()): errors.append(T["err_email"])
        def valid_narozeni(n): return bool(re.match(r"^\s*\d{1,2}\.\s*\d{1,2}\.\s*\d{4}\s*$", n))
        if not valid_narozeni(n1): errors.append(T["err_narozeni_1"])
        if pocet_osob==2 and not valid_narozeni(n2): errors.append(T["err_narozeni_2"])
        if not d1.strip(): errors.append(T["err_doklad_1"])
        if pocet_osob==2 and not d2.strip(): errors.append(T["err_doklad_2"])
        required = [j1, n1, a1, email]
        if pocet_osob==2: required += [j2, n2, a2]
        if not all(field.strip() for field in required): errors.append(T["err_pole"])
        if not souhlas: errors.append(T["err_souhlas"])

        if errors:
            for e in errors: st.error(e)
            st.stop()

        o2_data = {"jmeno": j2, "narozeni": n2, "adresa": a2, "doklad": d2} if pocet_osob==2 else {}
        row = [
            prichod.strftime("%d.%m.%Y"), odjezd.strftime("%d.%m.%Y"), pocet_osob,
            j1.strip(), n1.strip(), a1.strip(), d1.strip(),
            o2_data.get("jmeno", ""), o2_data.get("narozeni", ""),
            o2_data.get("adresa", ""), o2_data.get("doklad", ""),
            telefon.strip(), email.strip(), datetime.now().strftime("%d.%m.%Y %H:%M"),
            st.session_state.lang.upper()  # uložení jazyka do sheetu
        ]

        if sheet:
            try:
                sheet.append_row(row)
                st.session_state.odeslano = True
                st.rerun()
            except Exception as e:
                st.error(f"{T['err_ukladani']}{e}")
        else:
            st.error(T["err_sheets"])
