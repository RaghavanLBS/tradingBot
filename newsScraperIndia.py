import requests,datetime,json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import log


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://google.com",
    "CallTreeId": "||BTOC-1BF47A0C-CCDD-47BB-A9DA-592009B5FB38",
    "Content-Type": "application/json; charset=UTF-8",
    "x-timeout-ms": "5000",
    "DNT": "1",
    "Connection": "keep-alive",
    
}
url= "https://www.moneycontrol.com/"

def strip_tab_nextLine(str):
    return str.replace('\t','').replace('\n','').replace('"','\'')


# Function to scrape headlines from a given URL
def scrape_moneycontrol_news_India():
    try:
        print('Scrapping Moneycontrol News:\n')
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch {url}")
            log.error(f"Moneycontrol Scraping with response code: {response.status_code}")
            return []
        news = []

        soup = BeautifulSoup(response.text, 'html.parser')

        news.append({
            'title': strip_tab_nextLine(soup.find('h3').text),
            'source': 'moneycontrol.com',
            'date': datetime.datetime.today().strftime('%Y-%m-%d')
        })

        for x in soup.select('div.list_sepbx a'):
            news.append({
                'title': strip_tab_nextLine(x.text),
                'source': 'moneycontrol.com',
                'date': datetime.datetime.today().strftime('%Y-%m-%d')
            })

        for x in soup.select('div.ltsnewsbx a'):
            news.append({
                'title': strip_tab_nextLine(x.text),
                'source': 'moneycontrol.com',
                'date': datetime.datetime.today().strftime('%Y-%m-%d')
            })
        if(len(news) ==0 ):
            log.error("MOneycontrol  parsing failed. Most likely div.list_sepbx div.ltsnewsbx tags changed.")
        else:
            log.info("Successfully parsed MoneyControl")      
        return news
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        log.error(f"Moneycontrol Scraping failed: {e}")
        return []

def scrape_economic():
    url= "https://economictimes.indiatimes.com/"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch {url}")
            log.error(f"Economic Times scraping Failed - response status code - {response.status_code}")
            return []
        news = []

        soup = BeautifulSoup(response.text, 'html.parser')
        for x in soup.select('.newsList li a'):
            news.append({
            'title': x.text,
            'source': 'economictimes.indiatimes.com',
            'date': datetime.datetime.today().strftime('%Y-%m-%d')
            })
        if(len(news) ==0 ):
            log.error("Economic Times parsing failed. Most likely .newsList li a tags changed.")
        else:
            log.info("Successfully parsed Economic Times")       
        return news
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

