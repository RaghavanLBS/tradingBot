import db
import datetime



def compute_signal(market_sentiment, gpt_sentiment, final_sentiment, news_summary,fii_weighted, dii_weighted):
    """Generates trade signals & stores them in SQLite."""
    
    
    final_sentiment, news_summary = compute_final_sentiment()
    gift_nifty = fetch_gift_nifty()
    nifty_ohlc = fetch_nifty_ohlc()

    close_prices = [entry['close'] for entry in nifty_ohlc]
    x = np.arange(len(close_prices))
    slope, _, r_value, _, _ = linregress(x, close_prices)
    momentum_trend = slope * r_value

    # Decision Criteria
    trade_type = None
    entry_reason = ""

    if gift_nifty > close_prices[-1] and momentum_trend > 0 and final_sentiment > 0:
        trade_type = "BUY CE"
        entry_reason = "Positive momentum, bullish sentiment, GIFT Nifty above last close"
    elif gift_nifty < close_prices[-1] and momentum_trend < 0 and final_sentiment < 0:
        trade_type = "BUY PE"
        entry_reason = "Negative momentum, bearish sentiment, GIFT Nifty below last close"
    else:
        trade_type = "NO TRADE"
    computed_market_sentiment = compute_market_sentiment()
    
    if trade_type != "NO TRADE":
        # Store trade in SQLite
      obj = { 
          trade_type:trade_type ,
          entry_reason:entry_reason,
          fii_weighted:fii_weighted,
          dii_weighted:dii_weighted,
          computed_market_sentiment:computed_market_sentiment,
          gpt_sentiment:gpt_sentiment, 
          final_sentiment:final_sentiment
      }
      db.createBuyTrade(obj)

    
    return trade_type, entry_reason
