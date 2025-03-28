import requests
import pandas as pd
import matplotlib.pyplot as plt
import os
from custom_dirs import DataDirectory, RootDirectory
from matplotlib.dates import DayLocator, DateFormatter

API_KEY = "bf4ade668e2827d69705ea67"  # Replace with your actual API key
url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"


def get_exchange_rate_data(url):
    """Fetches exchange rate data from the API."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None


def create_dataframe(data):
    """Creates a DataFrame from the API response."""
    if not data or "conversion_rates" not in data:
        print("Invalid or missing data from API response.")
        return None

    rates = data["conversion_rates"]
    df = pd.DataFrame(list(rates.items()), columns=['Currency', 'Rate'])
    df.insert(0, 'time_last_update_utc', data['time_last_update_utc'])
    # convert time_last_update_utc to date dd/mm/yyyy format
    df['time_last_update_utc'] = pd.to_datetime(df['time_last_update_utc']).dt.strftime('%d/%m/%Y')
    df = df[df['Currency'] == 'INR']
    print(df)
    # apend this to dataframe existing at  to ./data/ folder usd_to_inr_exchange_rate.csv
    if os.path.exists(os.path.join(DataDirectory.path,"usd_to_inr_exchange_rate.csv")):
        existing_df = pd.read_csv(os.path.join(DataDirectory.path,"usd_to_inr_exchange_rate.csv"))
        df = pd.concat([existing_df, df], ignore_index=True)
    # remove duplicate
    df = df.drop_duplicates(subset='time_last_update_utc')
    df.to_csv(os.path.join(DataDirectory.path,"usd_to_inr_exchange_rate.csv"), index=False)
    return df


def plot_and_save_usd_to_inr(df, filename=os.path.join(RootDirectory.path,"src","usd_to_inr_exchange_rate.png")):
    """Plots and saves the USD to INR exchange rate."""
    if df is None:
        print("No data to plot.")
        return

    try:
        df_inr = df[df['Currency'] == 'INR'].copy()
        if df_inr.empty:
            print("No INR data found in DataFrame.")
            return
        # Convert time_last_update_utc to datetime
        # Convert time_last_update_utc to datetime and set as index
        df_inr['time_last_update_utc'] = pd.to_datetime(df_inr['time_last_update_utc'], format='mixed', dayfirst=True)
        df_inr.dropna(subset=['time_last_update_utc'], inplace=True)
        df_inr.insert(1, 'date', df_inr['time_last_update_utc'].dt.date)
        df_inr.set_index('time_last_update_utc', inplace=True)  # Set datetime as index

        df_inr.drop(columns=['Currency'], inplace=True)
        df_inr.rename(columns={'Rate': 'INR'}, inplace=True)

        ax = df_inr.plot(x='date', y='INR', kind='line', marker= 'o', legend=True)

        # Add labels to each data point
        for i, row in df_inr.iterrows():
            ax.text(row['date'], row['INR'], f"{row['INR']:.2f}",
                    fontsize=10, ha='right', va='bottom', color='black')

        # Format x-axis dates
        ax.xaxis.set_major_locator(DayLocator())  # Show every day
        ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))  # Format as YYYY-MM-DD
        plt.xticks(rotation=90, ha='center')  # Rotate labels vertically
        
        # Adjust layout to prevent label cutoff
        plt.subplots_adjust(bottom=0.25)  # Add more space at the bottom
        
        plt.title('USD to INR Exchange Rate')
        plt.xlabel('Date')
        plt.ylabel('INR')

        # Save the plot to a file
        plt.savefig(filename)
        print(f"Plot saved to {filename}")

        # Clear the plot
        plt.clf()
        plt.close()

    except Exception as e:
        print(f"An error occurred during plotting: {e}")

def main():
    """Main function to orchestrate the process."""
    data = get_exchange_rate_data(url)
    df = create_dataframe(data)
    plot_and_save_usd_to_inr(df)
if __name__ == "__main__":
    main()

