import requests
from bs4 import BeautifulSoup
import pandas as pd

# Base URL and pagination suffix
base_url = "https://www.abcbourse.com/forums/bitcoin_10447"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# Function to scrape a single page
def scrape_page(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        comments_elements = soup.find_all("a", class_="lfor")
        comments = [comment.text.strip() for comment in comments_elements]
        return comments
    else:
        print(f"Erreur : Impossible d'accéder à {url} (status code : {response.status_code}).")
        return []

# Iterate over all pages (adjust the range as needed)
all_comments = []
for page_num in range(1, 11):  # Adjust the range for the number of pages you want to scrape
    page_url = f"{base_url}?p={page_num}"
    print(f"Scraping {page_url}...")
    comments = scrape_page(page_url)
    all_comments.extend(comments)

# Save comments to CSV
if all_comments:
    df = pd.DataFrame(all_comments, columns=["Comment"])
    df.to_csv("tradingview_comments_all.csv", index=False, encoding="utf-8")
    print("Les commentaires de toutes les pages ont été sauvegardés dans 'tradingview_comments_all.csv'.")
else:
    print("Aucun commentaire n'a été extrait.")
