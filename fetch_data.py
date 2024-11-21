import requests
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
from predict import calculate_growth_rate, predict_next_value, fetch_bitcoin_data, load_model
import numpy as np
# Charger les variables d'environnement
load_dotenv()

COINCAP_API_URL = os.getenv("COINCAP_API_URL")
MONGODB_URI = os.getenv("MONGODB_URI")
MODEL_PATH = "logistic_regression_model.pkl"
model = load_model(MODEL_PATH)


# Connexion à MongoDB
client = MongoClient(MONGODB_URI)
db = client.get_database("cryptodash")
bitcoin_collection = db["bitcoin_data"]

def fetch_and_store_bitcoin_data():
    try:
        # Requête à l'API CoinCap
        response = requests.get(COINCAP_API_URL)
        response.raise_for_status()
        data = response.json().get("data")

        # Récupérer le prix actuel
        current_price = float(data["priceUsd"])

        # Récupérer les données précédentes depuis MongoDB
        last_record = bitcoin_collection.find_one(sort=[("timestamp", -1)])  # Dernier document

        if last_record:
            previous_price = last_record["price_usd"]
            # Calculer le taux de croissance
            growth_rate = calculate_growth_rate(current_price, previous_price)
        else:
            # Aucun taux de croissance si pas de données précédentes
            growth_rate = 0.0

        # Préparer les données pour prédiction
        features = np.array([[ 
            float(data["priceUsd"]), 
            float(data["marketCapUsd"]),
            float(data["volumeUsd24Hr"]),
            float(data["vwap24Hr"])
        ]])

        # Prédire la prochaine valeur
        predicted_next_price = predict_next_value(model, features, current_price, growth_rate)

        # Préparer les données pour MongoDB
        document = {
            "name": data["name"],
            "supply": float(data["supply"]),
            "max_supply": float(data["maxSupply"]) if data["maxSupply"] else None,
            "price_usd": current_price,
            "market_cap_usd": float(data["marketCapUsd"]),
            "change_percent_24hr": float(data["changePercent24Hr"]),
            "volume_usd_24hr": float(data["volumeUsd24Hr"]),
            "vwap_24hr": float(data["vwap24Hr"]),
            "explorer": data["explorer"],
            "growth_rate": growth_rate,
            "predicted_next_price": predicted_next_price,
            "timestamp": datetime.utcnow()
        }

        # Insertion dans MongoDB
        bitcoin_collection.insert_one(document)
        print("Données récupérées et enregistrées avec succès !")
        print(f"Taux de croissance : {growth_rate:.2f}%")
        print(f"Prochaine valeur prédite : {predicted_next_price:.2f} USD")

    except Exception as e:
        print(f"Erreur lors de la récupération des données : {e}")


def get_all_bitcoin_data():
    """
    Récupère toutes les données Bitcoin stockées dans la collection MongoDB.
    :return: Liste de dictionnaires représentant les données Bitcoin.
    """
    try:
        data = list(bitcoin_collection.find({}, {"_id": 0}))  # Exclure le champ `_id`
        export_to_excel(data)
        return data
    except Exception as e:
        print(f"Erreur lors de la récupération des données depuis MongoDB : {e}")
        return []

def export_to_excel(data):
    """Export Bitcoin data to an Excel file."""
    try:
        # data = list(bitcoin_collection.find({}, {"_id": 0}))  # Exclure le champ `_id`

        # Convert the data into a pandas DataFrame
        df = pd.DataFrame(data)

        # Define the filename
        filename = f"bitcoin_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
        
        # Save the DataFrame to Excel
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"Data exported to {filename}")
    except Exception as e:
        print(f"Error exporting data to Excel: {e}")