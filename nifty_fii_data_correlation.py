import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def convert_daily_to_monthly_ohlc(df):
    """
    Convert daily OHLC data to monthly OHLC data
    
    Parameters:
    df (pd.DataFrame): Daily OHLC dataframe with columns: ['Date', 'Open', 'High', 'Low', 'Close']
    
    Returns:
    pd.DataFrame: Monthly OHLC data
    """
    # Ensure the date column is datetime
    
    
    # Resample to monthly frequency
    monthly_ohlc = pd.DataFrame()
    monthly_ohlc['Open'] = df['Open'].resample('ME').first()  # First price of the month
    monthly_ohlc['High'] = df['High'].resample('ME').max()    # Highest price of the month
    monthly_ohlc['Low'] = df['Low'].resample('ME').min()      # Lowest price of the month
    monthly_ohlc['Close'] = df['Close'].resample('ME').last() # Last price of the month
    
    # Reset index to get Date as a column
    monthly_ohlc.reset_index(inplace=True)
    
    return monthly_ohlc
# Load FII/DII data
fii_dii_data = pd.read_csv('C:\\Users\\Raghavan M\\Downloads\\ABCD.csv',
                            parse_dates=['Date'], dayfirst=True)
#fii_dii_data.set_index('Date', inplace=True)

# Load Nifty 50 OHLC data
nifty_data = pd.read_csv('C:\\Users\\Raghavan M\\Downloads\\NIFTY 50-07-03-2024-to-07-03-2025.csv', 
                         parse_dates=['Date'], dayfirst=True)
#nifty_data.set_index('Date', inplace=True)

nifty_monthly_data = convert_daily_to_monthly_ohlc(nifty_data)
print(fii_dii_data.columns)

# Ensure data alignment
nifty_data['Date'] = pd.to_datetime(nifty_monthly_data['Date'])
fii_dii_data['Date'] = pd.to_datetime(fii_dii_data['Date'])
    
data = nifty_monthly_data.join(fii_dii_data, how='inner')
#view this data in a table format 

# Calculate Nifty 50 daily returns
data['Nifty_Returns'] = data['Close'].pct_change()
print(data.head())

# Calculate correlation coefficients
correlation_matrix = data[['FII Equity', 'MF Equity', 'Nifty_Returns']].corr()

# Display correlation matrix
print("Correlation Matrix:")
print(correlation_matrix)

# Plotting the data
plt.figure(figsize=(14, 7))

# Plot Nifty 50 Closing Prices
plt.subplot(2, 1, 1)
plt.plot(data.index, data['Close'], label='Nifty 50 Close', color='blue')
plt.title('Nifty 50 Closing Prices')
plt.xlabel('Date')
plt.ylabel('Close Price')
plt.legend()

# Plot FII and DII Net Investments
plt.subplot(2, 1, 2)
plt.bar(data.index, data['FII Equity'], label='FII Net Investments', color='green', alpha=0.6)
plt.bar(data.index, data['MF Equity'], label='DII Net Investments', color='red', alpha=0.6)
plt.title('FII and DII Net Investments')
plt.xlabel('Date')
plt.ylabel('Net Investment (INR Crores)')
plt.legend()

plt.tight_layout()
plt.show()
