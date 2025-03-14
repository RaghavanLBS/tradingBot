import requests,datetime,log, pandas as pd



def get_realtime_nifty():
    
    """Fetch real-time Nifty 50 intraday price data"""
   # Yahoo Finance API for Intraday Data
    NIFTY_TICKER = "^NSEI"
    INTERVAL = "5m"  # 1-minute interval for real-time updates
    LOOKBACK_PERIOD = 100  # Number of historical data points to fetch
    base_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{NIFTY_TICKER}"
    params = {
        "interval": INTERVAL,
        "range": "1d",
    }
    headers = {
        "user-agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.0.3705;)"
    }
    response = requests.get(base_url, params=params, headers = headers)
    
    if response.status_code == 200:
        data = response.json()
        timestamps = data['chart']['result'][0]['timestamp']
        prices = data['chart']['result'][0]['indicators']['quote'][0]['close']

        df = pd.DataFrame({
            "Date": [datetime.datetime.fromtimestamp(t) for t in timestamps],
            "Close": prices
        })
        log.info(f" Successfully scraped NIFTY from Yahoo finance")
        return df
    else:
        log.error(f"❌ Failed to fetch real-time data {response.status_code}")
        return None



def get_realtime_BEL_price():
    
    """Fetch real-time Nifty 50 intraday price data"""
   # Yahoo Finance API for Intraday Data
    NIFTY_TICKER = "BEL.NS"
    INTERVAL = "1m"  # 1-minute interval for real-time updates
    LOOKBACK_PERIOD = 100  # Number of historical data points to fetch
    base_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{NIFTY_TICKER}"
    params={}
    headers = {
        "user-agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.0.3705;)"
    }
    response = requests.get(base_url, params=params, headers = headers)
    
    if response.status_code == 200:
        data = response.json()
        meta_json  = data['chart']['result'][0]['meta']
        percent_up = 100*(  meta_json['regularMarketPrice'] - meta_json['previousClose'])/meta_json['previousClose']
        bel_data = {
            'current_price': meta_json['regularMarketPrice'],
            'current_market_high' : meta_json['regularMarketDayHigh'],
            'current_market_low' : meta_json['regularMarketDayLow'],
            'previous_close': meta_json['previousClose'],
            'percent_up_or_down': percent_up
            }
        log.info(f" Successfully scraped BEL from Yahoo finance")
        return bel_data
    else:
        log.error(f"❌ Failed to fetch real-time data {response.status_code}")
        return None
