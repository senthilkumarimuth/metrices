import requests
import pandas as pd
import matplotlib.pyplot as plt
import os

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
    # apend this to dataframe existing at  to ./data/ folder usd_to_inr_exchange_rate.csv
    if os.path.exists("./data/usd_to_inr_exchange_rate.csv"):
        existing_df = pd.read_csv("./data/usd_to_inr_exchange_rate.csv")
        df = pd.concat([existing_df, df], ignore_index=True)
    # remove duplicate
    df = df.drop_duplicates(subset='time_last_update_utc')
    df.to_csv("./data/usd_to_inr_exchange_rate.csv", index=False)
    return df


def plot_and_save_usd_to_inr(df, filename="usd_to_inr_exchange_rate.png"):
    """Plots and saves the USD to INR exchange rate."""
    if df is None:
        print("No data to plot.")
        return

    try:
        df_inr = df[df['Currency'] == 'INR'].copy()
        if df_inr.empty:
            print("No INR data found in DataFrame.")
            return

        df_inr.drop(columns=['Currency'], inplace=True)
        df_inr.rename(columns={'Rate': 'INR'}, inplace=True)

        ax = df_inr.plot(x='time_last_update_utc', y='INR', kind='line', marker= 'o',legend=True, label='INR')  # added legend=False
        plt.title('USD to INR Exchange Rate')
        plt.xlabel('Date')
        plt.ylabel('INR')

        ax.legend(['INR'])
        plt.tight_layout()

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

