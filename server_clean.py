from flask import Flask, request, render_template, redirect, session
import pymongo
import os
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.static_folder = 'static'
app.secret_key = 'HereWegoAgain'

# Connessione al DB
try:
    mongo = pymongo.MongoClient(host="localhost", port=27017, serverSelectionTimeoutMS=1000)
    db = mongo.vetture
    mongo.server_info()
    print("connect to db")
except:
    print("ERROR - Cannot connect to db")

# Homepage
@app.route("/")
def home():
    return render_template("index.html")

# About Us
@app.route('/about')
def about():
    return render_template('about.html')

# Area Admin protetta (login hardcoded)
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'Barbarossa' and password == 'Carollo':
            session['is_admin'] = True
            return redirect('/gestion_reservations')
        else:
            return render_template('admin_login.html', error='Credenziali errate')
    else:
        if session.get('is_admin'):
            return redirect('/gestion_reservations')
        return render_template('admin_login.html')

# Visualizza tutte le auto
@app.route('/cars', methods=['GET'])
def get_cars():
    cars = list(db['auto'].find())
    return render_template('category.html', cars=cars)

# Prenotazione auto
@app.route("/location_car/<voiture_id>", methods=['GET', 'POST'])
def location_car(voiture_id):
    from datetime import timedelta
    reservation_collection = db['reservation']
    if request.method == 'POST':
        date_debut_str = request.form.get('date_debut')
        date_fin_str = request.form.get('date_fin')
        try:
            obj_id = ObjectId(voiture_id)
            auto = db['auto'].find_one({"_id": obj_id})
        except Exception:
            auto = db['auto'].find_one({"_id": voiture_id})
        if not auto:
            return render_template("location_car.html", voiture_id=voiture_id, auto=None, error_message="Auto non trovata.")
        date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d")
        date_fin = datetime.strptime(date_fin_str, "%Y-%m-%d")
        oggi = datetime.now().date()
        if date_debut.date() < oggi:
            return render_template("location_car.html", voiture_id=voiture_id, auto=auto, error_message="Non è possibile prenotare per oggi o per una data passata.")
        diff_days = (date_fin - date_debut).days + 1
        prezzo_auto = auto.get('prezzo', 0)
        price = diff_days * prezzo_auto
        statut = request.form.get('statut', 'en_attente')
        nome = request.form.get('nome')
        cognome = request.form.get('cognome')
        email = request.form.get('email')
        reservation = {
            'auto_id': voiture_id,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'prix_reservation': price,
            'statut': statut,
            'marque': auto.get('marca', ''),
            'modele': auto.get('modello', ''),
            'prezzo': prezzo_auto,
            'nome': nome,
            'cognome': cognome,
            'email': email
        }
        reservation_collection.insert_one(reservation)
        # Giorni bloccati
        prenotazioni_accettate = reservation_collection.find({"auto_id": voiture_id, "statut": "accettata"})
        giorni_bloccati = []
        for pren in prenotazioni_accettate:
            start = pren['date_debut']
            end = pren['date_fin']
            if isinstance(start, str):
                try: start = datetime.strptime(start, "%Y-%m-%d")
                except: continue
            if isinstance(end, str):
                try: end = datetime.strptime(end, "%Y-%m-%d")
                except: continue
            while start <= end:
                giorni_bloccati.append(start.strftime("%Y-%m-%d"))
                start += timedelta(days=1)
        return render_template("location_car.html", voiture_id=voiture_id, auto=auto, success_message="Prenotazione avvenuta con successo!", giorni_bloccati=giorni_bloccati)
    # GET: mostra giorni bloccati
    prenotazioni_accettate = db['reservation'].find({"auto_id": voiture_id, "statut": "accettata"})
    giorni_bloccati = []
    for pren in prenotazioni_accettate:
        start = pren['date_debut']
        end = pren['date_fin']
        if isinstance(start, str):
            try: start = datetime.strptime(start, "%Y-%m-%d")
            except: continue
        if isinstance(end, str):
            try: end = datetime.strptime(end, "%Y-%m-%d")
            except: continue
        while start <= end:
            giorni_bloccati.append(start.strftime("%Y-%m-%d"))
            start += timedelta(days=1)
    try:
        obj_id = ObjectId(voiture_id)
        auto = db['auto'].find_one({"_id": obj_id})
    except Exception:
        auto = db['auto'].find_one({"_id": voiture_id})
    if not auto:
        return render_template("location_car.html", voiture_id=voiture_id, auto=None, error_message="Auto non trovata.", giorni_bloccati=giorni_bloccati)
    return render_template("location_car.html", voiture_id=voiture_id, auto=auto, giorni_bloccati=giorni_bloccati)

# Gestione prenotazioni (admin)
@app.route('/gestion_reservations', methods=['GET', 'POST'])
def gestion_reservations():
    reservation_collection = db['reservation']
    if not session.get('is_admin'):
        return redirect('/admin')
    if request.method == 'POST':
        reservation_id = request.form.get('reservation_id')
        action = request.form.get('action')
        reservation_collection.update_one({'_id': ObjectId(reservation_id)}, {'$set': {'statut': action}})
    reservations_raw = list(reservation_collection.find({"statut": {"$in": ["en_attente", "accettata"]}}))
    enriched_reservations = []
    for reservation in reservations_raw:
        auto_id = reservation.get('auto_id')
        try:
            auto_obj_id = ObjectId(auto_id)
        except Exception:
            auto_obj_id = auto_id
        auto = db['auto'].find_one({'_id': auto_obj_id})
        marque = reservation.get('marque') or (auto.get('marque') if auto else '')
        modele = reservation.get('modele') or (auto.get('modele') if auto else '')
        date_debut = reservation.get('date_debut')
        date_fin = reservation.get('date_fin')
        if isinstance(date_debut, str):
            try: date_debut = datetime.strptime(date_debut, "%Y-%m-%d")
            except: date_debut = None
        if isinstance(date_fin, str):
            try: date_fin = datetime.strptime(date_fin, "%Y-%m-%d")
            except: date_fin = None
        prix_reservation = reservation.get('prix_reservation')
        if (not prix_reservation or prix_reservation == 0) and auto and date_debut and date_fin:
            diff_days = (date_fin - date_debut).days
            prix_reservation = diff_days * auto.get('prezzo', 0)
        enriched_reservations.append({
            '_id': reservation.get('_id'),
            'email': reservation.get('email', ''),
            'nome': reservation.get('nome', ''),
            'cognome': reservation.get('cognome', ''),
            'marque': marque,
            'modele': modele,
            'date_debut': date_debut.strftime('%d/%m/%Y') if date_debut else '',
            'date_fin': date_fin.strftime('%d/%m/%Y') if date_fin else '',
            'prix_reservation': prix_reservation,
            'statut': reservation.get('statut', '')
        })
    return render_template('gestion_reservations.html', reservations=enriched_reservations)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port, debug=True)
