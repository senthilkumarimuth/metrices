import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import os
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
        'HDFC.NS',
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
        'HINDUNILVR.NS',
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
    nifty50_symbols = [
        'RELIANCE.NS'
        
    ]
    return nifty50_symbols

def fetch_stock_data():
    symbols = get_nifty50_symbols()
    today = datetime.now()
    
    stock_data = []
    
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(start=today, end=today)
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                
                stock_data.append({
                    'symbol': symbol.replace('.NS', ''),
                    'current_price': round(current_price, 2)
                })
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
    
    return stock_data

def process_and_save_data():
    stock_data = fetch_stock_data()
    
    # Sort by current price
    sorted_data = sorted(stock_data, key=lambda x: x['current_price'], reverse=True)
    
    # Get top 10 highest and lowest priced stocks
    highest_priced = sorted_data[:10]
    lowest_priced = sorted_data[-10:][::-1]  # Reverse to show lowest priced first
    
    # Create output directory if it doesn't exist
    output_dir = DataDirectory.path
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save to JSON file
    output_data = {
        'highest_priced': highest_priced,
        'lowest_priced': lowest_priced,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open(os.path.join(output_dir, 'nifty50_data.json'), 'w') as f:
        json.dump(output_data, f, indent=4)

if __name__ == "__main__":
    process_and_save_data() 