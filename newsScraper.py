from openai import OpenAI
import os,re
import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd
import datetime,json,yfinance as yf
import newsScraperIndia,log,db,time
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

news_sources = {
    
    "Japan": {
        "Nikkei Asia": {"url": "https://asia.nikkei.com/", "tag": "h3", "class": "nui-hed"},
        "Japan Times": {"url": "https://www.japantimes.co.jp/news_category/business/", "tag": "h2", "class": "entry-title"},
        "NHK World": {"url": "https://www3.nhk.or.jp/nhkworld/en/news/", "tag": "h2", "class": "news-title"},
        "Mainichi Shimbun": {"url": "https://mainichi.jp/english", "tag": "h2", "class": "main-title"},
    },
    "China": {
        "SCMP": {"url": "https://www.scmp.com/business", "tag": "h2", "class": "article__title"},
        "Caixin": {"url": "https://www.caixinglobal.com/markets/", "tag": "h4", "class": "feed-card-title"},
        "Global Times": {"url": "https://www.globaltimes.cn/business/", "tag": "h3", "class": "title"},
        "China Daily": {"url": "https://www.chinadaily.com.cn/business", "tag": "h3", "class": "news-title"},
        "Xinhua": {"url": "http://www.xinhuanet.com/english/business/", "tag": "div", "class": "xin-title"},
    },
    "India": {
        "Economic Times": {"url": "https://economictimes.indiatimes.com/markets", "tag": "h3", "class": "eachStory"},
        "Moneycontrol": {"url": "https://www.moneycontrol.com/news/business/", "tag": "h2", "class": "clearfix"},
        "Business Standard": {"url": "https://www.business-standard.com/markets", "tag": "h2", "class": "headline"},
        "LiveMint": {"url": "https://www.livemint.com/market", "tag": "h3", "class": "headline"},
        "The Hindu Business": {"url": "https://www.thehindubusinessline.com/markets", "tag": "h3", "class": "story-title"},
    }
}
news_data = {}
def scrape_usa_with_api():

    # API Keys (Replace with your own)
    NEWS_API_KEY = os.geenv("NEWS_API_KEY")
    


    try:
        DJI = yf.Search("^DJI", news_count=10).news
        news=[]
        for article in DJI:
            summary = ''
            if 'summary' in article : 
                summary = article['summary']
            news.append( {'title': article['title'], 
                'description':summary,
                'date':datetime.datetime.fromtimestamp(article['providerPublishTime']).strftime('%Y-%m-%d'), 
                'source': 'Yahoo Finance' } )
        print(news) 
        news_data["USA"] = news
        fed_news =[]
        fed = yf.Search("FED", news_count=10).news
        for article in fed:
            fed_news.append({'title': article['title'], 
                    'date':datetime.datetime.fromtimestamp(article['providerPublishTime']).strftime('%Y-%m-%d'),
                    'source': 'Yahoo Finance' })
        news_data["USA_Fed"] = fed_news

        url= f"https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey={NEWS_API_KEY}"
        
        try:
            response = requests.get(url)
            data = response.json()
            if "articles" in data:
                for article in data["articles"]:
                    news_data["USA"].append({'title': article["title"], 
                                            'description':article["description"], 
                                            'source':article["source"] 
                                            })
                

        except Exception as e:
            log.error(f"Error fetching NEWS API  news: {e}")
    except Exception as e:
        log.error(f"Error while collecting news sentiment{e}")
    return news_data

def extract(text):
    pattern = r'<JSON>(.*?)</JSON>'
    match = re.search(pattern, text, re.DOTALL)

    if match:
        return match.group(1)
    log.error ( f"Error. LLM did not return <JSON></JSON> tag for parsing{text}")
    return -1

def extract_sentiment(summary):
    text = extract(summary)
    if(text ==-1):
        log.error("UNable to parse news ummary json from - returned LLM -1")
        return -1
    json_result = json.loads(text)
    print(json_result)
   # db.update_fii_dii_sentiment(json_result, currdate)
    return json_result

#df.to_csv("market_sentiment.csv", index=False)


def fetch_news_summary_from_open_ai(events, sentiment_update_window =30):
    """Scrape news and summarize using ChatGPT API."""

    if(db.check_last_sentiment_retrieval_within_minutes(sentiment_update_window)):
         
        json_sentiment= db.get_latest_sentiment_records()
        return json_sentiment
    scrape_usa_with_api()
    news_data["India"] = newsScraperIndia.scrape_moneycontrol_news_India()
    news_data["economicTimesIndia"] = newsScraperIndia.scrape_economic()
    
    usa_json_format = '''<JSON>{
                        
                        "USA_market_sentiment": values between -1 to 1. p-1 being overly positive and can be used and can be used by trading bot to buy NIFTY Ce or indian stocks. -1 being overly negative and can be used by trading bot for buying PE or shorting indian stocks. Use the news and events to calcualte this,
                        "USA_market_news_summary": Use the news and events given and summarize in 100-200 words,  
                        }</JSON>'''
    
    india_json_format = '''<JSON>{
                        "Indian_market_sentiment": values between -1 to 1. p-1 being overly positive and can be used and can be used by trading bot to buy NIFTY Ce or indian stocks. -1 being overly negative and can be used by trading bot for buying PE or shorting indian stocks. Use the news and events to calcualte this,
                        "Indian_market_news_summary": Use the news given and summarize in 100-200 words,    
                        
                        "VERDICT_BUY": Accepted response. 'PE' or 'CE'.Based on news today should i buy NIFTY PE or CE in market for intraday
                        }</JSON>
                        '''

    global_json_format = '''
                        <JSON>{
                        "Global_market_sentiment": values between -1 to 1. p-1 being overly positive and can be used and can be used by trading bot to buy NIFTY Ce or indian stocks. -1 being overly negative and can be used by trading bot for buying PE or shorting indian stocks. Use the news and events to calcualte this,
                        "Global_market_news_summary": Use the news given and summarize in 100-200 words,    
                        }</JSON>      
    '''

    usa_prompt = f"""Summarize the following news and provide a JSON as response :
                 {usa_json_format}\n 
                USA NEWS:\n{news_data["USA"]}\n
                FED news: \n{news_data["USA_Fed"]}
                Events Data of the week from today for next 7 days:{events}
                Use only the provided data. Give json in the JSON format provided earlier. 
                Use only the provided news data and events data to caculate sentiment and creating buy PE Ce signal and summary. donot repeat back news or evernts in response.
                   
                the response should be json format  and has to be enclosed with tags <JSON></JSON>
    """
    india_prompt = f"""Summarize the following news and provide a JSON as response  :
                 {india_json_format}\n 
                India NEWS:\n{news_data["India"]}\n
                Economic Times India:\n{news_data["economicTimesIndia"]}
                
                Use only the provided news data and events data to caculate sentiment and creating buy PE Ce signal and summary. donot repeat back news or evernts in response.
                Give json in the JSON format provided earlier.    
                the response should be json format and has to be enclosed with tags <JSON></JSON>
    """

    global_prompt = f"""Summarize the following news and provide a JSON as response  :
                 {global_json_format}\n 
                Economic Times India:\n{news_data["economicTimesIndia"]}
                
                Use only the provided data. Give json in the JSON format provided earlier.    
                the response should be json format and has to be enclosed with tags <JSON></JSON>
    """
    client = OpenAI(api_key = OPENAI_API_KEY)
    # Get responses from ChatGPT for each prompt
    usa_response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": usa_prompt}]
    )
    time.sleep(60)  # 60 seconds = 1 minutes
    india_response = client.chat.completions.create(
        model="gpt-4", 
        messages=[{"role": "system", "content": india_prompt}]
    )
    time.sleep(60)  # 60 seconds = 1 minutes
    global_response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": global_prompt}]
    )

    # Extract summaries
    usa_summary = usa_response.choices[0].message.content
    india_summary = india_response.choices[0].message.content
    global_summary = global_response.choices[0].message.content

    # Extract sentiments for each
    usa_sentiment = extract_sentiment(usa_summary)
    india_sentiment = extract_sentiment(india_summary)
    global_sentiment = extract_sentiment(global_summary)

    # Combine sentiments into JSON
    sentiment_json = {
        "usa_sentiment": usa_sentiment,
        "india_sentiment": india_sentiment,
        "global_sentiment": global_sentiment
    }
    usa_sentiment = sentiment_json['usa_sentiment']['USA_market_sentiment']
    usa_summary = sentiment_json['usa_sentiment']['USA_market_news_summary']

    indian_sentiment = sentiment_json['india_sentiment']['Indian_market_sentiment']
    indian_summary = sentiment_json['india_sentiment']['Indian_market_news_summary']
    verdict_buy = 'PE' if sentiment_json['india_sentiment']['VERDICT_BUY'] == 'PE' else 'CE'

    global_sentiment = sentiment_json['global_sentiment']['Global_market_sentiment']
    global_summary = sentiment_json['global_sentiment']['Global_market_news_summary']
    db.insert_sentiment_record( usa_sentiment, usa_summary, indian_sentiment, indian_summary, 
                          verdict_buy, global_sentiment, global_summary)

    sentiment_json_unwrapped = { 
            "usa_sentiment" : usa_sentiment,
            "usa_summary" : usa_summary,
            "indian_sentiment" : indian_sentiment,
            "indian_summary" : verdict_buy,
            "verdict_buy" : verdict_buy,
            "global_sentiment" : global_sentiment,
            "global_summary" : global_summary,
        }
    return sentiment_json_unwrapped