from flask import Flask, render_template, request, redirect, url_for, flash
import csv
from datetime import datetime
import os
import re

app = Flask(__name__)
app.secret_key = 'apartman_tyrsova_tajne'

CSV_FILE = 'data/hoste.csv'

os.makedirs('data', exist_ok=True)

# Hlavička
HEADER = [
    'Čas odeslání', 'Počet osob',
    'Jméno 1', 'Doklad 1', 'Adresa 1', 'Narození 1',
    'Jméno 2', 'Doklad 2', 'Adresa 2', 'Narození 2',
    'Email', 'Telefon', 'Příjezd', 'Odjezd'
]

# Zajistí, že CSV má hlavičku – i když už existuje
def zajisti_hlavicku():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(HEADER)
    else:
        with open(CSV_FILE, 'r', newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            try:
                first_row = next(reader)
                if first_row != HEADER:
                    # Soubor existuje, ale nemá správnou hlavičku → přidáme ji
                    temp_file = CSV_FILE + '.tmp'
                    with open(temp_file, 'w', newline='', encoding='utf-8-sig') as tf:
                        writer = csv.writer(tf, delimiter=';')
                        writer.writerow(HEADER)
                        writer.writerow(first_row)
                        for row in reader:
                            writer.writerow(row)
                    os.replace(temp_file, CSV_FILE)
            except StopIteration:
                # Soubor je prázdný → přidáme hlavičku
                with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f, delimiter=';')
                    writer.writerow(HEADER)

# Spustí se při startu
zajisti_hlavicku()

@app.route('/')
def index():
    return render_template('formular.html', data={})

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

    def datum_z_kalendare(d):
        dt = datetime.strptime(d, '%Y-%m-%d')
        return f"{dt.day}. {dt.month}. {dt.year}"

    cas = datetime.now().strftime('%d.%m.%Y %H:%M')
    prijezd_fmt = datum_z_kalendare(prijezd)
    odjezd_fmt = datum_z_kalendare(odjezd)

    # Uložení – bez hlavičky
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

if __name__ == '__main__':
    app.run(debug=True)