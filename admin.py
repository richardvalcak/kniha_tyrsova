# admin.py – TAJNÁ STRÁNKA PRO MAJITELE
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# === TAJNÉ HESLO (ZMĚŇ SI HO!) ===
MAJITEL_HESLO = "Tyrsova2025"  # ← ZMĚŇ NA SVŮJ!

# === Nastavení ===
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "hoste.csv")

st.set_page_config(page_title="Majitel – Apartmán Tyršova", layout="centered")
st.title("Majitel – Správa dat")

heslo = st.text_input("Zadej heslo majitele:", type="password")

if heslo == MAJITEL_HESLO:
    st.success("Přístup povolen!")

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if not df.empty:
            df_display = df.copy()
            df_display.insert(0, "ID", range(1, len(df_display) + 1))
            st.dataframe(df_display, use_container_width=True)

            # Stahování
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Stáhnout CSV pro úřad",
                csv,
                f"hoste_tyrsova_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )

            # Mazání
            st.markdown("### Smazat záznam")
            id_to_delete = st.selectbox("Vyber ID:", df_display["ID"].tolist())
            if st.button("Smazat vybraný záznam"):
                idx = df_display[df_display["ID"] == id_to_delete].index[0]
                df = df.drop(idx).reset_index(drop=True)
                df.to_csv(DATA_FILE, index=False)
                st.success(f"Záznam {id_to_delete} smazán!")
                st.rerun()

            if st.button("Smazat VŠE"):
                if st.checkbox("Opravdu smazat všechny záznamy?"):
                    pd.DataFrame(columns=df.columns).to_csv(DATA_FILE, index=False)
                    st.success("Vše smazáno!")
                    st.rerun()
        else:
            st.info("Zatím žádní hosté.")
    else:
        st.info("Žádná data.")
else:
    st.error("Špatné heslo nebo přístup zamítnut.")

st.markdown("---")
st.markdown("**Zpět na formulář:** [Hlavní stránka](https://kniha-tyrsova-znojmo.streamlit.app)")
