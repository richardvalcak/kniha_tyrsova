from flask import Flask, render_template, request, redirect, url_for, flash, Response, session
import csv
from datetime import datetime
import os
import re

app = Flask(__name__)
app.secret_key = 'apartman_tyrsova_render_2025_ultra_secure'  # Silný klíč

CSV_FILE = 'data/hoste.csv'
os.makedirs('data', exist_ok=True)

# === HESLO ===
ADMIN_PASSWORD = 'tyrsova123'  # ← ZMĚŇ NA SVÉ! (např. 'MojeHeslo2025!')

# === HLAVIČKA CSV ===
HEADER = [
    'Čas odeslání', 'Počet osob',
    'Jméno 1', 'Doklad 1', 'Adresa 1', 'Narození 1',
    'Jméno 2', 'Doklad 2', 'Adresa 2', 'Narození 2',
    'Email', 'Telefon', 'Příjezd', 'Odjezd'
]

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

# === PŘIHLÁŠENÍ (pro /data a /smazat) ===
def je_prihlasen():
    return session.get('prihlasen') == True

def vyzaduj_prihlaseni(f):
    def wrapper(*args, **kwargs):
        if not je_prihlasen():
            return redirect(url_for('prihlaseni'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/prihlaseni', methods=['GET', 'POST'])
def prihlaseni():
    if request.method == 'POST':
        heslo = request.form.get('heslo', '')
        if heslo == ADMIN_PASSWORD:
            session['prihlasen'] = True
            return redirect(url_for('zobraz_data'))
        else:
            flash('Špatné heslo!', 'error')
    return '''
    <style>
        body { font-family: system-ui, sans-serif; background: #f1f5f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); width: 100%; max-width: 400px; text-align: center; }
        input { width: 100%; padding: 14px; margin: 10px 0; border: 1.5px solid #e2e8f0; border-radius: 8px; font-size: 1rem; }
        button { background: #4f46e5; color: white; padding: 14px; border: none; border-radius: 8px; width: 100%; font-size: 1.1rem; cursor: pointer; }
        button:hover { background: #4338ca; }
        h2 { margin-bottom: 20px; color: #1f2937; }
    </style>
    <div class="login-box">
        <h2>Přihlášení do správy</h2>
        <form method="post">
            <input type="password" name="heslo" placeholder="Zadej heslo" required autofocus>
            <button type="submit">Přihlásit se</button>
        </form>
    </div>
    '''

@app.route('/odhlasit')
def odhlasit():
    session.pop('prihlasen', None)
    flash('Byl jsi odhlášen.', 'info')
    return redirect(url_for('index'))

# === FORMULÁŘ (veřejný) ===
@app.route('/')
def index():
    return render_template('formular.html', data={})

@app.route('/odeslat', methods=['POST'])
def odeslat():
    # --- STEJNÝ KÓD JAKO DŘÍV (validace + ukládání) ---
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
        chyby.append('Datum narození 1. osoby: 15. 6. 1985')
    if pocet == '2' and narozeni2 and not je_platne_datum(narozeni2):
        chyby.append('Datum narození 2. osoby: 22. 9. 1988')

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

# === ZOBRAZENÍ DAT (CHRÁNĚNO HESLEM) ===
@app.route('/data')
@vyzaduj_prihlaseni
def zobraz_data():
    if not os.path.exists(CSV_FILE):
        return "<h3>Žádná data</h3><a href='/'>← Zpět</a> | <a href='/odhlasit'>Odhlásit</a>"

    with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=';')
        rows = list(reader)

    if len(rows) <= 1:
        return "<h3>Žádná data</h3><a href='/'>← Zpět</a> | <a href='/odhlasit'>Odhlásit</a>"

    html = """
    <style>
        body { font-family: system-ui, sans-serif; background: #f8fafc; padding: 20px; margin: 0; }
        h2 { color: #1f2937; text-align: center; }
        .links { text-align: center; margin: 15px 0; }
        .links a { margin: 0 10px; color: #4f46e5; }
        table { width: 100%; max-width: 1200px; margin: 20px auto; border-collapse: collapse; background: white; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #4f46e5; color: white; }
        tr:nth-child(even) { background: #f9fafb; }
        .delete-btn { background: #ef4444; color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; }
        .delete-btn:hover { background: #dc2626; }
    </style>
    <h2>Seznam hostů</h2>
    <div class="links">
        <a href='/'>← Formulář</a> | 
        <a href='/stahnout-csv'>↓ Stáhnout CSV</a> | 
        <a href='/odhlasit'>Odhlásit</a>
    </div>
    <table>
    """

    for i, row in enumerate(rows):
        if i == 0:
            html += "<tr>" + "".join(f"<th>{cell}</th>" for cell in row) + "<th>Akce</th></tr>"
            continue
        cas = row[0]
        html += "<tr>"
        for cell in row:
            html += f"<td>{cell}</td>"
        html += f"""
        <td style="text-align:center;">
            <form method="POST" action="/smazat" style="display:inline;" onsubmit="return confirm('SMAZAT?');">
                <input type="hidden" name="cas" value="{cas}">
                <button type="submit" class="delete-btn">SMAZAT</button>
            </form>
        </td>
        """
        html += "</tr>"
    html += "</table>"
    return html

# === SMAZÁNÍ (CHRÁNĚNO HESLEM) ===
@app.route('/smazat', methods=['POST'])
@vyzaduj_prihlaseni
def smazat():
    cas_k_smazani = request.form.get('cas')
    if not cas_k_smazani or not os.path.exists(CSV_FILE):
        flash("Chyba při mazání!", 'error')
        return redirect('/data')

    with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=';')
        rows = list(reader)

    new_rows = [row for row in rows if row and row[0] != cas_k_smazani]
    if len(new_rows) == len(rows):
        flash("Řádek nenalezen!", 'error')
    else:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerows(new_rows)
        flash("Smazáno!", 'success')
    return redirect('/vdata')

# === STÁHNUTÍ CSV (CHRÁNĚNO HESLEM) ===
@app.route('/stahnout-csv')
@vyzaduj_prihlaseni
def stahnout_csv():
    if not os.path.exists(CSV_FILE):
        return "Žádná data!"
    with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    return Response(
        content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=hoste.csv'}
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
