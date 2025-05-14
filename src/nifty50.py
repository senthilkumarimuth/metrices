import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import time
from custom_dirs import DataDirectory

def get_nifty50_symbols():
    # Nifty 50 symbols
    nifty50_symbols = [
        'RELIANCE.NS',
        'TCS.NS',
        'HDFCBANK.NS',
        'INFY.NS',
        'ICICIBANK.NS',
        'HINDUNILVR.NS',
        'SBIN.NS',
        'BHARTIARTL.NS',
        'ITC.NS',
        'KOTAKBANK.NS',
        'HCLTECH.NS',
        'WIPRO.NS',
        'AXISBANK.NS',
        'ASIANPAINT.NS',
        'ULTRACEMCO.NS',
        'TITAN.NS',
        'BAJFINANCE.NS',
        'MARUTI.NS',
        'NESTLEIND.NS',
        'BAJAJFINSV.NS',
        'BAJAJ-AUTO.NS',
        'HINDALCO.NS',
        'JSWSTEEL.NS',
        'POWERGRID.NS',
        'ADANIENT.NS',
        'ADANIPORTS.NS',
        'ADANIPOWER.NS',
        'BPCL.NS',
        'BRITANNIA.NS',
        'CIPLA.NS',
        'COALINDIA.NS',
        'DLF.NS',
        'DIVISLAB.NS',
        'DRREDDY.NS',
        'EICHERMOT.NS',
        'GAIL.NS',
        'GODREJCP.NS',
        'GRASIM.NS',
        'HDFCLIFE.NS',
        'HEROMOTOCO.NS',
        'ICICIGI.NS',
        'ICICIPRULI.NS',
        'IOC.NS',
        'INDUSINDBK.NS',
        'M&M.NS',
        'MARICO.NS',
        'NTPC.NS',
        'ONGC.NS',
        'PIDILITIND.NS',
        'SBILIFE.NS',
        'SHREECEM.NS',
        'SUNPHARMA.NS',
        'TATASTEEL.NS',
        'TECHM.NS',
        'UPL.NS'
    ]
    return nifty50_symbols

def fetch_stock_data():
    symbols = get_nifty50_symbols()
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    print(f"Fetching data from {yesterday.date()} to {today.date()}")
    stock_data = []
    
    # Use batch downloading to fetch data for all symbols at once
    try:
        print("Fetching data for all stocks...")
        hist = yf.download(symbols, start=yesterday, end=today, group_by='ticker')
        
        for symbol in symbols:
            try:
                if not hist.empty and symbol in hist.columns.levels[0]:
                    stock_hist = hist[symbol]
                    if not stock_hist.empty:
                        stock_data.append({
                            'symbol': symbol.replace('.NS', ''),
                            'open': round(stock_hist['Open'].iloc[-1], 2),
                            'close': round(stock_hist['Close'].iloc[-1], 2),
                            'high': round(stock_hist['High'].iloc[-1], 2),
                            'low': round(stock_hist['Low'].iloc[-1], 2),
                            'volume': int(stock_hist['Volume'].iloc[-1]),
                            'prev_close': round(stock_hist['Close'].iloc[0], 2) if len(stock_hist) > 1 else None
                        })
                        print(f"Successfully fetched data for {symbol}")
                    else:
                        print(f"No data available for {symbol}")
                else:
                    print(f"No data available for {symbol}")
            except Exception as e:
                print(f"Error processing data for {symbol}: {str(e)}")
    except Exception as e:
        print(f"Error fetching batch data: {str(e)}")
    
    print(f"Successfully fetched data for {len(stock_data)} out of {len(symbols)} stocks")
    return stock_data

def fetch_nifty50_index():
    try:
        print("Fetching Nifty 50 index data...")
        nifty = yf.Ticker("^NSEI")
        hist = nifty.history(period="1d")
        
        if not hist.empty:
            print("Successfully fetched Nifty 50 index data")
            return {
                'current_value': round(hist['Close'].iloc[-1], 2),
                'open': round(hist['Open'].iloc[0], 2),
                'high': round(hist['High'].iloc[0], 2),
                'low': round(hist['Low'].iloc[0], 2),
                'volume': int(hist['Volume'].iloc[0])
            }
        else:
            print("No data available for Nifty 50 index")
    except Exception as e:
        print(f"Error fetching Nifty 50 index data: {str(e)}")
    return None

def process_and_save_data():
    print("Starting data fetch process...")
    stock_data = fetch_stock_data()
    nifty_index = fetch_nifty50_index()
    
    # Create output directory if it doesn't exist
    output_dir = DataDirectory.path
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Save to JSON file
    output_data = {
        'nifty50_index': nifty_index,
        'stocks': stock_data,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    output_file = os.path.join(output_dir, 'nifty50_data.json')
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    process_and_save_data() 