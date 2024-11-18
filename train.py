import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler

# Step 1: Load the Excel file
def load_data(file_path):
    # Lire le fichier Excel
    df = pd.read_excel(file_path, engine='openpyxl')
    
    # Debug : Afficher les colonnes pour vérifier leur exactitude
    print("Colonnes dans le fichier :", df.columns)
    
    return df

# Step 2: Préparer les données pour la régression logistique
def prepare_data(df):
    # Vérifier si la colonne 'change_percent_24hr' existe
    if 'change_percent_24hr' in df.columns:
        df['price_increase'] = df['change_percent_24hr'].apply(lambda x: 1 if x > 0 else 0)
    else:
        raise KeyError("'change_percent_24hr' column not found in the data.")
    
    # Sélectionner les features
    features = ['price_usd', 'market_cap_usd', 'volume_usd_24hr', 'vwap_24hr']  
    X = df[features]
    y = df['price_increase']
    
    # Standardiser les données
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return X_scaled, y

# Step 3: Entraîner le modèle de régression logistique et le sauvegarder en .pkl
def train_and_save_model(X, y, model_filename="logistic_regression_model.pkl"):
    # Diviser les données en ensembles d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Créer et entraîner le modèle de régression logistique
    model = LogisticRegression()
    model.fit(X_train, y_train)
    
    # Sauvegarder le modèle entraîné au format .pkl
    with open(model_filename, 'wb') as f:
        pickle.dump(model, f)
    print(f"Modèle sauvegardé sous {model_filename}")
    
    # Faire des prédictions et évaluer le modèle
    y_pred = model.predict(X_test)
    print(f"Précision : {accuracy_score(y_test, y_pred)}")
    print("Rapport de classification :")
    print(classification_report(y_test, y_pred))

# Fonction principale
if __name__ == "__main__":
    try:
        # Charger les données depuis le fichier Excel
        df = load_data("bitcoin_data.xlsx")  # Remplacez par votre chemin
        
        # Préparer les données
        X, y = prepare_data(df)
        
        # Entraîner le modèle et sauvegarder
        train_and_save_model(X, y)
    except KeyError as e:
        print(f"Erreur : {e}")
