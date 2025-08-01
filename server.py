from flask import Flask ,Response,request,render_template,redirect,session, url_for,jsonify
import pymongo
import json
import os
from user import User
app = Flask(__name__)
app.static_folder = 'static'
from bson.objectid import ObjectId
from cars import Cars
from werkzeug.utils import secure_filename
from datetime import datetime
from pymongo import MongoClient


##################################### MOHAMED FATEHI #########################################

## CONNECTION TO DB
try : 
    mongo = pymongo.MongoClient(host="localhost", port =27017,serverSelectionTimeoutMS =1000 )
    db = mongo.vetture #use the company db in mongo 
    mongo.server_info() 
    print("connect to db")

except : 
    print("ERROR - Cannot connect to db")


#ROOT TO LOGIN
@app.route("/login")
def blade() : 
    return render_template("login.html")

##################################### PAGINA ABOUT US E AREA ADMIN PROTETTA ###############################

# About Us
@app.route('/about')
def about():
    return render_template('about.html')


# Area Admin protetta
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'Barbarossa' and password == 'Carollo':
            session['is_admin'] = True
            return render_template('gestion_reservations.html')  # crea questa pagina o modifica come preferisci
        else:
            return render_template('admin_login.html', error='Credenziali errate')
    else:
        if session.get('is_admin'):
            return render_template('gestion_reservations.html')
        return render_template('admin_login.html')

#AUTHENTIFICATION 

@app.route("/auth", methods=["POST"])
def auth():
    email = request.form["email"]
    password = request.form["password"]
    session['email'] = email
  
    
    user = User.authenticate(email, password)
  

    if user is not None:
        # Authentication successful, redirect to get_cars route
        return redirect(url_for('get_cars'))

    return render_template("login.html", error_message="Invalid credentials")




#GET ALL THE CARS BASED ON THE ETAT 
@app.route('/cars', methods=['GET'])
def get_cars():
 email = session.get('email')

 car_list = Cars.get()
 user = User.get(email)
 return render_template('category.html', cars=car_list,user=user)

@app.route('/logout')
def logout():
    session.clear()
    return render_template('login.html')



@app.route('/addManager' ,methods=['POST','GET'])
def addManager():
    if request.method == 'POST':
        client_data = {
            'password': request.form['password'],
            'nom': request.form['nom'],
            'prenom': request.form['prenom'],
            'email': request.form['email'],
            'tel': request.form['telephone'],
            'ville': request.form['ville'],
            'role' : "manager"
        }
        db.utilisateur.insert_one(client_data)
        session['success'] = True
        return redirect('/manager')
        #return render_template('ManagerList.html',success_message="Manager bien saisie!")
    return render_template('addManager.html') 




@app.route('/addAdmin' ,methods=['POST','GET'])
def addAdmin():
    if request.method == 'POST':
        client_data = {
            'password': request.form['password'],
            'nom': request.form['nom'],
            'prenom': request.form['prenom'],
            'email': request.form['email'],
            'tel': request.form['telephone'],
            'ville': request.form['ville'],
            'role' : "admin"
        }
        db.utilisateur.insert_one(client_data)
        session['success'] = True
        return render_template('addAdmin.html',success_message="Admin bien saisie!")
    return render_template('addAdmin.html')
    
@app.route('/manager')
def list_managers():
    role = "manager"
    managers = db.utilisateur.find({'role': role})
    return render_template('ManagerList.html', clients=managers)


@app.route('/deleteManager', methods=['POST'])
def delete_manager():

    manager_id = ObjectId(request.form.get('idClient'))
    print(manager_id)

    print(f"Deleting client with ID: {manager_id}")


    result = db.utilisateur.delete_one({'_id': manager_id})

    if result.deleted_count > 0:
        return redirect(url_for('list_managers'))
    else:
        return 'Failed to delete the client or client not found.'
    
    
@app.route('/admin')
def list_admins():
    print("DEBUG: Entrato nella route /admin")
    return render_template('AdminList.html')


@app.route('/deleteAdmin', methods=['POST'])
def delete_admin():

    manager_id = ObjectId(request.form.get('idClient'))
    print(manager_id)

    print(f"Deleting client with ID: {manager_id}")


    result = db.utilisateur.delete_one({'_id': manager_id})

    if result.deleted_count > 0:
        return redirect(url_for('list_admins'))
    else:
        return 'Failed to delete the client or client not found.'


@app.route('/modify_manager', methods=['POST'])
def modify_manager():

    print(request.form)  # Debugging line
    id= ObjectId(request.form['CIN'])
    nom = request.form['nom']
    prenom = request.form['prenom']
    email = request.form['email']
    telephone = request.form['telephone']
    ville= request.form['ville']

    # Find the client with the matching CIN
    query = {'_id': id}
    client = db.utilisateur.find_one(query)

    if client:
        # Update the client data
        update = {
            '$set': {
                'nom': nom,
                'prenom': prenom,
                'email': email,
                'tel': telephone,
                'ville': ville
            }
        }
        db.utilisateur.update_one(query, update)

        return redirect(url_for('list_managers'))
    else:
        return 'Manager not found'


  
@app.route('/modify_admin', methods=['POST'])
def modify_admin():

    print(request.form)  # Debugging line
    id= ObjectId(request.form['CIN'])
    nom = request.form['nom']
    prenom = request.form['prenom']
    email = request.form['email']
    telephone = request.form['telephone']
    ville= request.form['ville']

    # Find the client with the matching CIN
    query = {'_id': id}
    client = db.utilisateur.find_one(query)

    if client:
        # Update the client data
        update = {
            '$set': {
                'nom': nom,
                'prenom': prenom,
                'email': email,
                'tel': telephone,
                'ville': ville
            }
        }
        db.utilisateur.update_one(query, update)

        return redirect(url_for('list_admins'))
    else:
        return 'Admin not found'






##############################""ANAS#######################



# Connect to MongoDB
try:
    mongo = pymongo.MongoClient(
        host='localhost', 
        port=27017,
        serverSelectionTimeoutMS = 1000     
    )

    db = mongo.vetture
    cars_collection = db['auto']
    mongo.server_info() # trigger exception if cannot connect to db
    print("Connected to db")
except:
    print("ERROR - Cannot connect to db")

@app.route('/manage_cars')
def manage_cars():
    cars = cars_collection.find()
    return render_template('managecars.html', cars=cars)

UPLOAD_FOLDER = 'static/images/cars/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/add_car', methods=['GET', 'POST'])
def add_car():
    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        year = int(request.form['year'])
        price = int(request.form['price'])
        matricule = request.form['matricule']
        image = request.files['image']

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

            car_data = {
                'marque': make,
                'modele': model,
                'annee': year,
                'prix': price,
                'matricule': matricule,
                'image': filename
            }
            cars_collection.insert_one(car_data)

            return redirect('/manage_cars')

    return render_template('addcar.html')


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/update_car', methods=['POST'])
def update_car():
    car_id = request.form.get('carId')
    make = request.form['make']
    model = request.form['model']
    year = int(request.form['year'])
    price = int(request.form['price'])
    matricule = request.form['matricule']

    filter_criteria = {'_id': ObjectId(car_id)}
    update_data = {'$set': {'marque': make, 'modele': model, 'annee': year, 'prix': price, 'matricule': matricule}}

    try:
        cars_collection.update_one(filter_criteria, update_data)
        return redirect('/manage_cars')
    except Exception as e:
        print(f"Error updating document: {e}")


@app.route('/modify_car')
def modify_car():
    car_id = request.args.get('carId')
    car = cars_collection.find_one({'_id': ObjectId(car_id)})

    if car:
        return render_template('modifycar.html', car=car)
    else:
        return "Car not found"

@app.route('/delete_car', methods=['POST'])
def delete_car():
    car_id = request.form.get('carId')

    try:
        cars_collection.delete_one({'_id': ObjectId(car_id)})
        return redirect('/manage_cars')
    except Exception as e:
        print(f"Error deleting document: {e}")



############################ AHMED ##################################

app.secret_key = 'HereWegoAgain'


client = MongoClient('mongodb://localhost:27017')
db = client['vetture']
collection = db['client']


@app.route('/AddNewClient')
def hello():
    return render_template('AddNewClient.html')

@app.route('/add_client', methods=['POST'])
def add_client():
    client_data = {
        'cin': request.form['CIN'],
        'nom': request.form['nom'],
        'prenom': request.form['prenom'],
        'email': request.form['email'],
        'tel': request.form['telephone'],
        'adresse': request.form['adresse']
    }
    collection.insert_one(client_data)

    session['success'] = True

    return redirect(url_for('list_clients'))


@app.route('/clients')
def list_clients():
    clients = collection.find()
    return render_template('ClientList.html', clients=clients, client=None)





@app.route('/deleteClient', methods=['POST'])
def delete_client():

    client_id = request.form.get('idClient')

    print(f"Deleting client with ID: {client_id}")


    result = collection.delete_one({'cin': client_id})

    if result.deleted_count > 0:
        return redirect(url_for('list_clients'))
    else:
        return 'Failed to delete the client or client not found.'
    





@app.route('/add_new_client')
def add_new_client():
    success = session.pop('success', False)
    if success:
        return """
        <script>
            Swal.fire({
                title: 'Success!',
                text: 'Client data inserted successfully.',
                icon: 'success',
                confirmButtonText: 'OK'
            });
        </script>
        """

    return render_template('AddNewClient.html')
@app.route('/modify_client', methods=['POST'])
def modify_client():

    print(request.form)  # Debugging line
    cin = request.form['CIN']
    nom = request.form['nom']
    prenom = request.form['prenom']
    email = request.form['email']
    telephone = request.form['telephone']
    adresse = request.form['adresse']

    # Find the client with the matching CIN
    query = {'cin': cin}
    client = collection.find_one(query)

    if client:
        # Update the client data
        update = {
            '$set': {
                'nom': nom,
                'prenom': prenom,
                'email': email,
                'tel': telephone,
                'adresse': adresse
            }
        }
        collection.update_one(query, update)

        return redirect(url_for('list_clients'))
    else:
        return 'Client not found'






############################### MOUAD ###################################
reservation_collection = db['reservation']

@app.route("/location_car/<voiture_id>", methods=['GET', 'POST'])
def location_car(voiture_id):
    from datetime import timedelta
    if request.method == 'POST':
        date_debut_str = request.form.get('date_debut')
        date_fin_str = request.form.get('date_fin')
        try:
            try:
                obj_id = ObjectId(voiture_id)
                auto = db['auto'].find_one({"_id": obj_id})
            except Exception:
                auto = db['auto'].find_one({"_id": voiture_id})
            print(f"ID cercato: {voiture_id}, auto trovata: {auto}")
            if not auto:
                return render_template("location_car.html", voiture_id=voiture_id, auto=None, error_message="Auto non trovata. Controlla l'ID o i dati nel database.")
            date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d")
            date_fin = datetime.strptime(date_fin_str, "%Y-%m-%d")
            oggi = datetime.now().date()
            if date_debut.date() < oggi:
                return render_template("location_car.html", voiture_id=voiture_id, auto=auto, error_message="Non è possibile prenotare per oggi o per una data passata.")
            diff_days = (date_fin - date_debut).days
            diff_days += 1
            prezzo_auto = auto.get('prezzo', 0)
            price = diff_days * prezzo_auto
            statut = request.form.get('statut', 'en_attente')
            # Nuovi campi dal form
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
            # Mostra la stessa pagina con messaggio di successo
            # Calcola giorni bloccati per questa auto (prenotazioni accettate)
            prenotazioni_accettate = reservation_collection.find({
                "auto_id": voiture_id,
                "statut": "accettata"
            })
            giorni_bloccati = []
            for pren in prenotazioni_accettate:
                start = pren['date_debut']
                end = pren['date_fin']
                if isinstance(start, str):
                    try:
                        start = datetime.strptime(start, "%Y-%m-%d")
                    except:
                        continue
                if isinstance(end, str):
                    try:
                        end = datetime.strptime(end, "%Y-%m-%d")
                    except:
                        continue
                while start <= end:
                    giorni_bloccati.append(start.strftime("%Y-%m-%d"))
                    start += timedelta(days=1)
            return render_template("location_car.html", voiture_id=voiture_id, auto=auto, success_message="Prenotazione avvenuta con successo!", giorni_bloccati=giorni_bloccati)
        except Exception as e:
            print(f"Errore nella ricerca auto: {e}")
            # Calcola giorni bloccati anche in caso di errore
            prenotazioni_accettate = reservation_collection.find({
                "auto_id": voiture_id,
                "statut": "accettata"
            })
            giorni_bloccati = []
            for pren in prenotazioni_accettate:
                start = pren['date_debut']
                end = pren['date_fin']
                if isinstance(start, str):
                    try:
                        start = datetime.strptime(start, "%Y-%m-%d")
                    except:
                        continue
                if isinstance(end, str):
                    try:
                        end = datetime.strptime(end, "%Y-%m-%d")
                    except:
                        continue
                while start <= end:
                    giorni_bloccati.append(start.strftime("%Y-%m-%d"))
                    start += timedelta(days=1)
            return render_template("location_car.html", voiture_id=voiture_id, auto=None, error_message="Errore nella ricerca auto.", giorni_bloccati=giorni_bloccati)
    clients = db['client'].find()
    # Logga tutti gli ID delle auto presenti
    all_autos = list(db['auto'].find())
    print('ID auto presenti nel database:')
    for a in all_autos:
        print(a['_id'])
    # Calcola giorni bloccati per questa auto (prenotazioni accettate)
    prenotazioni_accettate = reservation_collection.find({
        "auto_id": voiture_id,
        "statut": "accettata"
    })
    giorni_bloccati = []
    for pren in prenotazioni_accettate:
        start = pren['date_debut']
        end = pren['date_fin']
        if isinstance(start, str):
            try:
                start = datetime.strptime(start, "%Y-%m-%d")
            except:
                continue
        if isinstance(end, str):
            try:
                end = datetime.strptime(end, "%Y-%m-%d")
            except:
                continue
        while start <= end:
            giorni_bloccati.append(start.strftime("%Y-%m-%d"))
            start += timedelta(days=1)
    # Prova a convertire l'id in ObjectId, se fallisce usa la stringa
    try:
        obj_id = ObjectId(voiture_id)
        voitures = db['auto'].find_one({"_id": obj_id})
    except Exception:
        voitures = db['auto'].find_one({"_id": voiture_id})
    print(f"ID cercato (GET): {voiture_id}, auto trovata: {voitures}")
    if not voitures:
        return render_template("location_car.html", clients=clients, voiture_id=voiture_id, auto=None, error_message="Auto non trovata. Controlla l'ID o i dati nel database.", giorni_bloccati=giorni_bloccati)
    return render_template("location_car.html", clients=clients, voiture_id=voiture_id, auto=voitures, giorni_bloccati=giorni_bloccati)


# Route to display all reservations and handle accept/refuse functionality
@app.route('/gestion_reservations', methods=['GET', 'POST'])
def gestion_reservations():
    if request.method == 'POST':
        reservation_id = request.form.get('reservation_id')  # Get the reservation ID from the submitted form
        action = request.form.get('action')  # Get the action (accept/refuse) from the submitted form
        
        print(reservation_id, action)
        
        # Update the reservation status based on the action
        reservation_collection.update_one({'_id': ObjectId(reservation_id)}, {'$set': {'statut': action}})
        
        # return 'Reservation updated successfully!'
    
            
    # Fetch all reservations with status 'en_attente' or 'accettata'
    reservations_raw = list(reservation_collection.find({"statut": {"$in": ["en_attente", "accettata"]}}))
    enriched_reservations = []
    for reservation in reservations_raw:
        # Recupera l'auto associata
        auto_id = reservation.get('auto_id')
        try:
            auto_obj_id = ObjectId(auto_id)
        except Exception:
            auto_obj_id = auto_id
        auto = db['auto'].find_one({'_id': auto_obj_id})
        # Marca e modello
        marque = reservation.get('marque') or (auto.get('marque') if auto else '')
        modele = reservation.get('modele') or (auto.get('modele') if auto else '')
        # Calcolo prezzo totale
        date_debut = reservation.get('date_debut')
        date_fin = reservation.get('date_fin')
        if isinstance(date_debut, str):
            try:
                date_debut = datetime.strptime(date_debut, "%Y-%m-%d")
            except:
                date_debut = None
        if isinstance(date_fin, str):
            try:
                date_fin = datetime.strptime(date_fin, "%Y-%m-%d")
            except:
                date_fin = None
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




# Route to edit a reservation
@app.route('/edit_reservation/<reservation_id>', methods=['GET', 'POST'])
def edit_reservation(reservation_id):
    # Retrieve the reservation object using reservation_id (example implementation)
    reservation = db.reservations.find_one({'_id': ObjectId(reservation_id)})
    print(reservation_id, reservation.get('client_id'))

    return render_template('edit_reservation.html', reservation=reservation)


# Route to dashboard
@app.route('/dashboardTest')
def dashboardtest():
    # Fetch all reservations from the collection
    reservations = list(reservation_collection.find())
    client_collection = db['client']
    
    
    # Fetch all clients from the collection
    clients = list(client_collection.find())
    
    # Extract the status counts from reservations
    status_counts = {}
    for reservation in reservations:
        status = reservation.get('statut')
        if status:
            status_counts[status] = status_counts.get(status, 0) + 1
            
            



    # Extract the address counts from clients
    address_counts = {}
    for client in clients:
        address = client.get('adresse')
        if address:
            address_counts[address] = address_counts.get(address, 0) + 1

    
    # Prepare the data for the chart
    labels = list(status_counts.keys())
    data = list(status_counts.values())



    # Prepare the data for the chart
    labels1 = list(address_counts.keys())
    data1 = list(address_counts.values())
    
    
    
    return render_template('dashboard_test.html', 
                           labels=json.dumps(labels), 
                           data=json.dumps(data),
                           labels1=json.dumps(labels1), 
                           data1=json.dumps(data1)
                           )



@app.route("/")
def home():
    return render_template("index.html")





####################################
# if the script is the main programme, else if its imported from another module not __main__
if __name__ == "__main__"  :
    app.run(port =80, debug =True )


@app.route('/search', methods=['GET'])
def search():
    pickup_date = request.args.get('pickup_date')
    dropoff_date = request.args.get('dropoff_date')
    category = request.args.get('category')

    # Validate and parse dates
    try:
        if pickup_date:
            pickup_date_obj = datetime.strptime(pickup_date, '%Y-%m-%d')
        else:
            pickup_date_obj = None
    except Exception:
        pickup_date_obj = None
        pickup_date = None
    try:
        if dropoff_date:
            dropoff_date_obj = datetime.strptime(dropoff_date, '%Y-%m-%d')
        else:
            dropoff_date_obj = None
    except Exception:
        dropoff_date_obj = None
        dropoff_date = None

    # Example: Query cars by category (add date logic as needed)
    query = {}
    if category:
        query['categorie'] = category  # Adjust field name to match your DB

    cars_collection = db['auto']
    cars = list(cars_collection.find(query))

    # Render a results page (e.g., search_results.html) with the filtered cars
    return render_template('search_results.html', cars=cars, pickup_date=pickup_date, dropoff_date=dropoff_date, category=category)

