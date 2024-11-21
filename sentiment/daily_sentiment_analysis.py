import requests
from bs4 import BeautifulSoup
import pandas as pd
import nltk
import os
from nltk.sentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt

# --- Configurations ---
base_url = "https://www.abcbourse.com/forums/bitcoin_10447"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
output_csv = "tradingview_comments_daily.csv"
result_csv = "bitcoin_sentiment_results.csv"
sentiment_chart = "sentiment_pie_chart.png"

# --- Étape 1 : Scraper les données ---
def scrape_comments():
    all_comments = []
    for page_num in range(1, 11):  # Ajustez le nombre de pages ici
        page_url = f"{base_url}?p={page_num}"
        print(f"Scraping {page_url}...")
        response = requests.get(page_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            comments_elements = soup.find_all("a", class_="lfor")
            comments = [comment.text.strip() for comment in comments_elements]
            all_comments.extend(comments)
        else:
            print(f"Erreur : Impossible d'accéder à {page_url} (status code : {response.status_code}).")
    # Sauvegarde des commentaires dans un CSV
    if all_comments:
        df = pd.DataFrame(all_comments, columns=["Comment"])
        df.to_csv(output_csv, index=False, encoding="utf-8")
        print(f"Les commentaires ont été sauvegardés dans {output_csv}.")
    else:
        print("Aucun commentaire n'a été extrait.")

# --- Étape 2 : Analyse des sentiments ---
def analyze_comments(file_path):
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except Exception as e:
        print(f"Erreur de chargement du fichier : {e}")
        return
    
    sia = SentimentIntensityAnalyzer()

    def get_sentiment_score(text):
        if pd.isna(text):
            return 0
        return sia.polarity_scores(str(text))['compound']

    df['sentiment_score'] = df['Comment'].apply(get_sentiment_score)

    def categorize_sentiment(score):
        if score > 0.05:
            return 'Positif'
        elif score < -0.05:
            return 'Négatif'
        else:
            return 'Neutre'

    df['sentiment_category'] = df['sentiment_score'].apply(categorize_sentiment)

    sentiment_stats = {
        'total_comments': len(df),
        'sentiment_breakdown': df['sentiment_category'].value_counts(normalize=True) * 100,
        'average_sentiment_score': df['sentiment_score'].mean(),
        'median_sentiment_score': df['sentiment_score'].median()
    }

    print("\n--- Résumé de l'analyse de sentiment ---")
    print(sentiment_stats)

    df.to_csv(result_csv, index=False)
    print(f"Résultats détaillés sauvegardés dans {result_csv}.")

    plt.figure(figsize=(10, 6))
    sentiment_breakdown = df['sentiment_category'].value_counts()
    plt.pie(sentiment_breakdown, labels=sentiment_breakdown.index, autopct='%1.1f%%')
    plt.title('Répartition des sentiments sur les commentaires Bitcoin')
    plt.savefig(sentiment_chart)
    print(f"Graphique sauvegardé dans {sentiment_chart}.")

# --- Script principal ---
def main():
    print("Début du scraping...")
    scrape_comments()
    print("Début de l'analyse des sentiments...")
    analyze_comments(output_csv)
    print("Processus terminé.")

if __name__ == "__main__":
    nltk.download('vader_lexicon', quiet=True)  # Téléchargement NLTK
    main()
