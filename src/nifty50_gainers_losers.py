import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import os

def get_nifty50_symbols():
    # Nifty 50 symbols
    nifty50_symbols = [
        'RELIANCE.NS'
    ]
    return nifty50_symbols

def fetch_stock_data():
    symbols = get_nifty50_symbols()
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    stock_data = []
    
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(start=yesterday, end=today)
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[0]
                change_percent = ((current_price - prev_price) / prev_price) * 100
                
                stock_data.append({
                    'symbol': symbol.replace('.NS', ''),
                    'current_price': round(current_price, 2),
                    'change_percent': round(change_percent, 2)
                })
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
    
    return stock_data

def process_and_save_data():
    stock_data = fetch_stock_data()
    
    # Sort by change percentage
    sorted_data = sorted(stock_data, key=lambda x: x['change_percent'], reverse=True)
    
    # Get top 10 gainers and losers
    gainers = sorted_data[:10]
    losers = sorted_data[-10:][::-1]  # Reverse to show biggest losers first
    
    # Create output directory if it doesn't exist
    output_dir = 'data'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save to JSON file
    output_data = {
        'gainers': gainers,
        'losers': losers,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open(os.path.join(output_dir, 'nifty50_data.json'), 'w') as f:
        json.dump(output_data, f, indent=4)

if __name__ == "__main__":
    process_and_save_data() 