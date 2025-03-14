import requests,log
from bs4 import BeautifulSoup

def get_gift_nifty():
    # URL of the website providing GIFT Nifty data
    url = 'https://www.equitypandit.com/giftnifty/'

    # Send a GET request to the website
    response = requests.get(url)
    response.raise_for_status()  # Check for request errors

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the element containing GIFT Nifty data
    # Note: The actual HTML structure may vary; inspect the webpage to find the correct element
    gift_nifty_data = soup.select('div#Gift_Nifty_Data')

    # Extract and print the data
    if gift_nifty_data:
        text = (soup.select('div#Gift_Nifty_Data')[0]).get_text()
        return text
        
    else:
        print('GIFT Nifty data not found.')
        log.error("Error scraping GIFT nifty")
