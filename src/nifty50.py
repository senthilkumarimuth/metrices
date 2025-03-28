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
    # nifty50_symbols = [
    #     'RELIANCE.NS'
        
    # ]
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
                stock_data.append({
                    'symbol': symbol.replace('.NS', ''),
                    'open': round(hist['Open'].iloc[0], 2),
                    'close': round(hist['Close'].iloc[-1], 2),
                    'high': round(hist['High'].iloc[0], 2),
                    'low': round(hist['Low'].iloc[0], 2),
                    'volume': int(hist['Volume'].iloc[0])
                })
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
    
    return stock_data

def fetch_nifty50_index():
    try:
        nifty = yf.Ticker("^NSEI")
        hist = nifty.history(period="1d")
        
        if not hist.empty:
            return {
                'current_value': round(hist['Close'].iloc[-1], 2),
                'open': round(hist['Open'].iloc[0], 2),
                'high': round(hist['High'].iloc[0], 2),
                'low': round(hist['Low'].iloc[0], 2),
                'volume': int(hist['Volume'].iloc[0])
            }
    except Exception as e:
        print(f"Error fetching Nifty 50 index data: {str(e)}")
    return None

def process_and_save_data():
    stock_data = fetch_stock_data()
    nifty_index = fetch_nifty50_index()
    
    # Create output directory if it doesn't exist
    output_dir = DataDirectory.path
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save to JSON file
    output_data = {
        'nifty50_index': nifty_index,
        'stocks': stock_data,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open(os.path.join(output_dir, 'nifty50_data.json'), 'w') as f:
        json.dump(output_data, f, indent=4)

if __name__ == "__main__":
    process_and_save_data() 