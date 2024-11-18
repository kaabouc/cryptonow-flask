import requests
import pickle
import numpy as np

# Charger le modèle sauvegardé
def load_model(filepath):
    with open(filepath, "rb") as file:
        model = pickle.load(file)
    return model

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

# Initialiser le modèle
model_filepath = "logistic_regression_model.pkl"
model = load_model(model_filepath)

# Exemple de test
try:
    # Simuler une valeur précédente pour le calcul du taux
    previous_price = 43000  # Exemple de prix précédent, à remplacer par une source réelle
    current_price, bitcoin_data = fetch_bitcoin_data()

    # Calculer le taux d'augmentation
    growth_rate = calculate_growth_rate(current_price, previous_price)
    print(f"Taux de croissance : {growth_rate:.2f}%")

    # Prédire la prochaine valeur
    next_price = predict_next_value(model, bitcoin_data, current_price, growth_rate)
    print(f"Prix actuel : {current_price:.2f} USD")
    print(f"Prochaine valeur prédite : {next_price:.2f} USD")
except Exception as e:
    print(f"Erreur : {e}")
