import datetime, json
def next_market_open_time( market_open_time="09:15:00", market_close_time="15:30:00"):
    curtimestamp = datetime.datetime.today()
    curdate = curtimestamp.strftime('%Y-%m-%d')
    holiday_list = []
    with open('holidays\\2025.json') as f:
        holiday_list = json.load(f)
        
    if(curtimestamp.strftime('%d-%b-%Y') in holiday_list):
            return 86400 # 1 day = 86400 seconds
    market_close_time_sec = datetime.datetime.strptime(f"{curdate} {market_close_time}", "%Y-%m-%d %H:%M:%S").timestamp()
    market_open_time_sec = datetime.datetime.strptime(f"{curdate} {market_open_time}", "%Y-%m-%d %H:%M:%S").timestamp()
    if(curtimestamp.timestamp() < market_open_time_sec ):
        timeToOpen = 0
        newDate = curtimestamp.replace(hour=9, minute=15)
        timeToOpen = (newDate -curtimestamp).total_seconds()
        return timeToOpen
    if(curtimestamp.timestamp() > market_close_time_sec ):
        timeToOpen = 0
        newDate = (curtimestamp + datetime.timedelta(days=1)).replace(hour=9, minute=15)
        timeToOpen = (newDate -curtimestamp).total_seconds()
        return timeToOpen
    

timesec = next_market_open_time()