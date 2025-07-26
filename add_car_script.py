from pymongo import MongoClient
from datetime import datetime
import random

# Connessione al database MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['vetture']
cars_collection = db['auto']

# Dati di esempio per la nuova auto (modifica se vuoi)
marche = ['Fiat', 'Ford', 'Renault', 'Peugeot', 'Toyota', 'Volkswagen']
modelli = ['Panda', 'Focus', 'Clio', '208', 'Yaris', 'Golf']

car_data = {
    'marque': random.choice(marche),
    'modele': random.choice(modelli),
    'annee': random.randint(2015, 2025),
    'prix': random.randint(20, 100),
    'matricule': f"{random.randint(100,999)}-{random.choice(['AA','BB','CC','DD'])}-{random.randint(100,999)}",
    'image': 'default.jpg',
    'created_at': datetime.now()
}

result = cars_collection.insert_one(car_data)
print(f"Auto inserita con _id: {result.inserted_id}\nDati: {car_data}")
