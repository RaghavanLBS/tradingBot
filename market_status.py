import json,datetime,log

market_open = False
volatile_time_over = False
market_open = "09:00:00"
market_close = "15:30:00"
volatile_end_time = "09:45:00 AM"
def is_market_open():
    
    with open('holidays\\2025.json') as f:
        d = json.load(f)
        curtimestamp = datetime.datetime.today()
        curdate = curtimestamp.strftime('%Y-%m-%d')
        if(curtimestamp.strftime('%d-%b-%Y') in d):
            return False
        
        market_close_time_sec = datetime.datetime.strptime(f"{curdate} {market_close}", "%Y-%m-%d %H:%M:%S").timestamp()
        market_open_time_sec = datetime.datetime.strptime(f"{curdate} {market_open}", "%Y-%m-%d %H:%M:%S").timestamp()
        if(curtimestamp.timestamp() >= market_open_time_sec and curtimestamp.timestamp() <= market_close_time_sec):
            log.info("Market is open Now")
            return True
    log.info("Market is Closed Now")
    return False

def is_in_volatile_time(currentdate):
      
    if(currentdate.strftime("%H:%M:%S") < volatile_end_time ):
        return False
    return True