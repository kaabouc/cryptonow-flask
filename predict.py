from pymongo import MongoClient
import requests
import numpy as np
import pickle

# Charger le modèle sauvegardé
def load_model(filepath):
    with open(filepath, "rb") as file:
        model = pickle.load(file)
    return model

# MongoDB configuration
MONGODB_URI = "mongodb://localhost:27017/"  # Remplacez par votre URI
client = MongoClient(MONGODB_URI)
db = client.get_database("cryptodash")
bitcoin_price_collection = db["bitcoin_prices"]

# Récupérer les données Bitcoin
def fetch_bitcoin_data():
    url = "https://api.coincap.io/v2/assets/bitcoin"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["data"]
        features = [
            float(data["priceUsd"]),
            float(data["marketCapUsd"]),
            float(data["volumeUsd24Hr"]),
            float(data["vwap24Hr"])
        ]
        return float(data["priceUsd"]), np.array([features])
    else:
        raise RuntimeError(f"Erreur API : {response.status_code}")

# Calculer le taux d'augmentation
def calculate_growth_rate(current_price, previous_price):
    return ((current_price - previous_price) / previous_price) * 100

# Prédire la prochaine valeur
def predict_next_value(model, current_data, current_price, growth_rate):
    # Si le modèle prédit une augmentation
    if model.predict(current_data)[0] == 1:
        next_price = current_price * (1 + growth_rate / 100)
    else:
        next_price = current_price * (1 - abs(growth_rate) / 100)
    return next_price

# Obtenir le dernier prix sauvegardé
def get_previous_price():
    last_entry = bitcoin_price_collection.find_one(sort=[("_id", -1)])  # Récupérer le dernier enregistrement
    if last_entry:
        return last_entry["price"]
    else:
        return None  # Aucun prix précédent trouvé

# Sauvegarder le prix actuel
def save_current_price(price):
    bitcoin_price_collection.insert_one({"price": price})

# Initialiser le modèle
model_filepath = "logistic_regression_model.pkl"
model = load_model(model_filepath)

# Exemple de test
try:
    # Obtenir le prix précédent
    previous_price = get_previous_price()
    if previous_price is None:
        previous_price = 43000  # Valeur par défaut si aucun prix n'est trouvé

    # Récupérer les données actuelles
    current_price, bitcoin_data = fetch_bitcoin_data()

    # Sauvegarder le prix actuel dans la base de données
    save_current_price(current_price)

    # Calculer le taux d'augmentation
    growth_rate = calculate_growth_rate(current_price, previous_price)
    print(f"Taux de croissance : {growth_rate:.2f}%")

    # Prédire la prochaine valeur
    next_price = predict_next_value(model, bitcoin_data, current_price, growth_rate)
    print(f"Prix actuel : {current_price:.2f} USD")
    print(f"Prix previous : {previous_price:.2f} USD")
    print(f"Prochaine valeur prédite : {next_price:.2f} USD")
except Exception as e:
    print(f"Erreur : {e}")
