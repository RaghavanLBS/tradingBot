
import numpy as np
from scipy.stats import linregress
import db,datetime


def update_sentiment():
    """Perform sentiment analysis and update database."""
   
    last_date = db.last_sentiment_fetched_date()
    if last_date and datetime.strptime(last_date, "%Y-%m-%d") >= datetime.today() - datetime.timedelta(hours=1):
        print("Using cached sentiment data.")
        return

    print("Fetching fresh sentiment data...")

    # Fetch news sentiment
    sentiment_score = get_news_sentiment()  # Function to scrape & analyze news

    today = datetime.today().strftime("%Y-%m-%d")
    db.update_sentiment(today, sentiment_score)
    

def compute_final_sentiment():
    """Combines GPT sentiment (60%) and code-generated sentiment (40%)"""
    
    gpt_sentiment, news_summary = fetch_news_summary()
    code_sentiment = compute_market_sentiment()  # Our previous method
    
    final_sentiment = (gpt_sentiment * 0.6) + (code_sentiment * 0.4)
    
    return final_sentiment, news_summary