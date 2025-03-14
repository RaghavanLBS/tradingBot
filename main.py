import db,time,eventScrapper,newsScraper
import json,datetime,time,log
from generateBuySignal import compute_signal
import diifiidata, imageScraper, market_status,tradingSignal#,sentimentCalculator, ticker, zerodhaConnector
import scrapeGiftNifty
in_trade = False

def startup_tasks(currentdate):
    image_path = imageScraper.create5dayScreenshotforNifty(currentdate.strftime('%Y-%b-%d'))
    diifiidata.update_fii_dii()
    eventsThisWeek =  eventScrapper.get_this_week_events()
    json_data = diifiidata.get_fii_dii_sentiment()
    gift_nifty  = scrapeGiftNifty.get_gift_nifty()

    return eventsThisWeek,json_data,gift_nifty,image_path


def tasks_once_30_minutes(eventsThisWeek, nifty_intraday_image_path):
    sentiment_json = newsScraper.fetch_news_summary_from_open_ai(events= eventsThisWeek)
    
    imageScraper.createScreenshotforIntradayNifty(nifty_intraday_image_path)
    return sentiment_json

def startBot():
    while(True):
       currentdate =  datetime.datetime.today()
       market_opened = market_status.is_market_open()
       
       if market_opened == False:
          log.info(f"Market Closed. I am going to seleep for 1800 seconds - 30 minutes")
          time.sleep(1800)
          continue
       else:
           log.info("We are in the market. Doing Startup tasks")
           eventsThisWeek,json_data, giftNifty,nifty_5_day_image_path = startup_tasks(currentdate)
           
           sentiment_json = None #packed variables retrieved from market sentiment analysis
           in_trade = False
           current_config = {
                "counter" : 0,
                "currentTrade" : {},
                "last_fetch_time" : 0
            }
           with open('main_current_config', 'w') as f:
              json.dump(current_config,f)
           if(market_opened and market_status.is_in_volatile_time(currentdate) ==False):
               time.sleep(300)  # 300 seconds = 5 minutes
           log.info("Volatile Trading over. Looks like we are above 9:45 AM")
           choppy = tradingSignal.check_for_nuetral_market()
           
           while True:
            if in_trade == False:
                with open('main_current_config') as f:
                   current_config = json.load(f)
                currentTime = time.time()
                
                nifty_intraday_image_path  = f'.\\intraday\\nifty-{currentdate.strftime("%Y-%m-%d")}-{current_config["counter"]}.png'
                if(sentiment_json is None or (last_fetch_time - currentTime) > 1800):
                    log.info("30 minutes over after last sentiment calculation. Recalculating and taking intraday screenshot")
                    current_config['counter'] =  f"{int(current_config ['counter']) + 1}"
                    sentiment_json  = tasks_once_30_minutes(eventsThisWeek,  nifty_intraday_image_path)
                    last_fetch_time = time.time()
                    with open('main_current_config', 'w') as f:
                        json.dump(current_config, f)
                log.info("Generating buy signal and sending email...")
                buy = tradingSignal.get_buy_signal(sentiment_json, json_data, nifty_5_day_image_path, nifty_intraday_image_path)
                '''{'CE_BUY_POINT': 22500, 'CE_STOP_LOSS': 22350, 'CE_PROFIT_POINT': 22650, 
                    'CE_OPTION_TO_BUY': '22500 CE',
                    'PE_BUY_POINT': 22300, 'PE_STOP_LOSS': 22450, 
                    'PE_PROFIT_POINT': 22150, 'PE_OPTION_TO_BUY': '22300 PE', 
                    'Preferred_Buying': 'PE'}'''
                if buy==-1:
                   log.info("Sleeping for 5 minutes")
                   time.sleep(300)
                else:
                   log.info("Sleeping for 1 hour")
                   time.sleep(3600)
                
            #else:
              # tradingSignal.get_sell_signal(x, json_data, currentTrade)
           

            if(market_opened == False):
               imageScraper.createScreenshotforIntradayNifty(f'nifty\\{currentdate.strftime("%d-%b-%Y")} nifty.png')
               break
            
        #final_sentiment, news_summary = sentimentCalculator.compute_final_sentiment()
    '''df =ticker.get_realtime_ticker()
    if in_trade:
        exit_signal, reason = tradingSignal.check_exit_signal(df)
        if(exit_signal == True):
            zerodhaConnector.close_trade()

    else:
        buy_signal_ce = tradingSignal.check_entry_signal(df)
        buy_signal_pe = tradingSignal.check_entry_signal(df)
        if(buy_signal_ce == True):
            zerodhaConnector.buyCE()
        elif(buy_signal_pe == True):
            zerodhaConnector.buyPE()
    
    

  '''
    

    


if __name__ =="__main__":
    startBot()