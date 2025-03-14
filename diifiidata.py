import db,datetime,requests,imageScraper,log
import requests, pandas as pd

import requests,re,json,yaml,gptConnector
from pathlib import Path


with open("tradingBot\config.yaml") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        log.error(f"Error while loading yaml",{exc})


headers = {
        "user-agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.0.3705;)"
    }
# Example usage
mistral_api_key = "5ZXnnmlUSlQj0dhaaVVR8F1MJSK68zn8"


def extract(text):
    pattern = r'<JSON>(.*?)</JSON>'
    match = re.search(pattern, text, re.DOTALL)

    if match:
        return match.group(1)
    log.error ( f"Error. LLM did not return <JSON></JSON> tag for parsing{text}")
    return -1

def extract_from_image(image_path,content):
    log.info("Extracting FII DII data from screenshot")
    fii_dii = gptConnector.extract_details_from_image(mistral_api_key, image_path,  content)
    extractedJSONStr  = extract(fii_dii) 
    if(extractedJSONStr!=-1):     
        json_result = json.loads(extractedJSONStr)
        log.info("Successfully parsed FII DII from trendlyne")
        return json_result
    log.error ( f"Error reading image into json for fii_dii data from trendlyne - check for changes")
    return -1


def update_fii_dii():
    """Fetch new FII/DII data only if outdated."""
    last_date = db.last_fetched_fii_dii_from_db()
    if last_date and last_date.strftime("%Y-%m-%d") >= (datetime.datetime.today() - datetime.timedelta(hours=48)).strftime("%Y-%m-%d"):
        print("Using cached FII/DII data.")
        log.info("Using cached FII/DII data.")
        return

    print("Fetching fresh FII/DII data...")
    log.info("Fetching fresh FII/DII data...")
    yesterday = datetime.datetime.now() - datetime.timedelta(days=2)
    date = yesterday.strftime("%Y-%m-%d")  
    imageScraper.createScreenshot_and_get_fii_data(config['NSE_FII_DII_URL'])
    """
    content_fii_dii = f'''Find values of fii_equity, fii_debt,fii_derivatives,
                                fii_total,mf_total,mf_derivatives,mf_debt,mf_equity for date {date} 
                                from the image and give it as JSON so i can use it in code. 
                                enclose the json in between the tags  <JSON></JSON>
                                '''"
    """
    content_fii_dii = f'''Find values of fii_gross_purchase, fii_gross_sales,fii_net_purchase,
                                dii_net_purchase,dii_gross_sales,dii_gross_purchase for date from {last_date} till today
                                from the image and give it as JSON so i can use it in code. 
                                enclose the json in between the tags  <JSON></JSON>
                                '''
    my_file = Path( config['image_path_fii_dii'])
    if my_file.is_file() == False:
        log.error('Screenshot for image_path_fii_dii from Trendlyne failed')
    # Fetch new data
    else:
        json_data = extract_from_image(config['image_path_fii_dii'],  content_fii_dii)
        if(json_data ==-1):
            log.error("Error JSON parsing content_fii_dii")
        else:
            for i  in json_data:
                db.create_fii_dii_data(json_data[i],i)
        
            
        
    content_fii_equity = f'''Find values of equity_gross_purchase, equity_gross_sales,equity_net,
                                debt_gross_sales,debt_gross_purchase for date from {last_date} till today
                                from the image and give it as JSON so i can use it in code. 
                                enclose the json in between the tags  <JSON></JSON>
                                '''
    my_file = Path( config['image_path_fii'])
    if my_file.is_file() == False:
        log.error('Screenshot for image_path_fii from Trendlyne failed')
    # Fetch new data
    else:
        json_data_equity = extract_from_image(config['image_path_fii'],  content_fii_equity)
        if(json_data_equity !=-1):
            
            for i  in json_data_equity:
                db.create_fii_equity_data(json_data_equity[i],i)
        else:
            log.error("Error JSON parsing content_fii_equity")
    

def get_fii_dii_sentiment():    
    currdate = datetime.datetime.today().strftime("%Y-%m-%d")
    date = db.last_fetched_update_fii_dii_sentiment()
    if(date is not None and date.strftime("%Y-%m-%d") == currdate):
       df_json = db.get_fii_dii_sentiment_summary(currdate)
       return df_json
    log.info("fetching dii fii sentiment summary from db")
    data = db.fetch_fii_dii_sentiment_from_db()
    data_last_3_months_sentiment = db.fetch_fii_dii_last3_months_from_db()
    
    currdate = datetime.datetime.today().strftime("%Y-%b-%d")
    my_file = Path( f'nifty\\5-day_nifty-{currdate}.png')
    if my_file.is_file() == False:
        my_file = imageScraper.create5dayScreenshotforNifty(currdate)
        if my_file.is_file() == False:
            log.error("Error creating screenshot for 5-day_nifty")
            return -1

    data_json = data.to_json(orient='records')
    data_json_3 = data_last_3_months_sentiment.to_json(orient='records')
    json_format = '{"long_term_fii_sentiment":"", "short_term_fii_sentiment":"", ' \
                    '"long_term_dii_sentiment":"", "short_term_dii_sentiment":"",' \
                    '"fii_sentiment_summary":"", "dii_sentiment_summary":"",' \
                    '"buy_CE_next_trading_day_based_on_FII":"", "buy_PE_next_trading_day_based_on_FII":"",' \
                    '"buy_CE_next_trading_day_based_on_DII":"", "buy_PE_next_trading_day_based_on_DII":"",' \
                    '"FII_Sentiment_weightage_based_ON_NIFTY_image":"","DII_Sentiment_weightage_based_ON_NIFTY_image":""}'
    sample_json = '<JSON>{"long_term_fii_sentiment":"positive", "short_term_fii_sentiment":"negative", ' \
                    '"long_term_dii_sentiment":"negative", "short_term_dii_sentiment":"negative",' \
                    '"fii_sentiment_summary":"FII are buying for past 5 months.But selling in past 6 days. SO proceed with caution to buy CE just based on this signal ", ' \
                    '"dii_sentiment_summary":"DII are selling for past 5 months.Also selling in past 6 days. This will affect market and just based on DII CE is not a buy for next few days",' \
                    '"buy_CE_next_trading_day_based_on_FII":"NO", "buy_PE_next_trading_day_based_on_FII":"NO",' \
                    '"buy_CE_next_trading_day_based_on_DII":"NO", "buy_PE_next_trading_day_based_on_DII":"YES",' \
                    '"FII_Sentiment_weightage_based_ON_NIFTY_image":"0.3", "DII_Sentiment_weightage_based_ON_NIFTY_image":"0.7"}' \
                    '</JSON>'

    sentiment_fii_dii = f''' You are market analyst. Can you analyse the DII and FII sales in Indian market given here below for past 30 days . 
                            Correlate with last 3 month fii net sell off.
                            Also i am providing you with image of nifty for past 5 days. 
                            Correlate nifty graph with FII sell off in past 6 days and extract sentiment summary in following JSON format: {json_format}
                            When answering variable buy_ce_next_trading_day or buy_pe_next_trading_day 
                            make sure you consider only given data - correlate nifty image in past 5 days superimpose on dii and fii sentiment past 6 days 
                            and assume that you are day trader and answer. 
                            Donot hallucinate . Donot return anything other than requested json format.
                           enclose the json response in between the tags  <JSON></JSON>
                            30 day FII DII sale purchase details in this JSON : {data_json}
                            last 3 months FII DII sale purchase details in this JSON : {data_json_3}
                            
                            Example response: 
                            {sample_json}
                            

                        '''
    log.info("calling GPT to extract summary")
    fii_dii_sentiment = gptConnector.extract_details_from_image_openai(my_file,  sentiment_fii_dii)
    extractedJSONStr  = extract(fii_dii_sentiment) 
    if(extractedJSONStr!=-1):     
        json_result = json.loads(extractedJSONStr)
        print(json_result)
        db.update_fii_dii_sentiment(json_result, currdate)
        return json_result
    else:
        log.error("Error extracting json details from image for fii_dii_sentiment summary")
        return -1
