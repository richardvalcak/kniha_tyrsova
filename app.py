# app.py – Ubytovací kniha Apartmán Tyršova | VERZE 2.5 | © 2025
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import re
import hashlib
from xml.etree import ElementTree as ET
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import qrcode

# === KONFIGURACE ===
st.set_page_config(page_title="Apartmán Tyršova – Kniha hostů", layout="centered")

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "hoste.csv")
os.makedirs(DATA_DIR, exist_ok=True)

# ZMĚŇ SI HESLO!
MAJITEL_HESLO_HASH = "d2f7b3e8c1a9f4e6d8b7c5a3e1f9d7b5c3a1e9f7d5b3c1a9e7f5d3b1c9a7e5f3"  # hash("Znojmo2025!")

COLUMNS = [
    "Příjezd", "Odjezd", "Počet osob",
    "Jméno 1", "Narození 1", "Stát 1", "Účel 1", "Adresa 1", "Doklad 1",
    "Jméno 2", "Narození 2", "Stát 2", "Účel 2", "Adresa 2", "Doklad 2",
    "Telefon", "Email", "Zapsáno"
]

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=COLUMNS).to_csv(DATA_FILE, index=False, encoding='utf-8')

# === FUNKCE ===
def check_password(pwd: str) -> bool:
    return hashlib.sha256(pwd.encode()).hexdigest() == MAJITEL_HESLO_HASH

def format_date(text: str) -> str:
    if not text or not text.strip(): return ""
    parts = [p.strip() for p in re.split(r'[.\\/]', text)]
    if len(parts) != 3: return text.strip()
    try:
        d, m, y = map(int, parts)
        return f"{d}. {m}. {y}"
    except:
        return text.strip()

def valid_date(text: str) -> bool:
    if not text.strip(): return False
    if not re.match(r'^\d{1,2}\s*\.\s*\d{1,2}\s*\.\s*\d{4}$', text.strip()): return False
    try:
        d, m, y = map(int, [x.strip() for x in text.split('.')])
        datetime(y, m, d)
        return True
    except:
        return False

def valid_email(email: str) -> bool:
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email.strip()))

def valid_phone(phone: str) -> bool:
    return bool(re.match(r"^\+?\d{3,15}$", re.sub(r"\s+", "", phone)))

@st.cache_data
def load_data() -> pd.DataFrame:
    try:
        return pd.read_csv(DATA_FILE, encoding='utf-8')
    except:
        return pd.DataFrame(columns=COLUMNS)

def save_data(df: pd.DataFrame):
    df.to_csv(DATA_FILE, index=False, encoding='utf-8')

# === EXPORTY ===
def generate_xml(df: pd.DataFrame) -> bytes:
    root = ET.Element("UbytovaciKniha")
    for _, row in df.iterrows():
        host = ET.SubElement(root, "Host")
        ET.SubElement(host, "Jmeno").text = row["Jméno 1"]
        ET.SubElement(host, "DatumNarozeni").text = row["Narození 1"]
        ET.SubElement(host, "StatniPrislusnost").text = row["Stát 1"]
        ET.SubElement(host, "CisloDokladu").text = row["Doklad 1"]
        ET.SubElement(host, "Adresa").text = row["Adresa 1"]
        ET.SubElement(host, "UcelPobytu").text = row["Účel 1"]
        ET.SubElement(host, "DatumPrijezdu").text = row["Příjezd"]
        ET.SubElement(host, "DatumOdjezdu").text = row["Odjezd"]
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)

def generate_pdf(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=40)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("<b>Apartmán Tyršova – Kniha hostů</b>", styles['Title']))
    elements.append(Paragraph("Tyršova 1239/1, 669 02 Znojmo", styles['Normal']))
    elements.append(Paragraph(f"Datum tisku: {datetime.now().strftime('%d. %m. %Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 12))
    data = [COLUMNS] + [[str(row[col]) if pd.notna(row[col]) else "" for col in COLUMNS] for _, row in df.iterrows()]
    table = Table(data, colWidths=[55]*len(COLUMNS))
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)
    doc.build(elements)
    return buffer.getvalue()

def generate_qr() -> bytes:
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data('https://kniha-tyrsova-znojmo.streamlit.app')
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

# === DESIGN ===
st.markdown("""
<style>
    .big { font-size: 32px !important; font-weight: bold; text-align: center; }
    .small { font-size: 16px; text-align: center; color: #555; }
    .stButton > button {
        background-color: #28a745 !important; color: white !important;
        font-weight: bold !important; font-size: 18px !important;
        padding: 12px 24px !important; border-radius: 8px !important; width: 100% !important;
    }
    .stButton > button:hover { background-color: #218838 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big">Apartmán Tyršova – Kniha hostů</p>', unsafe_allow_html=True)
st.markdown('<p class="small">Tyršova 1239/1, 669 02 Znojmo</p>', unsafe_allow_html=True)
st.markdown("---")

# === POČET OSOB MIMO FORMULÁŘ (aby se stránka obnovila) ===
if 'pocet_osob' not in st.session_state:
    st.session_state.pocet_osob = 1

def update_pocet():
    st.session_state.pocet_osob = st.session_state.pocet_temp

st.selectbox(
    "Počet osob *",
    [1, 2],
    index=0 if st.session_state.pocet_osob == 1 else 1,
    key="pocet_temp",
    on_change=update_pocet,
    help="Po výběru 2 osob se objeví formulář pro druhou osobu."
)

pocet_osob = st.session_state.pocet_osob

# === VEŘEJNÝ FORMULÁŘ ===
with st.form("reg_form", clear_on_submit=True):
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        prichod = st.date_input("Příjezd *", value=datetime.today(), key="prichod")
    with col_date2:
        odjezd = st.date_input("Odjezd *", value=datetime.today(), key="odjezd")

    col_tel, col_mail = st.columns(2)
    with col_tel:
        telefon = st.text_input("Telefon *", placeholder="+420 777 123 456", key="tel")
    with col_mail:
        email = st.text_input("Email *", placeholder="jan@seznam.cz", key="email")

    st.markdown("---")
    st.subheader("1. Osoba")
    col1a, col1b = st.columns(2)
    with col1a:
        j1 = st.text_input("Jméno a příjmení *", placeholder="Jan Novák", key="j1")
        n1 = st.text_input("Narození * (15. 6. 1985)", placeholder="15. 6. 1985", key="n1")
        stat1 = st.selectbox("Stát *", ["Česko", "Slovensko", "Německo", "Rakousko", "Polsko", "Ukrajina", "Rusko", "USA", "Jiná"], key="stat1_osoba")
    with col1b:
        a1 = st.text_input("Adresa *", placeholder="Hlavní 123, Brno", key="a1")
        d1 = st.text_input("Doklad *", placeholder="123456789", key="d1")
        ucel1 = st.selectbox("Účel *", ["turismus", "zaměstnání", "studium", "rodinné důvody", "jiný"], key="ucel1_osoba")

    o2_data = {}
    if pocet_osob == 2:
        st.markdown("---")
        st.subheader("2. Osoba")
        col2a, col2b = st.columns(2)
        with col2a:
            j2 = st.text_input("Jméno *", key="j2")
            n2 = st.text_input("Narození *", key="n2")
            stat2 = st.selectbox("Stát *", ["Česko", "Slovensko", "Německo", "Rakousko", "Polsko", "Ukrajina", "Rusko", "USA", "Jiná"], key="stat2_osoba")
        with col2b:
            a2 = st.text_input("Adresa *", key="a2")
            d2 = st.text_input("Doklad *", key="d2")
            ucel2 = st.selectbox("Účel *", ["turismus", "zaměstnání", "studium", "rodinné důvody", "jiný"], key="ucel2_osoba")
        o2_data = {"jmeno": j2, "narozeni": n2, "stat": stat2, "ucel": ucel2, "adresa": a2, "doklad": d2}

    st.markdown("---")
    st.markdown("**Souhlasím se zpracováním osobních údajů dle GDPR a zákona č. 326/1999 Sb.**")
    souhlas = st.checkbox("**Souhlasím**", value=False, key="souhlas")

    submitted = st.form_submit_button("ODESLAT")
    if submitted:
        errors = []
        if prichod >= odjezd: errors.append("Odjezd musí být po příjezdu.")
        if not all([j1, n1, a1, d1, telefon, email]): errors.append("Vyplňte vše u 1. osoby.")
        if not valid_date(format_date(n1)): errors.append("Špatné datum narození 1.")
        if not valid_email(email): errors.append("Neplatný email.")
        if not valid_phone(telefon): errors.append("Neplatný telefon.")
        if pocet_osob == 2 and not all(o2_data.values()): errors.append("Vyplňte vše u 2. osoby.")
        if pocet_osob == 2 and not valid_date(format_date(o2_data["narozeni"])): errors.append("Špatné datum narození 2.")
        if not souhlas: errors.append("Souhlas je povinný.")

        if errors:
            for e in errors: st.error(e)
        else:
            df = load_data()
            new_row = {
                "Příjezd": prichod.strftime("%d. %m. %Y"), "Odjezd": odjezd.strftime("%d. %m. %Y"),
                "Počet osob": pocet_osob, "Jméno 1": j1.strip(), "Narození 1": format_date(n1),
                "Stát 1": stat1, "Účel 1": ucel1, "Adresa 1": a1.strip(), "Doklad 1": d1.strip(),
                "Jméno 2": o2_data.get("jmeno", "").strip(), "Narození 2": format_date(o2_data.get("narozeni", "")),
                "Stát 2": o2_data.get("stat", ""), "Účel 2": o2_data.get("ucel", ""),
                "Adresa 2": o2_data.get("adresa", "").strip(), "Doklad 2": o2_data.get("doklad", "").strip(),
                "Telefon": telefon.strip(), "Email": email.strip(),
                "Zapsáno": datetime.now().strftime("%d. %m. %Y %H:%M")
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("Hosté zaregistrováni!")
            st.balloons()

# === SKRYTÝ ADMIN ===
query_params = st.query_params
admin_pass = query_params.get("admin")

if admin_pass and check_password(admin_pass):
    st.markdown("## Správa dat")
    st.success("Přístup povolen")
    df = load_data()
    if not df.empty:
        df_disp = df.copy()
        df_disp.insert(0, "ID", range(1, len(df_disp)+1))
        st.dataframe(df_disp, use_container_width=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.download_button("CSV", df.to_csv(index=False, encoding='utf-8').encode(), f"hoste_{datetime.now():%Y%m%d}.csv", "text/csv")
        with c2: st.download_button("XML", generate_xml(df), "eturista.xml", "application/xml")
        with c3: st.download_button("PDF", generate_pdf(df), "kniha.pdf", "application/pdf")
        id_del = st.selectbox("ID:", df_disp["ID"], key="id_del")
        if st.button("Smazat", key="smazat"):
            df = df.drop(df_disp[df_disp["ID"] == id_del].index).reset_index(drop=True)
            save_data(df)
            st.success("Smazáno!")
            st.rerun()
        if st.button("Smazat VŠE"):
            if st.checkbox("Opravdu?", key="smazat_vse"):
                pd.DataFrame(columns=COLUMNS).to_csv(DATA_FILE, index=False)
                st.success("Vše smazáno!")
                st.rerun()
    else:
        st.info("Žádní hosté.")
    st.image(generate_qr(), caption="QR pro check-in")
    if st.button("Odhlásit"):
        st.query_params.clear()
        st.rerun()

st.markdown("---")
st.markdown("""
<p style="text-align:center; color:#777; font-size:14px;">
    Evidence ubytování dle zákona č. 326/1999 Sb.<br>
    Kontakt: +420 XXX XXX XXX
</p>
""", unsafe_allow_html=True)
