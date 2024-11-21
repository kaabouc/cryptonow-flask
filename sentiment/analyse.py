import pandas as pd
import nltk
import os

# Téléchargement explicite des ressources NLTK
try:
    nltk.download('vader_lexicon', quiet=False)
except Exception as e:
    print(f"Erreur lors du téléchargement du lexique VADER : {e}")

from nltk.sentiment import SentimentIntensityAnalyzer

def analyze_bitcoin_comments_sentiment(file_path):
    """
    Analyse le sentiment des commentaires à partir d'un fichier CSV
    
    Parameters:
    file_path (str): Chemin vers le fichier CSV contenant les commentaires
    
    Returns:
    dict: Statistiques de sentiment et DataFrame avec scores de sentiment
    """
    # Charger le fichier CSV
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except Exception as e:
        print(f"Erreur de chargement du fichier : {e}")
        return f"Erreur de chargement du fichier : {e}"
    
    # Utiliser la colonne 'Comment' exactement
    comment_column = 'Comment'
    
    # Initialiser l'analyseur de sentiment
    sia = SentimentIntensityAnalyzer()
    
    # Fonction pour calculer le sentiment
    def get_sentiment_score(text):
        if pd.isna(text):
            return 0
        return sia.polarity_scores(str(text))['compound']
    
    # Ajouter une colonne avec les scores de sentiment
    df['sentiment_score'] = df[comment_column].apply(get_sentiment_score)
    
    # Catégoriser les sentiments
    def categorize_sentiment(score):
        if score > 0.05:
            return 'Positif'
        elif score < -0.05:
            return 'Négatif'
        else:
            return 'Neutre'
    
    df['sentiment_category'] = df['sentiment_score'].apply(categorize_sentiment)
    
    # Calculer les statistiques de sentiment
    sentiment_stats = {
        'total_comments': len(df),
        'sentiment_breakdown': df['sentiment_category'].value_counts(normalize=True) * 100,
        'average_sentiment_score': df['sentiment_score'].mean(),
        'median_sentiment_score': df['sentiment_score'].median()
    }
    
    # Afficher un résumé détaillé
    print("\n--- Résumé de l'analyse de sentiment ---")
    print(f"Nombre total de commentaires : {sentiment_stats['total_comments']}")
    print("\nRépartition des sentiments:")
    for category, percentage in sentiment_stats['sentiment_breakdown'].items():
        print(f"{category}: {percentage:.2f}%")
    print(f"\nScore de sentiment moyen : {sentiment_stats['average_sentiment_score']:.4f}")
    print(f"Score de sentiment médian : {sentiment_stats['median_sentiment_score']:.4f}")
    
    # Commentaires les plus positifs et négatifs
    print("\n5 commentaires les plus positifs:")
    print(df.nlargest(5, 'sentiment_score')[[comment_column, 'sentiment_score', 'sentiment_category']])
    
    print("\n5 commentaires les plus négatifs:")
    print(df.nsmallest(5, 'sentiment_score')[[comment_column, 'sentiment_score', 'sentiment_category']])
    
    # Visualisation graphique des sentiments
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(10, 6))
    sentiment_breakdown = df['sentiment_category'].value_counts()
    plt.pie(sentiment_breakdown, labels=sentiment_breakdown.index, autopct='%1.1f%%')
    plt.title('Répartition des sentiments sur les commentaires Bitcoin')
    plt.savefig('sentiment_pie_chart.png')
    plt.close()
    
    return {
        'dataframe': df,
        'stats': sentiment_stats
    }

# Exemple d'utilisation
result = analyze_bitcoin_comments_sentiment('tradingview_comments_all.csv')

# Sauvegarde des résultats dans un fichier CSV
result['dataframe'][['Comment', 'sentiment_score', 'sentiment_category']].to_csv('bitcoin_sentiment_results.csv', index=False)
print("\nRésultats détaillés sauvegardés dans 'bitcoin_sentiment_results.csv'")
print("Graphique de répartition des sentiments sauvegardé dans 'sentiment_pie_chart.png'")