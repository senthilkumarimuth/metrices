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
            # Calculate the start date for the filter (30 days ago)
            today = datetime.today()
            start_date = today - timedelta(days=30)

            # Filter data for the last 30 days
            df = df[df['date'] >= start_date]
            # Extract 'FII' and 'DII' data
            fii_data = df[df['category'] == 'FII/FPI *']
            dii_data = df[df['category'] == 'DII **']

            # Create figure with three subplots
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15))

            # Plot 1: FII Buy vs Sell
            ax1.plot(fii_data['date'], fii_data['buyValue'], label='FII Buy', marker='o', color='green')
            ax1.plot(fii_data['date'], fii_data['sellValue'], label='FII Sell', marker='o', color='red')
            ax1.set_title('FII Buy vs Sell')
            ax1.set_ylabel('Value (in Cr)')
            ax1.legend()
            ax1.grid(True)
            ax1.xaxis.set_major_locator(DayLocator())
            ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

            # Plot 2: DII Buy vs Sell
            ax2.plot(dii_data['date'], dii_data['buyValue'], label='DII Buy', marker='x', color='red')
            ax2.plot(dii_data['date'], dii_data['sellValue'], label='DII Sell', marker='x', color='green')
            ax2.set_title('DII Buy vs Sell')
            ax2.set_ylabel('Value (in Cr)')
            ax2.legend()
            ax2.grid(True)
            ax2.xaxis.set_major_locator(DayLocator())
            ax2.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

            # Plot 3: FII Net vs DII Net
            ax3.plot(fii_data['date'], fii_data['netValue'], label='FII Net', marker='o', color='green')
            ax3.plot(dii_data['date'], dii_data['netValue'], label='DII Net', marker='x', color='red')
            ax3.set_title('FII Net vs DII Net')
            ax3.set_xlabel('Date')
            ax3.set_ylabel('Value (in Cr)')
            ax3.legend()
            ax3.grid(True)
            ax3.xaxis.set_major_locator(DayLocator())
            ax3.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')

            # Adjust layout to prevent overlap
            plt.tight_layout()
            
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
