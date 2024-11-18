from flask import Flask, jsonify
from flask_restful import Api, Resource
from dotenv import load_dotenv
from pymongo import MongoClient
import os
import threading
import time
from fetch_data import fetch_and_store_bitcoin_data, get_all_bitcoin_data

# Importer les méthodes de train.py
from predict import load_model, fetch_bitcoin_data, calculate_growth_rate, predict_next_value

# Charger le modèle de prédiction
MODEL_PATH = "logistic_regression_model.pkl"
model = load_model(MODEL_PATH)

# Load environment variables
load_dotenv()

app = Flask(__name__)
api = Api(app)

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client.get_database("cryptodash")
bitcoin_collection = db["bitcoin_data"]

# API to fetch stored Bitcoin data
class BitcoinDataAPI(Resource):
    def get(self):
        try:
            # Retrieve data from MongoDB
            data = get_all_bitcoin_data()
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# Add the resource to the API
api.add_resource(BitcoinDataAPI, "/api/bitcoin-data")

# Periodically fetch Bitcoin data and predict
def start_fetching_and_predicting():
    previous_price = None  # Initialiser le prix précédent
    while True:
        # Récupérer et stocker les données actuelles
        current_price, bitcoin_data = fetch_bitcoin_data()

        # Si un prix précédent existe, calculer et prédire
        if previous_price is not None:
            # Calculer le taux de croissance
            growth_rate = calculate_growth_rate(current_price, previous_price)
            # Prédire la prochaine valeur
            next_price = predict_next_value(model, bitcoin_data, current_price, growth_rate)
            print(f"Prix actuel : {current_price:.2f} USD")
            print(f"Taux de croissance : {growth_rate:.2f}%")
            print(f"Prochaine valeur prédite : {next_price:.2f} USD")

            # Ajouter les prédictions dans MongoDB
            bitcoin_collection.insert_one({
                "current_price": current_price,
                "growth_rate": growth_rate,
                "predicted_next_price": next_price,
                "timestamp": time.time()
            })
        else:
            # Ajouter les données sans prédiction pour la première entrée
            bitcoin_collection.insert_one({
                "current_price": current_price,
                "timestamp": time.time()
            })

        # Mettre à jour le prix précédent
        previous_price = current_price

        # Attendre avant la prochaine itération
        time.sleep(10)  # Fetch data every 10 seconds

if __name__ == "__main__":
    # Start the data fetching and prediction thread
    threading.Thread(target=start_fetching_and_predicting, daemon=True).start()
    # Run the Flask application
    app.run(debug=True)
