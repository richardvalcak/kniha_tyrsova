# app.py – Kniha hostů Apartmán Tyršova | SKRYTÝ ADMIN PŘES ?secret=tajny_kod
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import re

# === TAJNÝ KÓD PRO URL (ZMĚŇ SI HO!) + HESLO ===
TAJNY_KOD = "tyrsova2025"  # ← ZMĚŇ NA SVŮJ! (pro URL ?secret=TEN_TO)
MAJITEL_HESLO = "MujHeslo123!"  # ← ZMĚŇ NA SVŮJ!

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
st.set_page_config(page_title="Apartmán Tyršova – Kniha hostů", layout="centered")

st.markdown("""
<style>
    .big { font-size: 32px !important; font-weight: bold; text-align: center; }
    .small { font-size: 16px; text-align: center; color: #555; }
    .stButton > button {
        background-color: #28a745 !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 18px !important;
        padding: 12px 24px !important;
        border-radius: 8px !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background-color: #218838 !important;
    }
    .delete-btn {
        background-color: #dc3545 !important;
        color: white !important;
    }
    .delete-btn:hover {
        background-color: #c82333 !important;
    }
</style>
""", unsafe_allow_html=True)

# === ZJIŠTĚNÍ ADMIN REŽIMU (PŘES ?secret=tajny_kod) ===
is_admin = st.query_params.get("secret", [None])[0] == TAJNY_KOD

# === ADMIN PANEL (SKRYTÝ – JEN PŘES TAJNÚ URL) ===
if is_admin:
    st.title("🔒 Majitel – Správa dat")
    st.markdown("**Pouze pro majitele – zadat heslo pro přístup**")
    
    heslo = st.text_input("Zadej heslo majitele:", type="password", key="heslo_input")
    
    if heslo == MAJITEL_HESLO:
        st.success("✅ Přístup povolen!")
        try:
            df = pd.read_csv(DATA_FILE)
            if not df.empty:
                # Tabulka s ID pro mazání
                df_display = df.copy()
                df_display.insert(0, "ID", range(1, len(df_display) + 1))
                st.subheader("Všechny záznamy")
                st.dataframe(df_display, use_container_width=True)

                # Stahování CSV
                st.subheader("Stáhnout data")
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Stáhnout CSV pro úřad",
                    csv,
                    f"hoste_tyrsova_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )

                # Mazání záznamů
                st.subheader("Smazat záznam")
                id_to_delete = st.selectbox("Vyber ID k odstranění:", df_display["ID"].tolist(), key="delete_select")
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button("Smazat vybraný záznam", key="delete_btn"):
                        idx = df_display[df_display["ID"] == id_to_delete].index[0]
                        df = df.drop(idx).reset_index(drop=True)
                        df.to_csv(DATA_FILE, index=False)
                        st.success(f"✅ Záznam ID {id_to_delete} smazán!")
                        st.rerun()
                with col2:
                    if st.button("Smazat VŠE", key="delete_all"):
                        if st.checkbox("Opravdu smazat VŠE?", key="confirm_all"):
                            pd.DataFrame(columns=df.columns).to_csv(DATA_FILE, index=False)
                            st.success("✅ Všechny záznamy smazány!")
                            st.rerun()

            else:
                st.info("ℹ️ Zatím žádní hosté.")
        except Exception as e:
            st.error(f"❌ Chyba při načítání dat: {e}")
    elif heslo:
        st.error("❌ Špatné heslo! Zkus to znovu.")
    else:
        st.info("🔒 Zadej heslo pro přístup k datům.")

    st.markdown("---")
    st.markdown("**Zpět na formulář pro hosty:**")
    if st.button("Přejít na hlavní stránku"):
        st.query_params.clear()
        st.rerun()

# === VEŘEJNÝ FORMULÁŘ (JEN PRO HOSTY) ===
else:
    st.markdown('<p class="big">Apartmán Tyršova – Kniha hostů</p>', unsafe_allow_html=True)
    st.markdown('<p class="small">Tyršova 1239/1, 669 02 Znojmo</p>', unsafe_allow_html=True)
    st.markdown("---")

    with st.form("reg_form", clear_on_submit=False):
        st.markdown("**Vyberte počet ubytovaných osob:**")
        pocet_osob = st.selectbox("Počet osob *", [1, 2], index=0, key="pocet_osob")

        st.markdown("**Vyplňte údaje o ubytování:**")
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            prichod = st.date_input("Datum příjezdu *", value=datetime.today(), key="prichod")
        with col_date2:
            odjezd = st.date_input("Datum odjezdu *", value=datetime.today(), key="odjezd")

        st.markdown("**Kontaktní údaje:**")
        col_tel, col_mail = st.columns(2)
        with col_tel:
            telefon = st.text_input("Telefon *", placeholder="+420 777 123 456", key="tel")
        with col_mail:
            email = st.text_input("Email *", placeholder="jan@seznam.cz", key="mail")

        st.markdown("---")
        st.subheader("1. Osoba")
        col1a, col1b = st.columns(2)
        with col1a:
            j1 = st.text_input("Jméno a příjmení *", key="j1", placeholder="Jan Novák")
            n1 = st.text_input("Datum narození *", key="n1", placeholder="15. 6. 1985")
        with col1b:
            a1 = st.text_input("Adresa bydliště *", key="a1", placeholder="Hlavní 123, Brno")
            d1 = st.text_input("Číslo dokladu *", key="d1", placeholder="123456789")

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

        st.markdown("---")
        st.markdown("""
        **Souhlas se zpracováním osobních údajů:**  
        Souhlasím se zpracováním mých osobních údajů (jméno, příjmení, adresa, datum narození a údaje o pobytu) pro účely evidence ubytování v Apartmánu Tyršova, v souladu se zákonem č. 101/2000 Sb., o ochraně osobních údajů, a nařízení GDPR (EU) 2016/679.  
        Souhlas je udělen dobrovolně a lze jej kdykoli odvolat. Tyto údaje budou uchovávány po dobu zákonem stanovenou pro evidenci pobytu hostů.
        """)
        souhlas = st.checkbox("**Souhlasím se zpracováním osobních údajů podle výše uvedeného textu**", key="souhlas")

        submitted = st.form_submit_button("ODESLAT")

        if submitted:
            o1 = {"jmeno": j1.strip(), "narozeni": n1.strip(), "adresa": a1.strip(), "doklad": d1.strip()}
            o2 = {"jmeno": j2.strip() if pocet_osob == 2 else "", "narozeni": n2.strip() if pocet_osob == 2 else "",
                  "adresa": a2.strip() if pocet_osob == 2 else "", "doklad": d2.strip() if pocet_osob == 2 else ""}

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
                save(prichod.strftime("%d.%m.%Y"), odjezd.strftime("%d.%m.%Y"), pocet_osob, o1, o2, telefon.strip(), email.strip())
                st.success("Hosté úspěšně zaregistrováni!")
                st.balloons()

    st.markdown("""
    <p style="text-align:center; color:#777; font-size:14px;">
        Apartmán Tyršova – evidence ubytování dle zákona č. 326/1999 Sb.<br>
        Kontakt: +420 XXX XXX XXX
    </p>
    """, unsafe_allow_html=True)
