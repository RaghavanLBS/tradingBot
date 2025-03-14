import imageScraper, datetime

def trade():
    curdate = datetime.datetime.today()
    curdates = curdate.strftime("%d-%b-%Y")
    ticker='NASDAQ'
    usDJI_path = imageScraper.create5dayUSDJI(f'usa\\{ticker}-{curdates}.png')
    usDJI_today_path = imageScraper.createIntradayUSDJI(f'usa\\{ticker}-{curdates}-5-day.png')

    list_s = ['NOW:NYSE',
              'AAPL:NASDAQ', 
              'AFRM:NASDAQ', 'AMZN:NASDAQ', 
              'ANET:NYSE', 
              'AVGO:NASDAQ', 
              'BABA:NYSE',
              'BKNG:NASDAQ',
              'CRM:NYSE', 
              'DASH:NASDAQ', 
              'GAP:NYSE', 
              'GOOGL:NASDAQ', 
              'HD:NYSE', 
              'HOOD:nasdaq', 
              'HUBS:nyse', 
              'INOD:nasdaq', 
              'JD:nasdaq', 
              'META:nasdaq', 
              'MSTR:nasdaq', 
              'NET:nyse', 
              'NOW:nyse', 
              'NTNX:nasdaq',
              'NVDA:nasdaq',
              'OKTA:nasdaq',
              'SNOW:nyse', 
              'SOUN:nasdaq','T:nyse',
              'TSLA:nasdaq', 'TWLO:nyse', 'U:NYSE' ]
    for ticker in list_s:
        filename=f'usa\\{ticker.split(":")[0]}-{curdates}.png'
        filename2=f'usa\\{ticker.split(":")[0]}-{curdates}-5-day.png'
        imageScraper.createIntradayTickerScreenshot(ticker, filename)
        imageScraper.create5dayTickerScreenshot (ticker, filename2)


if __name__=="__main__":
    trade()
