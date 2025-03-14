import pandas as pd
import numpy as np
import ticker
import gptConnector
import json,log
import matplotlib.pyplot as plt
from datetime import datetime
import email_sender

nifty_indicator_filename = "nifty\\indicator.png"

def calculate_indicators(df):
    """Compute MACD, RSI, Supertrend, VWAP, and 200 EMA"""
    # MACD Calculation
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # RSI Calculation
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Supertrend Calculation (10,3)
    df['ATR'] = df['Close'].rolling(10).std()  # Approximate ATR
    df['Upper_Band'] = df['Close'] + (3 * df['ATR'])
    df['Lower_Band'] = df['Close'] - (3 * df['ATR'])
    df['Supertrend'] = np.where(df['Close'] > df['Upper_Band'], 1, np.where(df['Close'] < df['Lower_Band'], -1, 0))

    # VWAP Calculation
    df['Cumulative_Volume'] = df['Close'].expanding().sum()
    df['VWAP'] = df['Cumulative_Volume'] / df.index.to_series().expanding().sum()

    # 200 EMA
    df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()
    return df

# Plot MACD & RSI
def plot_macd_rsi(df):
    fig, ax = plt.subplots(4, figsize=(12, 16))
    plt.ioff()
    # Supertrend Plot
    ax[0].plot(df['Date'], df['Close'], label='Close Price', color='blue')
    ax[0].plot(df['Date'], df['Upper_Band'], label='Upper Band', color='green', alpha=0.5)
    ax[0].plot(df['Date'], df['Lower_Band'], label='Lower Band', color='red', alpha=0.5)
    ax[0].set_title("Price with Supertrend Bands")
    ax[0].legend()
    
    
    # ATR Plot
    ax[1].plot(df['Date'], df['ATR'], label='ATR', color='orange')
    ax[1].set_title("Average True Range (ATR)")
    ax[1].legend()
    
    # MACD Plot
    ax[2].plot(df['Date'], df['MACD'], label="MACD", color='blue')
    ax[2].plot(df['Date'], df['Signal_Line'], label="Signal Line", color='red')
    ax[2].set_title("MACD & Signal Line (Real-Time)")
    ax[2].legend()
    
    # RSI Plot
    ax[3].plot(df['Date'], df['RSI'], label="RSI", color='purple')
    ax[3].axhline(70, linestyle="--", color='red', label="Overbought (70)")
    ax[3].axhline(30, linestyle="--", color='green', label="Oversold (30)")
    ax[3].set_title("RSI (Real-Time)")
    ax[3].legend()
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    #plt.show()
    plt.savefig(nifty_indicator_filename)
    plt.close(fig)


# MAIN EXECUTION LOOP
def check_exit_signal(df):
    df = calculate_indicators(df)
    """Generate exit signals based on MACD, RSI, Supertrend, VWAP, EMA 200"""
    last_macd = df['MACD'].iloc[-1]
    last_signal = df['Signal_Line'].iloc[-1]
    last_rsi = df['RSI'].iloc[-1]
    last_supertrend = df['Supertrend'].iloc[-1]
    last_vwap = df['VWAP'].iloc[-1]
    last_ema200 = df['EMA_200'].iloc[-1]
    last_close = df['Close'].iloc[-1]

    exit_signal = False
    reason = ""

    if last_macd < last_signal and last_rsi > 70 and last_supertrend == -1 and last_close < last_vwap and last_close < last_ema200:
        exit_signal = True
        reason = "MACD crossed below Signal, RSI overbought, Supertrend turned bearish, Price below VWAP & EMA 200"

    return exit_signal, reason

def get_nifty_indicators(df):
    df = calculate_indicators(df)
    """Generate exit signals based on MACD, RSI, Supertrend, VWAP, EMA 200"""
    last_macd = df['MACD'].iloc[-1]
    last_signal = df['Signal_Line'].iloc[-1]
    last_rsi = df['RSI'].iloc[-1]
    last_supertrend = df['Supertrend'].iloc[-1]
    last_vwap = df['VWAP'].iloc[-1]
    last_ema200 = df['EMA_200'].iloc[-1]
    last_close = df['Close'].iloc[-1]

    exit_signal = False
    reason = ""

    return {
        "last_macd":last_macd,
        "last_signal":last_signal,
        "last_rsi":last_rsi,
        "last_supertrend":last_supertrend,
        "last_vwap":last_vwap,
        "last_ema200":last_ema200,
        "last_close":last_close
    }

def check_for_nuetral_market():
    return False

def get_buy_signal(sentiment_json, fii_dii_json, nifty_5_day_image_path, nifty_intraday_image_path):
    
    df = ticker.get_realtime_nifty()
    df= calculate_indicators(df)
    plot_macd_rsi(df)
    bel_json = ticker.get_realtime_BEL_price()
    
    signal = gptConnector.get_buy_signal(sentiment_json, fii_dii_json, bel_json,nifty_indicator_filename, nifty_5_day_image_path, nifty_intraday_image_path)
    if(signal == -1):
        log.error("Problem with GPT in genearting signal")
        return -1
    json_str = signal.replace('<JSON>', '').replace('</JSON>', '').replace('```json\n{','{').replace('\n```','').replace('\n','')
    data = json.loads(json_str)
    email_sender.send_email(data,sentiment_json, fii_dii_json, bel_json,nifty_indicator_filename, nifty_5_day_image_path, nifty_intraday_image_path)
    
    return data
def get_sell_signal(x, json_data, currentTrade):
    print("Give me Sell signal")
