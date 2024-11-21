import os
import schedule
import time
import requests
from subprocess import Popen, PIPE

# Étape 1 : Stopper les requêtes en cours
def stop_requests():
    print("Stopping all ongoing requests...")
    # Ajoutez votre logique ici pour stopper les processus (si nécessaire).
    # Exemple : arrêtez un serveur ou un processus Flask.
    # Popen(["taskkill", "/F", "/IM", "flask.exe"], stdout=PIPE, stderr=PIPE)

# Étape 2 : Supprimer et recréer bitcoin_data.xlsx
def recreate_bitcoin_data():
    print("Recreating bitcoin_data.xlsx...")
    # Supprimer le fichier existant
    if os.path.exists("bitcoin_data.xlsx"):
        os.remove("bitcoin_data.xlsx")
        print("Deleted old bitcoin_data.xlsx")
    else:
        print("bitcoin_data.xlsx does not exist")

    # Faire un appel à l'API pour regénérer le fichier
    try:
        response = requests.get("http://127.0.0.1:5000/api/bitcoin-data")  # Remplacez par l'URL correcte
        if response.status_code == 200:
            print("Successfully called BitcoinDataAPI")
        else:
            print(f"API call failed with status code: {response.status_code}")
    except Exception as e:
        print(f"Error while calling the API: {e}")

# Étape 3 : Supprimer et regénérer logistic_regression_model.pkl
def regenerate_model():
    print("Regenerating logistic_regression_model.pkl...")
    # Supprimer le fichier existant
    if os.path.exists("logistic_regression_model.pkl"):
        os.remove("logistic_regression_model.pkl")
        print("Deleted old logistic_regression_model.pkl")
    else:
        print("logistic_regression_model.pkl does not exist")

    # Exécuter train.py pour regénérer le modèle
    try:
        process = Popen(["python", "train.py"], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            print("train.py executed successfully")
        else:
            print(f"train.py failed with error: {stderr.decode()}")
    except Exception as e:
        print(f"Error while executing train.py: {e}")

# Planifier les tâches


# Planification à 11:00 chaque jour
# schedule.every().day.at("11:00").do(daily_tasks)

# # Boucle infinie pour exécuter la tâche planifiée
# if __name__ == "__main__":
#     print("Task scheduler is running...")
#     while True:
#         schedule.run_pending()
#         time.sleep(1)
