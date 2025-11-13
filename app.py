from flask import Flask, render_template, request, redirect, url_for, flash, Response
import csv
from datetime import datetime
import os
import re

app = Flask(__name__)
app.secret_key = 'apartman_tyrsova_render_2025'  # Změň na své, pokud chceš

CSV_FILE = 'data/hoste.csv'
os.makedirs('data', exist_ok=True)

# Hlavička CSV
HEADER = [
    'Čas odeslání', 'Počet osob',
    'Jméno 1', 'Doklad 1', 'Adresa 1', 'Narození 1',
    'Jméno 2', 'Doklad 2', 'Adresa 2', 'Narození 2',
    'Email', 'Telefon', 'Příjezd', 'Odjezd'
]

# Zajistí správnou hlavičku
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
                    raise ValueError
        except (StopIteration, ValueError):
            temp_file = CSV_FILE + '.tmp'
            with open(temp_file, 'w', newline='', encoding='utf-8-sig') as tf:
                writer = csv.writer(tf, delimiter=';')
                writer.writerow(HEADER)
            os.replace(temp_file, CSV_FILE)

zajisti_hlavicku()

# === HLAVNÍ FORMULÁŘ ===
@app.route('/')
def index():
    return render_template('formular.html', data={})

# === ODESLÁNÍ FORMULÁŘE ===
@app.route('/odeslat', methods=['POST'])
def odeslat():
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

    # Povinná pole pro 1. osobu
    if not all([pocet, email, telefon, prijezd, odjezd, jmeno1, doklad1, adresa1, narozeni1]):
        chyby.append('Vyplň prosím všechna povinná pole pro 1. osobu!')

    # Povinná pole pro 2. osobu
    if pocet == '2' and not all([jmeno2, doklad2, adresa2, narozeni2]):
        chyby.append('Vyplň prosím všechna pole i pro 2. osobu!')

    # Datum odjezdu po příjezdu
    if odjezd <= prijezd:
        chyby.append('Datum odjezdu musí být po příjezdu!')

    # Validace formátu data narození
    def je_platne_datum(d):
        return bool(re.match(r'^\d{1,2}\.\s?\d{1,2}\.\s?\d{4}$', d))

    if not je_platne_datum(narozeni1):
        chyby.append('Datum narození 1. osoby: zadejte ve formátu 15. 6. 1985')

    if pocet == '2' and narozeni2 and not je_platne_datum(narozeni2):
        chyby.append('Datum narození 2. osoby: zadejte ve formátu 22. 9. 1988')

    # Zobraz chyby
    if chyby:
        for chyba in chyby:
            flash(chyba, 'error')
        return render_template('formular.html', data=request.form)

    # Formátování data z kalendáře
    def datum_z_kalendare(d):
        dt = datetime.strptime(d, '%Y-%m-%d')
        return f"{dt.day}. {dt.month}. {dt.year}"

    cas = datetime.now().strftime('%d.%m.%Y %H:%M')
    prijezd_fmt = datum_z_kalendare(prijezd)
    odjezd_fmt = datum_z_kalendare(odjezd)

    # Uložení do CSV
    with open(CSV_FILE, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow([
            cas, pocet,
            jmeno1, doklad1, adresa1, narozeni1,
            jmeno2, doklad2, adresa2, narozeni2,
            email, telefon, prijezd_fmt, odjezd_fmt
        ])

    return redirect(url_for('potvrzeni'))

# === POTVRZENÍ ===
@app.route('/potvrzeni')
def potvrzeni():
    return render_template('potvrzeni.html')

# === ZOBRAZENÍ DAT + MAZÁNÍ ===
@app.route('/data')
def zobraz_data():
    if not os.path.exists(CSV_FILE):
        return "<h3>Žádná data – první host ještě nepřijel!</h3><a href='/'>← Zpět na formulář</a>"

    try:
        with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)
    except Exception as e:
        return f"<h3>Chyba při čtení souboru: {e}</h3><a href='/'>← Zpět</a>"

    if len(rows) <= 1:  # jen hlavička
        return "<h3>Žádná data.</h3><a href='/'>← Zpět na formulář</a>"

    html = """
    <style>
        body { font-family: system-ui, sans-serif; background: #f8fafc; padding: 20px; margin: 0; }
        h2 { color: #1f2937; text-align: center; margin-bottom: 10px; }
        .links { text-align: center; margin: 15px 0; }
        .links a { margin: 0 10px; color: #4f46e5; text-decoration: none; font-weight: 500; }
        table { width: 100%; max-width: 1200px; margin: 20px auto; border-collapse: collapse; background: white; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #4f46e5; color: white; font-weight: 600; }
        tr:nth-child(even) { background: #f9fafb; }
        tr:hover { background: #f3f4f6; }
        .delete-btn { background: #ef4444; color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 0.85rem; font-weight: 500; }
        .delete-btn:hover { background: #dc2626; }
        @media (max-width: 768px) { table, th, td { font-size: 0.8rem; } th, td { padding: 8px; } }
    </style>
    <h2>Seznam hostů (CSV data)</h2>
    <div class="links">
        <a href='/'>← Zpět na formulář</a> | 
        <a href='/stahnout-csv'>↓ Stáhnout CSV</a>
    </div>
    <table>
    """

    for i, row in enumerate(rows):
        if i == 0:  # hlavička
            html += "<tr>" + "".join(f"<th>{cell}</th>" for cell in row) + "<th>Akce</th></tr>"
            continue
        cas = row[0]
        html += "<tr>"
        for cell in row:
            html += f"<td>{cell}</td>"
        html += f"""
        <td style="text-align:center;">
            <form method="POST" action="/smazat" style="display:inline;" onsubmit="return confirm('Opravdu smazat tento záznam?');">
                <input type="hidden" name="cas" value="{cas}">
                <button type="submit" class="delete-btn">SMAZAT</button>
            </form>
        </td>
        """
        html += "</tr>"
    html += "</table>"
    return html

# === SMAZÁNÍ ŘÁDKU ===
@app.route('/smazat', methods=['POST'])
def smazat():
    cas_k_smazani = request.form.get('cas')
    if not cas_k_smazani:
        flash("Chyba: žádný řádek k odstranění!", 'error')
        return redirect('/data')

    if not os.path.exists(CSV_FILE):
        flash("Soubor neexistuje!", 'error')
        return redirect('/data')

    # Načti všechny řádky
    with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=';')
        rows = list(reader)

    # Najdi a smaž
    new_rows = [row for row in rows if row and row[0] != cas_k_smazani]

    if len(new_rows) == len(rows):
        flash("Řádek nenalezen!", 'error')
    else:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerows(new_rows)
        flash("Řádek úspěšně smazán!", 'success')

    return redirect('/data')

# === STÁHNUTÍ CSV ===
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

# === SPUŠTĚNÍ ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
