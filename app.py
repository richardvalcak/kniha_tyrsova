# app.py – Ubytovací kniha Apartmán Tyršova | VERZE 2.0 | © 2025
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

# Tajné heslo (SHA-256 hash) – ZMĚŇ SI HO!
MAJITEL_HESLO_HASH = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6"  # hash("Tyrsova2025!")

# Sloupce v CSV
COLUMNS = [
    "Příjezd", "Odjezd", "Počet osob",
    "Jméno 1", "Narození 1", "Stát 1", "Účel 1", "Adresa 1", "Doklad 1",
    "Jméno 2", "Narození 2", "Stát 2", "Účel 2", "Adresa 2", "Doklad 2",
    "Telefon", "Email", "Zapsáno"
]

# Inicializace CSV
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=COLUMNS).to_csv(DATA_FILE, index=False, encoding='utf-8')

# === POMOCNÉ FUNKCE ===
def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

def check_password(pwd: str) -> bool:
    return hash_password(pwd) == MAJITEL_HESLO_HASH

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
        return 1900 <= y <= 2100 and 1 <= m <= 12 and 1 <= d <= 31
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

# === XML EXPORT PRO eTurista ===
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

# === PDF EXPORT ===
def generate_pdf(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=40)
    styles = getSampleStyleSheet()
    elements = []

    # Hlavička
    elements.append(Paragraph("<b>Apartmán Tyršova</b>", styles['Title']))
    elements.append(Paragraph("Tyršova 1239/1, 669 02 Znojmo", styles['Normal']))
    elements.append(Paragraph(f"Vygenerováno: {datetime.now().strftime('%d. %m. %Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Tabulka
    data = [COLUMNS]
    for _, row in df.iterrows():
        data.append([str(row[col]) if pd.notna(row[col]) else "" for col in COLUMNS])
    
    table = Table(data, colWidths=[60]*len(COLUMNS))
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

# === QR KÓD ===
def generate_qr() -> bytes:
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(st.session_state.get('page_url', 'https://kniha-tyrsova-znojmo.streamlit.app'))
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
    .delete-btn { background-color: #dc3545 !important; }
    .delete-btn:hover { background-color: #c82333 !important; }
    .admin-trigger { font-size: 12px; color: #ccc; text-align: right; margin-top: 20px; }
    .admin-input { width: 200px; opacity: 0.5; font-size: 12px; color: #999; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big">Apartmán Tyršova – Kniha hostů</p>', unsafe_allow_html=True)
st.markdown('<p class="small">Tyršova 1239/1, 669 02 Znojmo</p>', unsafe_allow_html=True)
st.markdown("---")

# === VEŘEJNÝ FORMULÁŘ ===
with st.form("reg_form", clear_on_submit=True):
    st.markdown("**Vyberte počet ubytovaných osob:**")
    pocet_osob = st.selectbox("Počet osob *", [1, 2], index=0, key="pocet")

    st.markdown("**Datum příjezdu a odjezdu:**")
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        prichod = st.date_input("Příjezd *", value=datetime.today(), key="prichod")
    with col_date2:
        odjezd = st.date_input("Odjezd *", value=datetime.today(), key="odjezd")

    st.markdown("**Kontaktní údaje:**")
    col_tel, col_mail = st.columns(2)
    with col_tel:
        telefon = st.text_input("Telefon *", placeholder="+420 777 123 456", key="tel")
    with col_mail:
        email = st.text_input("Email *", placeholder="jan@seznam.cz", key="mail")

    st.markdown("---")
    st.subheader("1. Osoba (hlavní host)")
    col1a, col1b = st.columns(2)
    with col1a:
        j1 = st.text_input("Jméno a příjmení *", placeholder="Jan Novák", key="j1")
        n1 = st.text_input("Datum narození * (15. 6. 1985)", placeholder="15. 6. 1985", key="n1")
        stat1 = st.selectbox("Státní občanství *", [
            "Česko", "Slovensko", "Německo", "Rakousko", "Polsko",
            "Ukrajina", "Rusko", "USA", "Velká Británie", "Jiná"
        ], key="stat1")
    with col1b:
        a1 = st.text_input("Adresa bydliště *", placeholder="Hlavní 123, Brno", key="a1")
        d1 = st.text_input("Číslo dokladu *", placeholder="123456789", key="d1")
        ucel1 = st.selectbox("Účel pobytu *", [
            "turismus", "zaměstnání", "studium", "rodinné důvody", "jiný"
        ], key="ucel1")

    o2_data = {}
    if pocet_osob == 2:
        st.markdown("---")
        st.subheader("2. Osoba")
        col2a, col2b = st.columns(2)
        with col2a:
            j2 = st.text_input("Jméno a příjmení *", key="j2")
            n2 = st.text_input("Datum narození *", key="n2")
            stat2 = st.selectbox("Státní občanství *", [
                "Česko", "Slovensko", "Německo", "Rakousko", "Polsko",
                "Ukrajina", "Rusko", "USA", "Velká Británie", "Jiná"
            ], key="stat2")
        with col2b:
            a2 = st.text_input("Adresa bydliště *", key="a2")
            d2 = st.text_input("Číslo dokladu *", key="d2")
            ucel2 = st.selectbox("Účel pobytu *", [
                "turismus", "zaměstnání", "studium", "rodinné důvody", "jiný"
            ], key="ucel2")
        o2_data = {"jmeno": j2, "narozeni": n2, "stat": stat2, "ucel": ucel2, "adresa": a2, "doklad": d2}

    st.markdown("---")
    st.markdown("""
    **Souhlas se zpracováním osobních údajů:**  
    Souhlasím se zpracováním osobních údajů pro účely evidence ubytování dle zákona č. 326/1999 Sb. a GDPR.
    """)
    souhlas = st.checkbox("**Souhlasím**", key="souhlas")

    submitted = st.form_submit_button("ODESLAT ZÁZNAM")
    if submitted:
        errors = []
        if prichod >= odjezd:
            errors.append("Odjezd musí být po příjezdu.")
        if not all([j1, n1, a1, d1, telefon, email]):
            errors.append("Vyplňte všechny povinné údaje 1. osoby.")
        if not valid_date(format_date(n1)):
            errors.append("Neplatné datum narození 1. osoby.")
        if not valid_email(email):
            errors.append("Neplatný email.")
        if not valid_phone(telefon):
            errors.append("Neplatný telefon.")
        if pocet_osob == 2 and not all(o2_data.values()):
            errors.append("Vyplňte všechny údaje 2. osoby.")
        if pocet_osob == 2 and not valid_date(format_date(o2_data["narozeni"])):
            errors.append("Neplatné datum narození 2. osoby.")
        if not souhlas:
            errors.append("Musíte souhlasit se zpracováním údajů.")

        if errors:
            for e in errors: st.error(e)
        else:
            df = load_data()
            new_row = {
                "Příjezd": prichod.strftime("%d. %m. %Y"),
                "Odjezd": odjezd.strftime("%d. %m. %Y"),
                "Počet osob": pocet_osob,
                "Jméno 1": j1.strip(),
                "Narození 1": format_date(n1),
                "Stát 1": stat1,
                "Účel 1": ucel1,
                "Adresa 1": a1.strip(),
                "Doklad 1": d1.strip(),
                "Jméno 2": o2_data.get("jmeno", "").strip(),
                "Narození 2": format_date(o2_data.get("narozeni", "")),
                "Stát 2": o2_data.get("stat", ""),
                "Účel 2": o2_data.get("ucel", ""),
                "Adresa 2": o2_data.get("adresa", "").strip(),
                "Doklad 2": o2_data.get("doklad", "").strip(),
                "Telefon": telefon.strip(),
                "Email": email.strip(),
                "Zapsáno": datetime.now().strftime("%d. %m. %Y %H:%M")
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("Hosté úspěšně zaregistrováni!")
            st.balloons()

# === SKRYTÝ ADMIN PANEL ===
st.markdown("---")
st.markdown('<p class="admin-trigger">Verze 2.0</p>', unsafe_allow_html=True)
admin_input = st.text_input("", placeholder="Tajný kód...", key="admin", type="password", help="Pro majitele")

if admin_input and check_password(admin_input):
    st.markdown("## Správa dat (majitel)")
    df = load_data()
    if not df.empty:
        df_display = df.copy()
        df_display.insert(0, "ID", range(1, len(df_display) + 1))
        st.dataframe(df_display, use_container_width=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            csv = df.to_csv(index=False, encoding='utf-8').encode()
            st.download_button("CSV", csv, f"hoste_{datetime.now():%Y%m%d}.csv", "text/csv")
        with col2:
            xml = generate_xml(df)
            st.download_button("XML (eTurista)", xml, "eturista.xml", "application/xml")
        with col3:
            pdf = generate_pdf(df)
            st.download_button("PDF (tisk)", pdf, "kniha_hostu.pdf", "application/pdf")

        st.markdown("### Smazat záznam")
        id_del = st.selectbox("ID k odstranění:", df_display["ID"])
        if st.button("Smazat", key="del"):
            idx = df_display[df_display["ID"] == id_del].index[0]
            df = df.drop(idx).reset_index(drop=True)
            save_data(df)
            st.success("Záznam smazán!")
            st.rerun()

        if st.button("Smazat VŠE"):
            if st.checkbox("Opravdu smazat vše?"):
                pd.DataFrame(columns=COLUMNS).to_csv(DATA_FILE, index=False)
                st.success("Vše smazáno!")
                st.rerun()
    else:
        st.info("Žádní hosté.")

    st.markdown("### QR kód pro rychlý přístup")
    qr_img = generate_qr()
    st.image(qr_img, caption="Naskenuj pro check-in")

# === FOOTER ===
st.markdown("""
<p style="text-align:center; color:#777; font-size:14px;">
    Evidence ubytování dle zákona č. 326/1999 Sb.<br>
    Kontakt: +420 XXX XXX XXX | apartman@tyrsova.cz
</p>
""", unsafe_allow_html=True)
