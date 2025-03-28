import requests
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
from matplotlib.dates import DayLocator, DateFormatter

from custom_dirs import DataDirectory, RootDirectory


def get_fii_dii_data():
    url = "https://www.nseindia.com/api/fiidiiTradeReact"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)  # Establish session
        response = session.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None


def save_data_to_csv(data, filename=os.path.join(DataDirectory.path, "fii_dii_buy_sell_data.csv")):
    if data:
        try:
            df = pd.DataFrame(data)
            print(df)
            # df.to_csv(filename, index=False)
            if os.path.exists(filename):
                existing_df = pd.read_csv(filename)
                df = pd.concat([existing_df, df], ignore_index=True)
            df.drop_duplicates(subset=['date', 'category'], keep='last', inplace=True)
            df.to_csv(filename, index=False)
            print(f"Data saved to {filename}")
        except IOError as e:
            print(f"Error saving data to {filename}: {e}")


def load_data_from_csv(filename=os.path.join(DataDirectory.path,"fii_dii_buy_sell_data.csv")):
    try:
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            return df
        else:
            print(f"File {filename} does not exist.")
            return None
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return None
    except pd.errors.EmptyDataError:
        print(f"File is empty: {filename}")
        return None
    except pd.errors.ParserError:
        print(f"Error parsing file: {filename}")
        return None


def create_visualization(df, filename=os.path.join(RootDirectory.path, "src","fii_dii_trends.png")):
    if df is not None:
        try:
            # Convert 'date' column to datetime objects
            df['date'] = pd.to_datetime(df['date'],format='mixed', dayfirst=True)
            # Calculate the start date for the filter (7 days ago)
            today = datetime.today()
            start_date = today - timedelta(days=30)

            # Filter data for the last 7 days
            df = df[df['date'] >= start_date]
            # Extract 'FII' and 'DII' data
            fii_data = df[df['category'] == 'FII/FPI *']
            dii_data = df[df['category'] == 'DII **']

            # Create the plot
            fig, ax = plt.subplots(figsize=(12, 6))

            # Plot FII data
            ax.plot(fii_data['date'], fii_data['buyValue'], label='FII Buy', marker='o', color='green')
            ax.plot(fii_data['date'], fii_data['sellValue'], label='FII Sell', marker='o', color='red')
            ax.plot(fii_data['date'], fii_data['netValue'], label='FII Net', linestyle='--', marker='o', color='blue')

            # Plot DII data
            ax.plot(dii_data['date'], dii_data['buyValue'], label='DII Buy', marker='x', color='red')
            ax.plot(dii_data['date'], dii_data['sellValue'], label='DII Sell',marker='x', color='green')
            ax.plot(dii_data['date'], dii_data['netValue'], label='DII Net', linestyle='-.', marker='x', color='blue')

            # Customize the plot
            ax.set_title('FII/DII Trading Trends')
            ax.set_xlabel('date')
            ax.set_ylabel('Value (in Cr)')
            ax.legend()
            ax.grid(True)

            # Format x-axis dates
            ax.xaxis.set_major_locator(DayLocator())  # Show every day
            ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))  # Format as YYYY-MM-DD
            plt.xticks(rotation=90, ha='center')  # Rotate labels vertically
            
            # Adjust layout to prevent label cutoff
            plt.subplots_adjust(bottom=0.25)  # Add more space at the bottom
            
            # Adjust x-axis limits
            ax.set_xlim(start_date, today)
            
            # Save the plot
            plt.savefig(filename)
            print(f"Visualization saved to {filename}")

            # Close the plot to prevent display
            plt.close()
        except Exception as e:
            print(f"An error occurred: {e}")


def main():
    data = get_fii_dii_data()
    save_data_to_csv(data)
    df = load_data_from_csv()
    create_visualization(df)


if __name__ == "__main__":
    main()
