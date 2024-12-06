import os
import requests
import json
import google.generativeai as genai
from dotenv import load_dotenv
import time  # For periodic fetching

# Charger les variables d'environnement
load_dotenv()

# Configurations API
GENAI_API_KEY = os.getenv("GEMINI_CLE")
COINCAP_API_URL = "https://api.coincap.io/v2/assets/bitcoin"  # URL pour les données Bitcoin
SENTIMENT_FILE = "sentiment/sentiment_values.json"  # Fichier des données de sentiment

# Configurer l'API de Google Generative AI
genai.configure(api_key=GENAI_API_KEY)

# Fonction pour récupérer les données de Bitcoin
def get_bitcoin_data():
    try:
        response = requests.get(COINCAP_API_URL)
        response.raise_for_status()  # Vérifier les erreurs HTTP
        data = response.json()["data"]
        return {
            "price": float(data["priceUsd"]),
            "market_cap": float(data["marketCapUsd"]),
            "volume_24h": float(data["volumeUsd24Hr"]),
            "supply": float(data["supply"]),
            "change_24h": float(data["changePercent24Hr"]),
        }
    except Exception as e:
        raise Exception(f"Erreur lors de la récupération des données Bitcoin: {e}")

# Fonction pour calculer le sentiment global
def calculate_sentiment():
    try:
        with open(SENTIMENT_FILE, "r") as file:
            sentiment_values = json.load(file)
            positive = sentiment_values["positive_percentage"]
            negative = sentiment_values["negative_percentage"]
            if positive + negative == 0:
                raise ValueError("Les pourcentages de sentiment sont invalides.")
            return (positive * 100) / (positive + negative)
    except FileNotFoundError:
        raise Exception(f"Fichier de sentiment non trouvé : {SENTIMENT_FILE}")
    except Exception as e:
        raise Exception(f"Erreur lors du calcul du sentiment : {e}")

# Générer une analyse avec l'IA
def generate_analysis(data, sentiment):
    try:
        prompt = (
            f"Bitcoin Data:\n"
            f"Price: ${data['price']:.2f}, Market Cap: ${data['market_cap']:.2f}, "
            f"24h Volume: ${data['volume_24h']:.2f}, Supply: {data['supply']:.2f}, "
            f"24h Change: {data['change_24h']:.2f}%. Sentiment: {sentiment:.2f}% positive.\n\n"
            "Based on these indicators, provide a concise recommendation on whether to buy, sell, or hold Bitcoin."
        )
        chat_session = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "max_output_tokens": 100,
            }
        ).start_chat(history=[])
        response = chat_session.send_message(prompt)
        return response.text.strip()
    except Exception as e:
        raise Exception(f"Erreur lors de la génération de l'analyse AI : {e}")

# Main function for continuous fetching
def continuous_analysis(interval=5):
    try:
        while True:
            print("\nFetching new data...\n")
            
            # Étape 1 : Récupérer les données Bitcoin
            bitcoin_data = get_bitcoin_data()

            # Étape 2 : Calculer le score de sentiment
            sentiment_score = calculate_sentiment()

            # Étape 3 : Générer l'analyse avec l'IA
            ai_analysis = generate_analysis(bitcoin_data, sentiment_score)

            # Étape 4 : Afficher les résultats
            print("AI Analysis and Recommendation:")
            print(ai_analysis)
            
            # Pause avant le prochain cycle
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nAnalyse interrompue par l'utilisateur.")
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    continuous_analysis(interval=5)
