from flask import Flask, render_template, request, redirect, url_for, flash, Response
import csv
from datetime import datetime
import os
import re

app = Flask(__name__)
app.secret_key = 'apartman_tyrsova_render_2025'

CSV_FILE = 'data/hoste.csv'
os.makedirs('data', exist_ok=True)

# Hlavička CSV
HEADER = [
    'Čas odeslání', 'Počet osob',
    'Jméno 1', 'Doklad 1', 'Adresa 1', 'Narození 1',
    'Jméno 2', 'Doklad 2', 'Adresa 2', 'Narození 2',
    'Email', 'Telefon', 'Příjezd', 'Odjezd'
]

# Zajistí hlavičku (pokud soubor neexistuje nebo je poškozený)
def zajisti_hlavicku():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(HEADER)
    else:
        try:
            with open(CSV_FILE, 'r', newline='', encoding='utf-8-sig') as f:
                reader = csv.reader(f, delimiter=';')
                first_row = next(reader)
                if first_row != HEADER:
                    raise ValueError("Chybí hlavička")
        except (StopIteration, ValueError):
            # Přepíše soubor s hlavičkou
            temp_file = CSV_FILE + '.tmp'
            with open(temp_file, 'w', newline='', encoding='utf-8-sig') as tf:
                writer = csv.writer(tf, delimiter=';')
                writer.writerow(HEADER)
            os.replace(temp_file, CSV_FILE)

zajisti_hlavicku()

@app.route('/')
def index():
    return render_template('formular.html', data={})

@app.route('/odeslat', methods=['POST'])
def odeslat():
    # --- ZÍSKÁNÍ DAT Z FORMULÁŘE ---
    pocet = request.form.get('pocet_osob', '')
    email = request.form.get('email', '').strip()
    telefon = request.form.get('telefon', '').strip()
    prijezd = request.form.get('prijezd', '')
    odjezd = request.form.get('odjezd', '')

    jmeno1 = request.form.get('jmeno1', '').strip()
    doklad1 = request.form.get('doklad1', '').strip()
    adresa1 = request.form.get('adresa1', '').strip()
    narozeni1 = request.form.get('narozeni1', '').strip()

    jmeno2 = request.form.get('jmeno2', '').strip()
    doklad2 = request.form.get('doklad2', '').strip()
    adresa2 = request.form.get('adresa2', '').strip()
    narozeni2 = request.form.get('narozeni2', '').strip()

    chyby = []

    # --- VALIDACE ---
    if not all([pocet, email, telefon, prijezd, odjezd, jmeno1, doklad1, adresa1, narozeni1]):
        chyby.append('Vyplň prosím všechna povinná pole pro 1. osobu!')

    if pocet == '2' and not all([jmeno2, doklad2, adresa2, narozeni2]):
        chyby.append('Vyplň prosím všechna pole i pro 2. osobu!')

    if odjezd <= prijezd:
        chyby.append('Datum odjezdu musí být po příjezdu!')

    def je_platne_datum(d):
        return bool(re.match(r'^\d{1,2}\.\s?\d{1,2}\.\s?\d{4}$', d))

    if not je_platne_datum(narozeni1):
        chyby.append('Datum narození 1. osoby: zadejte ve formátu 15. 6. 1985')

    if pocet == '2' and narozeni2 and not je_platne_datum(narozeni2):
        chyby.append('Datum narození 2. osoby: zadejte ve formátu 22. 9. 1988')

    if chyby:
        for chyba in chyby:
            flash(chyba, 'error')
        return render_template('formular.html', data=request.form)

    # --- FORMÁTOVÁNÍ DAT ---
    def datum_z_kalendare(d):
        dt = datetime.strptime(d, '%Y-%m-%d')
        return f"{dt.day}. {dt.month}. {dt.year}"

    cas = datetime.now().strftime('%d.%m.%Y %H:%M')
    prijezd_fmt = datum_z_kalendare(prijezd)
    odjezd_fmt = datum_z_kalendare(odjezd)

    # --- ULOŽENÍ DO CSV ---
    with open(CSV_FILE, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow([
            cas, pocet,
            jmeno1, doklad1, adresa1, narozeni1,
            jmeno2, doklad2, adresa2, narozeni2,
            email, telefon, prijezd_fmt, odjezd_fmt
        ])

    return redirect(url_for('potvrzeni'))

@app.route('/potvrzeni')
def potvrzeni():
    return render_template('potvrzeni.html')

# === NOVÁ FUNKCE: ZOBRAZENÍ DAT V PROHLÍŽEČI ===
@app.route('/data')
def zobraz_data():
    if not os.path.exists(CSV_FILE):
        return "<h3>Žádná data – první host ještě nepřijel!</h3><a href='/'>← Zpět na formulář</a>"

    try:
        with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)
    except Exception as e:
        return f"<h3>Chyba při čtení souboru: {e}</h3>"

    if len(rows) == 0:
        return "<h3>Žádná data.</h3><a href='/'>← Zpět</a>"

    # HTML tabulka
    html = """
    <style>
        body { font-family: system-ui, sans-serif; background: #f8fafc; padding: 20px; }
        h2 { color: #1f2937; text-align: center; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; background: white; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        th, td { padding: 12px; text-align: left; border: 1px solid #ddd; }
        th { background: #4f46e5; color: white; }
        tr:nth-child(even) { background: #f9fafb; }
        a { display: inline-block; margin: 20px 0; color: #4f46e5; text-decoration: none; }
        @media (max-width: 600px) { table, th, td { font-size: 0.9rem; } }
    </style>
    <h2>Seznam hostů (CSV data)</h2>
    <a href='/'>← Zpět na formulář</a>
    <table>
    """
    for i, row in enumerate(rows):
        html += "<tr>"
        for cell in row:
            html += f"<td>{cell}</td>"
        html += "</tr>"
    html += "</table><a href='/'>← Zpět</a>"
    return html

# === VOLITELNĚ: STÁHNUTÍ CSV ===
@app.route('/stahnout-csv')
def stahnout_csv():
    if not os.path.exists(CSV_FILE):
        return "Žádná data k stažení!"
    
    with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    return Response(
        content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=hoste.csv'}
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
