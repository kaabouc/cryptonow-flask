import requests
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
# Charger les variables d'environnement
load_dotenv()

COINCAP_API_URL = os.getenv("COINCAP_API_URL")
MONGODB_URI = os.getenv("MONGODB_URI")

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

        # Préparer les données pour MongoDB
        document = {
            "name": data["name"],
            "supply": float(data["supply"]),
            "max_supply": float(data["maxSupply"]),
            "price_usd": float(data["priceUsd"]),
            "market_cap_usd": float(data["marketCapUsd"]),
            "change_percent_24hr": float(data["changePercent24Hr"]),
            "volume_usd_24hr": float(data["volumeUsd24Hr"]),
            "vwap_24hr": float(data["vwap24Hr"]),
            "explorer": data["explorer"],
            "timestamp": datetime.utcnow()
        }
        print(document)
        # Insertion dans MongoDB
        bitcoin_collection.insert_one(document)
        print("Données récupérées et enregistrées avec succès !")
      
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
        # Convert the data into a pandas DataFrame
        df = pd.DataFrame(data)

        # Define the filename
        filename = f"bitcoin_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
        
        # Save the DataFrame to Excel
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"Data exported to {filename}")
    except Exception as e:
        print(f"Error exporting data to Excel: {e}")