import yaml,datetime,str,log,json
import psycopg2, pandas as pd
from psycopg2 import Error

config = {}
with open("tradingBot\config.yaml") as stream:
    try:
        config = yaml.safe_load(stream)
        print(config)
    except yaml.YAMLError as exc:
        log.error(exc)
        print(exc)


def get_conn():
    conn = psycopg2.connect(
        database="TradingBot",
        user="postgres", 
        password="welcome",
        host="localhost",
        port="5432"
    )
    
    print("Connected to PostgreSQL successfully!")

    return conn

def execute_sql_statement(conn, statement):
    try:
        cursor = conn.cursor()
        cursor.execute(statement)
        return cursor
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL:", error)
        log.error(error)
        if conn:
            cursor.close()
            conn.close()
        return -1
   
   
def execute_insert_statement(conn, statement, obj):
    try:
        cursor = conn.cursor()
        cursor.execute(statement, obj)
        return cursor
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL:", error)
        log.error(error)
        if conn:
            cursor.close()
            conn.close()
        return -1
            
def createBuyTrade(obj):
    conn = get_conn()
    execute_sql_statement(conn,"""
        INSERT INTO trades (date, trade_type, entry_reason, fii_value, dii_value, sentiment_score, gpt_sentiment, final_sentiment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (datetime.today().strftime("%Y-%m-%d"), 
          obj.trade_type, obj.entry_reason, 
          obj.fii_weighted, obj.dii_weighted, obj.computed_market_sentiment, 
          obj.gpt_sentiment, obj.final_sentiment))

    

# Run once to initialize the trades database


def last_fetched_update_fii_dii_sentiment():

    # Check latest entry
    log.info('fetching fii dii sentiment')
    conn = get_conn()
    cursor = execute_sql_statement(conn, "SELECT MAX(daily) FROM public.fii_di_sentiment_daily")
    if(cursor == -1):
        log.error("Error fetching last updated dated fii dii sentiment")
        return
    last_date = cursor.fetchone()[0]
    log.info(f"Last date of fii dii sentiment in database:{last_date}")
    cursor.close()
    conn.close()
    return last_date

def get_fii_dii_sentiment_summary(currdate):
    
    log.info("Fetching DII FII sentiment from DB summary")
    conn = get_conn()
    data = execute_sql_statement(conn, "SELECT * FROM fii_di_sentiment_daily ORDER BY daily DESC LIMIT 1")
    if(data ==-1):
        log.error("Unabel to fetch DII FII sentimen db summary")
        return
    
    log.info(f'Successully fetched DII FII sentiment')
    for row in data:
        json_data = {
            f'{str.ltfs}':row[1],
            'short_term_fii_sentiment':row[2],
            'long_term_dii_sentiment': row[3],
            'short_term_dii_sentiment':row[4],
            'dii_sentiment_summary':row[6],
            'fii_sentiment_summary':row[5]


        }
        conn.close()
        return json.dumps(json_data)

def update_fii_dii_sentiment(fii_dii_data, date):
    log.info("Updating FII DII sentiment Data from Database:"+json.dumps(fii_dii_data))
    conn = get_conn()
    ltfs=  fii_dii_data[str.ltfs]
    stfs= fii_dii_data['short_term_fii_sentiment'] 
    ltds= fii_dii_data['long_term_dii_sentiment'] 
    short_term_dii_sentiment=  fii_dii_data['short_term_dii_sentiment'] 
    bcefii= fii_dii_data['buy_CE_next_trading_day_based_on_FII'] 
    bpefii= fii_dii_data['buy_PE_next_trading_day_based_on_FII'] 
    bcedii= fii_dii_data['buy_CE_next_trading_day_based_on_DII'] 
    bpedii= fii_dii_data['buy_PE_next_trading_day_based_on_DII'] 

    fiiweight= float(fii_dii_data['FII_Sentiment_weightage_based_ON_NIFTY_image'])

    diiweight= float(fii_dii_data['DII_Sentiment_weightage_based_ON_NIFTY_image'])
    dss= fii_dii_data['dii_sentiment_summary']
    fii_sentiment_summary= fii_dii_data['fii_sentiment_summary']

    conn = get_conn()
    insert_statement = f'''INSERT INTO public.fii_di_sentiment_daily 
                                   (daily, {str.ltfs}, short_term_fii_sentiment, long_term_dii_sentiment, short_term_dii_sentiment, 
                                   fii_sentiment_summary, dii_sentiment_summary,buy_ce_next_trading_day_based_on_FII,buy_pe_next_trading_day_based_on_FII,
                                   buy_ce_next_trading_day_based_on_DII,buy_pe_next_trading_day_based_on_DII,
                                   FII_Sentiment_weightage_based_ON_NIFTY_image, DII_Sentiment_weightage_based_ON_NIFTY_image)  
                                   VALUES (%s, %s, %s,%s,%s,%s,%s, %s,%s,%s,%s,%s,%s)'''
    obj = (date, ltfs, stfs, ltds, short_term_dii_sentiment, 
           fii_sentiment_summary,dss,bcefii,bpefii,
           bcedii,bpedii,
           fiiweight, diiweight)
                                
    cursor = execute_insert_statement(conn,insert_statement, obj)
    if(cursor == -1):
        print("Unable to insert data into fii_dii_data with latest details")
        log.error("Unable to insert data into fii_dii_data with latest details")
    else:
        conn.commit()
        cursor.close()
        conn.close()
        log.info("Successfully inserted fii dii data")

def fetch_fii_dii_last3_months_from_db():
    log.info("""Fetch the latest FII/DII monthly data from the database.""")
    conn = get_conn()
    data = execute_sql_statement(conn, "SELECT * FROM fii_dii_data_monthly ORDER BY date DESC LIMIT 3")
    if(data == -1):
        log.error("Error fetching last 3 months FII DII Monthly data")
        return
    df = pd.DataFrame(data, columns = ["DATE", "FII Equity", "FII Debt",
                                       "FII Derivatives" ,"FII Total" ,"MF Total" ,
                                       "MF Derivatives" ,"MF Debt" ,"MF Equity" ])
    df = df[['DATE','FII Total', 'MF Total' ]] #= df.apply(lambda r: ['FII Total', 'MF Total' ], axis=1, result_type="expand") 
    log.info('Successfully fetched DII FII Monthly data')
    conn.close()
    return df

#FII DII DATA FUNCTIONS
def fetch_fii_dii_sentiment_from_db():
    log.info("""Fetch the latest FII/DII data from the database.""")
    
    conn = get_conn()
    data = execute_sql_statement(conn, "SELECT * FROM fii_dii_cash_provisional ORDER BY date DESC LIMIT 30")
    if(data ==-1):
        log.error("Unable to fetch FII/DII data from database")
        return -1
    df = pd.DataFrame(data,columns =['date', 'fii_gross_purchase',
                                      'fii_gross_sales', 'fii_net_purchase', 'dii_net_purchase',
                                    'dii_gross_sales', 'dii_gross_purchase'])
    df=df[['date','fii_net_purchase', 'dii_net_purchase']] #= df.apply(lambda r: ['dii_net_purchase', 'fii_net_purchase'], axis=1, result_type="expand") 
    conn.close()
    print(df.head())
    log.error("successfully fetched FII/DII data from database")
    return df
 

def last_fetched_fii_dii_from_db():
    log.error("Fetch max date into fii_dii_data with latest details")
    # Check latest entry
    conn = get_conn()
    cursor = execute_sql_statement(conn, "SELECT MAX(date) FROM public.fii_dii_cash_provisional")
    if(cursor == -1):
        log.error("Unable to fetch max date into fii_dii_data with latest details")
        return -1
    last_date = cursor.fetchone()[0]
    print(last_date)
    log.info("Succeffully fetched max date from fii_dii_data with latest details")
    cursor.close()
    conn.close()
    return last_date


def create_fii_dii_data(fii_dii_data,date):
    log.info('Trying inser fii_dii_cash_provisional')
    fii_gross_purchase= None if fii_dii_data['fii_gross_purchase'] == 'NA' else float(fii_dii_data['fii_gross_purchase'])
    fii_gross_sales= None if fii_dii_data['fii_gross_sales'] == 'NA' else float(fii_dii_data['fii_gross_sales'])
    fii_net_purchase= None if fii_dii_data['fii_net_purchase'] == 'NA' else float(fii_dii_data['fii_net_purchase'])
    dii_net_purchase= None if fii_dii_data['dii_net_purchase'] == 'NA' else float(fii_dii_data['dii_net_purchase'])
    dii_gross_sales= None if fii_dii_data['dii_gross_sales'] == 'NA' else float(fii_dii_data['dii_gross_sales'])
    dii_gross_purchase = None if fii_dii_data['dii_gross_purchase'] == 'NA' else float(fii_dii_data['dii_gross_purchase'])

    conn = get_conn()
    insert_statement = '''INSERT INTO public.fii_dii_cash_provisional 
                                   (date, fii_gross_purchase, fii_gross_sales, dii_net_purchase, fii_net_purchase, dii_gross_sales, dii_gross_purchase)  
                                   VALUES (%s, %s, %s,%s,%s,%s,%s)'''
    obj = (date, fii_gross_purchase, fii_gross_sales, dii_net_purchase, fii_net_purchase, dii_gross_sales, dii_gross_purchase,)
                                
    cursor = execute_insert_statement(conn,insert_statement, obj)
    if(cursor == -1):
        log.error("Unable to insert data into fii_dii_data with latest details")
        return -1
    else:
        conn.commit()
        cursor.close()
        conn.close()
        log.info('Successfully inserted fii_dii_cash_provisional')


def create_fii_equity_data(fii_equity, date):
    log.info('Create FII DII EQUITY DATA')
    equity_gross_purchase= None if fii_equity['equity_gross_purchase'] == 'NA' else float(fii_equity['equity_gross_purchase'])
    equity_gross_sales= None if fii_equity['equity_gross_sales'] == 'NA' else float(fii_equity['equity_gross_sales'])
    equity_net= None if fii_equity['equity_net'] == 'NA' else float(fii_equity['equity_net'])
    debt_gross_sales= None if fii_equity['debt_gross_sales'] == 'NA' else float(fii_equity['debt_gross_sales'])
    debt_gross_purchase= None if fii_equity['debt_gross_purchase'] == 'NA' else float(fii_equity['debt_gross_purchase'])
    

    conn = get_conn()
    insert_statement = '''INSERT INTO public.fii_equity 
                                   (trade_date, equity_gross_purchase, equity_gross_sales, equity_net, debt_gross_sales, debt_gross_purchase)  
                                   VALUES (%s, %s, %s,%s,%s,%s)'''
    obj = (date, equity_gross_purchase, equity_gross_sales, equity_net, debt_gross_sales, debt_gross_purchase)
                                
    cursor = execute_insert_statement(conn,insert_statement, obj)
    if(cursor == -1):
        log.error("Unable to insert data into fii_difii_equityi_data with latest details")
    else:
        conn.commit()
        cursor.close()
        conn.close()
        log.info("Successfully inserted data into dii_fii_equity")


def insert_sentiment_record( usa_sentiment, usa_summary, indian_sentiment, indian_summary, 
                          verdict_buy, global_sentiment, global_summary):
    """Insert a new sentiment record into the sentiment_store table"""
    log.info("Inserting USA,Indian and global market sentiment from DB summary")
    conn = get_conn()
    try:
        insert_query = """INSERT INTO public.sentiment_store (usa_market_sentiment, usa_market_news_summary, indian_market_sentiment, indian_market_news_summary, verdict_buy, global_market_sentiment, global_market_news_summary, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        
        cursor=execute_insert_statement(conn, insert_query, (usa_sentiment, usa_summary, indian_sentiment,
                                    indian_summary, verdict_buy, global_sentiment,
                                    global_summary, datetime.datetime.today()))
        if(cursor ==-1):
            return False
        else:
            conn.commit()
            cursor.close()
            conn.close()
            log.info('Successfully inserted Sentiment Score')
            return True
        
    except Exception as e:
        log.error(f"Error inserting record for USA,Indian and global sentiment summary: {e}")
        return False
    

def check_last_sentiment_retrieval_within_minutes(minutes=30):
    """Check if latest record is within last 30 minutes"""
      
    log.info("Check if latest sentiment record is created within last 30 minutes")
    conn = get_conn()
    try:
        cursor=execute_sql_statement(conn,"SELECT MAX(date) FROM public.sentiment_store")
        latest_time = cursor.fetchone()[0]
        
        if latest_time:
            time_diff = ((datetime.datetime.combine(datetime.date.today(), datetime.datetime.today().time()) -              datetime.datetime.combine(datetime.date.today(), latest_time)).total_seconds()) / 60
            return time_diff <= minutes
        return False
        
    except Exception as e:
        log.error(f"Error check_last_retrieval_within_minutes: {e}")
        return False

def get_latest_sentiment_records():
    """Get all records for current date"""
    
    log.info("Get all sentiment records for current date")
    conn = get_conn()
    try:
        cursor=execute_sql_statement(conn,"""
        SELECT * FROM public.sentiment_store 
        ORDER BY date DESC LIMIT 1
        """)
        
        records = cursor.fetchall()
        for row in records:
    
            json_data = {
            
            'usa_market_sentiment':row[0],
            'usa_market_news_summary':row[1],
            'indian_market_sentiment':row[2],
            'indian_market_news_summary':row[3],
            'global_market_sentiment':row[4],
            'global_market_news_summary':row[5],
            'buy_PE_CE_ONLY_BASED_ON_NEWS':row[6]

            }
            return json.dumps(json_data)
        
    except Exception as e:
        print(f"Error fetching today's sentiment_store  records: {e}")
        return []
    