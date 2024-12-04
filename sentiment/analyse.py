import pandas as pd
import nltk
import os
import json
import matplotlib.pyplot as plt
from nltk.sentiment import SentimentIntensityAnalyzer

# Téléchargement explicite des ressources NLTK
try:
    nltk.download('vader_lexicon', quiet=True)
except Exception as e:
    print(f"Erreur lors du téléchargement du lexique VADER : {e}")

def analyze_bitcoin_comments_sentiment(file_path, output_json):
    """
    Analyse le sentiment des commentaires, sauvegarde les pourcentages positifs et négatifs,
    et génère un graphique.
    
    Parameters:
    file_path (str): Chemin vers le fichier CSV contenant les commentaires.
    output_json (str): Chemin vers le fichier JSON pour sauvegarder les valeurs.
    
    Returns:
    dict: Résultats de l'analyse, y compris les statistiques et le DataFrame enrichi.
    """
    # Charger le fichier CSV
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except Exception as e:
        print(f"Erreur de chargement du fichier : {e}")
        return None

    # Initialiser l'analyseur de sentiment
    sia = SentimentIntensityAnalyzer()

    # Calculer les scores de sentiment
    def get_sentiment_score(text):
        if pd.isna(text):
            return 0
        return sia.polarity_scores(str(text))['compound']
    
    df['sentiment_score'] = df['Comment'].apply(get_sentiment_score)

    # Catégoriser les sentiments
    def categorize_sentiment(score):
        if score > 0.05:
            return 'Positif'
        elif score < -0.05:
            return 'Négatif'
        else:
            return 'Neutre'
    
    df['sentiment_category'] = df['sentiment_score'].apply(categorize_sentiment)

    # Calcul des pourcentages
    total_comments = len(df)
    sentiment_counts = df['sentiment_category'].value_counts()
    positive_percentage = (sentiment_counts.get('Positif', 0) / total_comments) * 100
    negative_percentage = (sentiment_counts.get('Négatif', 0) / total_comments) * 100

    sentiment_values = {
        "positive_percentage": positive_percentage,
        "negative_percentage": negative_percentage
    }

    # Sauvegarder les valeurs de sentiment dans un fichier JSON
    with open(output_json, 'w') as json_file:
        json.dump(sentiment_values, json_file)

    print(f"Les pourcentages de sentiment ont été sauvegardés dans {output_json}.")

    # Graphique de répartition des sentiments
    plt.figure(figsize=(10, 6))
    sentiment_breakdown = df['sentiment_category'].value_counts()
    plt.pie(sentiment_breakdown, labels=sentiment_breakdown.index, autopct='%1.1f%%', colors=['lightgreen', 'lightcoral', 'gold'])
    plt.title('Répartition des sentiments sur les commentaires Bitcoin')
    plt.savefig('sentiment_pie_chart.png')
    print("Graphique sauvegardé dans 'sentiment_pie_chart.png'")
    plt.close()

    # Retourner les résultats
    return {
        'dataframe': df,
        'stats': {
            'total_comments': total_comments,
            'positive_percentage': positive_percentage,
            'negative_percentage': negative_percentage
        }
    }

# Exemple d'utilisation
if __name__ == "__main__":
    input_csv = 'tradingview_comments_all.csv'  # Remplacez par le chemin réel
    output_json = 'sentiment_values.json'

    # Exécuter l'analyse
    result = analyze_bitcoin_comments_sentiment(input_csv, output_json)

    if result:
        # Sauvegarder les résultats détaillés
        result['dataframe'][['Comment', 'sentiment_score', 'sentiment_category']].to_csv('bitcoin_sentiment_results.csv', index=False)
        print("\nRésultats détaillés sauvegardés dans 'bitcoin_sentiment_results.csv'")
        
        # Afficher les statistiques
        print("\n--- Statistiques de l'analyse ---")
        for key, value in result['stats'].items():
            print(f"{key}: {value}")
