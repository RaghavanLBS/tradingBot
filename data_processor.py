import pandas as pd

def convert_daily_to_monthly_ohlc(df):
    """
    Convert daily OHLC data to monthly OHLC data
    
    Parameters:
    df (pd.DataFrame): Daily OHLC dataframe with columns: ['Date', 'Open', 'High', 'Low', 'Close']
    
    Returns:
    pd.DataFrame: Monthly OHLC data
    """
    # Print input DataFrame info
    print("\nInput DataFrame Columns:")
    print(df.columns.tolist())
    print("\nInput DataFrame Info:")
    print(df.info())
    
    # Ensure the date column is datetime
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    
    # Resample to monthly frequency
    monthly_ohlc = pd.DataFrame()
    monthly_ohlc['Open'] = df['Open'].resample('M').first()  # First price of the month
    monthly_ohlc['High'] = df['High'].resample('M').max()    # Highest price of the month
    monthly_ohlc['Low'] = df['Low'].resample('M').min()      # Lowest price of the month
    monthly_ohlc['Close'] = df['Close'].resample('M').last() # Last price of the month
    
    # Reset index to get Date as a column
    monthly_ohlc.reset_index(inplace=True)
    
    # Print output DataFrame info
    print("\nOutput Monthly DataFrame Columns:")
    print(monthly_ohlc.columns.tolist())
    print("\nOutput Monthly DataFrame Info:")
    print(monthly_ohlc.info())
    
    return monthly_ohlc

def merge_nifty_fii_data(nifty_data, fii_dii_data):
    """
    Merge NIFTY monthly data with FII/DII data
    
    Parameters:
    nifty_data (pd.DataFrame): NIFTY OHLC data with Date column
    fii_dii_data (pd.DataFrame): FII/DII data with Date column
    
    Returns:
    pd.DataFrame: Merged data
    """
    # Convert both date columns to datetime
    nifty_data['Date'] = pd.to_datetime(nifty_data['Date'])
    fii_dii_data['Date'] = pd.to_datetime(fii_dii_data['Date'])
    
    # Convert dates to the same format (year-month only for monthly comparison)
    nifty_data['YearMonth'] = nifty_data['Date'].dt.to_period('M')
    fii_dii_data['YearMonth'] = fii_dii_data['Date'].dt.to_period('M')
    
    # Merge on YearMonth
    merged_data = pd.merge(
        nifty_data,
        fii_dii_data,
        on='YearMonth',
        how='inner'
    )
    
    # Clean up the merged dataframe
    merged_data.drop(['YearMonth', 'Date_y'], axis=1, inplace=True)
    merged_data.rename(columns={'Date_x': 'Date'}, inplace=True)
    
    # Sort by date
    merged_data.sort_values('Date', inplace=True)
    merged_data.reset_index(drop=True, inplace=True)
    
    return merged_data

def process_nifty_data(nifty_file_path, fii_dii_file_path=None):
    """
    Process NIFTY 50 data and optionally merge with FII/DII data
    
    Parameters:
    nifty_file_path (str): Path to the NIFTY 50 data file
    fii_dii_file_path (str, optional): Path to the FII/DII data file
    """
    try:
        # Read the daily data
        daily_data = pd.read_csv(nifty_file_path)
        print("\nOriginal NIFTY Data Columns:")
        print(daily_data.columns.tolist())
        print("\nFirst few rows of original data:")
        print(daily_data.head())
        
        # Convert to monthly
        monthly_data = convert_daily_to_monthly_ohlc(daily_data)
        
        # Filter for the specific date range (07-03-2024 to 07-03-2025)
        start_date = '2024-03-07'
        end_date = '2025-03-07'
        monthly_data = monthly_data[
            (monthly_data['Date'] >= start_date) & 
            (monthly_data['Date'] <= end_date)
        ]
        
        # If FII/DII data path is provided, merge the data
        if fii_dii_file_path:
            fii_dii_data = pd.read_csv(fii_dii_file_path)
            print("\nFII/DII Data Columns:")
            print(fii_dii_data.columns.tolist())
            monthly_data = merge_nifty_fii_data(monthly_data, fii_dii_data)
            
        return monthly_data
        
    except Exception as e:
        print(f"Error processing data: {e}")
        return None

# Example usage:
if __name__ == "__main__":
    # For debugging
    def print_data_info(df, name):
        print(f"\n{name} Info:")
        print(f"Shape: {df.shape}")
        print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
        print(f"Columns: {df.columns.tolist()}")
        print("\nFirst few rows:")
        print(df.head()) 