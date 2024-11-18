from flask import Flask, jsonify
from flask_restful import Api, Resource
from dotenv import load_dotenv
from pymongo import MongoClient
import os
import threading
import time
from fetch_data import fetch_and_store_bitcoin_data , get_all_bitcoin_data

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

# Periodically fetch Bitcoin data
def start_fetching():
    while True:
        fetch_and_store_bitcoin_data()
        time.sleep(10)  # Fetch data every 10 seconds




if __name__ == "__main__":
    # Start the data fetching thread
    threading.Thread(target=start_fetching, daemon=True).start()
    # Run the Flask application
    app.run(debug=True)
