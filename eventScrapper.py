import pandas as pd
import datetime,log
def read_events_this_month():
    file_path_json = f'events\\events-{datetime.datetime.today().strftime("%b")}-{datetime.datetime.today().year}.json' 
    try:
        df= pd.read_json(file_path_json)
        return df
    except:
        log.error('Error reading this month file:'+file_path_json)
        return None

def get_this_week_events():

    df = read_events_this_month()
    if(df is  None):
        log.error('Unable to retrieve this week events')
        return -1

    # Convert date strings to datetime objects
    df['date'] = pd.to_datetime(df['date'])

    # Get today's date
    today = datetime.datetime.now()

    # Get date 7 days from today
    seven_days = today + datetime.timedelta(days=7)

    # Filter records for 7 days from today
    filtered_df = df[(df['date'].dt.date >= today.date()) & (df['date'].dt.date < seven_days.date())]

    print("Events 7 days from today:")
    print(filtered_df.head())
    return filtered_df.to_json()

