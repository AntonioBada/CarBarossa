from flask import redirect, render_template, url_for
import pymongo
class Cars:
    def __init__(self, model, brand, matricule, year, price, image, id_user, id,statut):
        self.model = model
        self.brand = brand
        self.matricule = matricule
        self.year = year
        self.price = price
        self.image = image
        self.id_user = id_user
        self.id = id
        self.statut = statut


    @staticmethod
    def get():
        try:
            mongo = pymongo.MongoClient(host="localhost", port=27017, serverSelectionTimeoutMS=1000)
            db = mongo.vetture  # Usa il database corretto
            mongo.server_info()
            print("Connected to MongoDB vetture")
        except Exception as e:
            print("ERROR - Cannot connect to MongoDB vetture:", str(e))
            return

        cars_collection = db['auto']  # Usa la collezione corretta
        reservations_collection = db['reservation']

        result = cars_collection.find()

        car_list = []
        for car in result:
            reservation = reservations_collection.find_one({"auto_id": car["_id"]})
            statut = reservation["statut"] if reservation else None

            car_list.append({
                "_id": car["_id"],
                "model": car.get("modello", ""),
                "brand": car.get("marca", ""),
                "matricule": car.get("targa", ""),
                "year": car.get("anno", ""),
                "price": car.get("prezzo", ""),
                "image": car.get("image", ""),
                "descrizione": car.get("descrizione", ""),
                "statut": statut
            })

        return car_list
