import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

# Étape 1 : Charger les données depuis le fichier Excel
def load_data(file_path):
    """
    Charge un fichier Excel et affiche les colonnes pour vérification.
    """
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        print("Colonnes dans le fichier :", df.columns)  # Debugging pour vérifier les colonnes
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"Le fichier {file_path} est introuvable.")
    except Exception as e:
        raise Exception(f"Une erreur s'est produite lors de chargement des données : {e}")

# Étape 2 : Préparer les données pour l'entraînement
def prepare_data(df):
    """
    Prépare les données pour l'entraînement en :
    - Créant une colonne 'price_increase' à partir de 'change_percent_24hr'.
    - Gérant les valeurs manquantes et en standardisant les données.
    """
    try:
        # Vérification de la présence de la colonne cible
        if 'change_percent_24hr' not in df.columns:
            raise KeyError("'change_percent_24hr' column not found in the data.")

        # Créer la colonne cible
        df['price_increase'] = df['change_percent_24hr'].apply(lambda x: 1 if x > 0 else 0)

        # Sélectionner les colonnes pour les features
        features = ['price_usd', 'market_cap_usd', 'volume_usd_24hr', 'vwap_24hr', 'sentiment']
        if not all(feature in df.columns for feature in features):
            missing = [f for f in features if f not in df.columns]
            raise KeyError(f"Les colonnes suivantes sont manquantes dans les données : {missing}")

        X = df[features]
        y = df['price_increase']

        # Remplir les valeurs manquantes
        imputer = SimpleImputer(strategy='mean')
        X = pd.DataFrame(imputer.fit_transform(X), columns=features)

        # Standardiser les données
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        return X_scaled, y
    except Exception as e:
        raise Exception(f"Erreur lors de la préparation des données : {e}")

# Étape 3 : Entraîner et sauvegarder le modèle
def train_and_save_model(X, y, model_filename="logistic_regression_model_with_sentiment.pkl"):
    """
    Entraîne un modèle de régression logistique et le sauvegarde en fichier pickle (.pkl).
    """
    try:
        # Diviser les données en ensembles d'entraînement et de test
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Créer et entraîner le modèle
        model = LogisticRegression()
        model.fit(X_train, y_train)

        # Sauvegarder le modèle
        with open(model_filename, 'wb') as f:
            pickle.dump(model, f)
        print(f"Modèle sauvegardé sous {model_filename}")

        # Évaluer le modèle
        y_pred = model.predict(X_test)
        print(f"Précision : {accuracy_score(y_test, y_pred)}")
        print("Rapport de classification :")
        print(classification_report(y_test, y_pred))
    except Exception as e:
        raise Exception(f"Erreur lors de l'entraînement ou de la sauvegarde du modèle : {e}")

# Fonction principale
if __name__ == "__main__":
    try:
        # Chemin vers le fichier Excel
        file_path = "bitcoin_data.xlsx"  # Remplacez par votre chemin exact

        # Charger les données
        df = load_data(file_path)

        # Préparer les données
        X, y = prepare_data(df)

        # Entraîner et sauvegarder le modèle
        train_and_save_model(X, y)

    except FileNotFoundError as e:
        print(f"Erreur : {e}")
    except KeyError as e:
        print(f"Erreur : {e}")
    except Exception as e:
        print(f"Une erreur inattendue s'est produite : {e}")
