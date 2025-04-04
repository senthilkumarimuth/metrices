import requests
import pandas as pd
import matplotlib.pyplot as plt
import os
from custom_dirs import DataDirectory, RootDirectory
from matplotlib.dates import DayLocator, DateFormatter
from datetime import datetime, timedelta

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
            
        # Convert time_last_update_utc to datetime and set as index
        df_inr['time_last_update_utc'] = pd.to_datetime(df_inr['time_last_update_utc'], format='mixed', dayfirst=True)
        df_inr.dropna(subset=['time_last_update_utc'], inplace=True)
        
        # Calculate the start date for the filter (30 days ago)
        today = datetime.today()
        start_date = today - timedelta(days=30)
        
        # Filter data for the last 30 days
        df_inr = df_inr[df_inr['time_last_update_utc'] >= start_date]
        
        # Create the plot with a larger figure size
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot the exchange rate
        ax.plot(df_inr['time_last_update_utc'], df_inr['Rate'], 
                label='USD/INR Rate', marker='o', color='blue', linewidth=2)
        
        # Add value labels to each data point
        for i, row in df_inr.iterrows():
            ax.text(row['time_last_update_utc'], row['Rate'], 
                   f"{row['Rate']:.2f}", fontsize=10, ha='right', va='bottom')

        # Customize the plot
        ax.set_title('USD to INR Exchange Rate Trend', fontsize=14, pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Exchange Rate (INR)', fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.7)

        # Format x-axis dates
        ax.xaxis.set_major_locator(DayLocator())  # Show every day
        ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))  # Format as YYYY-MM-DD
        plt.xticks(rotation=90, ha='center')  # Rotate labels vertically
        
        # Adjust layout to prevent label cutoff
        plt.subplots_adjust(bottom=0.25)  # Add more space at the bottom
        
        # Adjust x-axis limits
        ax.set_xlim(start_date, today)
        
        # Save the plot
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {filename}")

        # Clear the plot
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

