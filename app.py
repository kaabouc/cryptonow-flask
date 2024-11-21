from flask import Flask, jsonify
from flask_restful import Api, Resource
from dotenv import load_dotenv
from pymongo import MongoClient
from flask_socketio import SocketIO
import schedule
import os
import threading
import time
from fetch_data import fetch_and_store_bitcoin_data, get_all_bitcoin_data , get_last_predicted_price
from task_detail import regenerate_model, stop_requests, recreate_bitcoin_data 

# Load environment variables
load_dotenv()

app = Flask(__name__)
api = Api(app)
socketio = SocketIO(app, cors_allowed_origins="*")  # Activer les connexions cross-origin

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


def start_real_time_fetching():
    while True:
        try:
            # Récupérer les nouvelles données et les stocker
            fetch_and_store_bitcoin_data()

            # Obtenir la dernière valeur prédite
            last_price = get_last_predicted_price()

            # Envoyer la dernière prédiction au frontend
            if last_price is not None:
                socketio.emit("update_price", {"predicted_price": last_price})
                print(f"Valeur prédite envoyée : {last_price}")
        except Exception as e:
            print(f"Erreur : {e}")

        time.sleep(10)  # Récupérer les données toutes les 10 secondes


# Periodically fetch Bitcoin data
def start_fetching():
    while True:
        fetch_and_store_bitcoin_data()
        time.sleep(10)  # Fetch data every 10 seconds

# Function for daily tasks
def daily_tasks():
    print("Starting daily tasks...")
    stop_requests()              # Stopper les requêtes
    recreate_bitcoin_data()      # Recréer le fichier bitcoin_data.xlsx
    regenerate_model()           # Regénérer le modèle logistic_regression_model.pkl
    print("Daily tasks completed!")

# Schedule daily tasks at 11:00
def schedule_tasks():
    schedule.every().day.at("02:09").do(daily_tasks)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # Start the data fetching thread
    # threading.Thread(target=start_fetching, daemon=True).start()

    # Start the task scheduler thread
    threading.Thread(target=start_real_time_fetching, daemon=True).start()

    # threading.Thread(target=schedule_tasks, daemon=True).start()

    # Run the Flask application
    app.run(debug=True)
