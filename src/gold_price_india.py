from matplotlib import legend
import requests
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
from openai import AzureOpenAI
from serpapi import GoogleSearch

# Load environment variables from .env file
load_dotenv()

def get_gold_price_with_serpapi():
    """Fetches gold price data using SerpAPI."""
    try:
        # Get SerpAPI key from environment variables
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        if not serpapi_key:
            print("SerpAPI key not found in environment variables")
            return None
            
        # Set up the search parameters
        params = {
            "engine": "google",
            "q": "current gold price per gram in chennai, india 24k 22k today as per goodreturns website",
            "location": "India",
            "google_domain": "google.co.in",
            "gl": "in",
            "hl": "en",
            "api_key": serpapi_key
        }
        
        # Execute the search
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Extract the organic results
        if "organic_results" in results and len(results["organic_results"]) > 0:
            # Get the snippets from the top 3 results
            snippets = []
            for i, result in enumerate(results["organic_results"][:1]):
                if "snippet" in result:
                    snippets.append(result["snippet"])
                    
            # Join the snippets
            context = "\n".join(snippets)
            return context
        else:
            print("No organic results found in SerpAPI response")
            return None
            
    except Exception as e:
        print(f"Error fetching data from SerpAPI: {e}")
        return None

def get_gold_price_data():
    """Gets today's gold price data using Azure OpenAI with SerpAPI context."""
    try:
        # Initialize the Azure OpenAI client
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        # Get today's date for the prompt
        today_date = datetime.now().strftime('%d %B %Y')
        
        # Get context from SerpAPI
        serpapi_context = get_gold_price_with_serpapi()
        
        # Create the prompt for getting current gold prices
        prompt = f"""
        I need today's ({today_date}) gold price in chennai, India per gram for both 24K and 22K gold.
        Please provide only the numerical values in INR without any symbols or text.
        
        Here is some context from recent search results that might help:
        {serpapi_context if serpapi_context else "No additional context available."}
        
        Make sure the data is for today's date, not historical data.
        
        Format your response as a JSON object with the following structure:
        {{
            "gold_24k_price": [price in INR as a number],
            "gold_22k_price": [price in INR as a number],
            "date_of_rate": "{today_date}"
        }}
        """
        
        # Call the Azure OpenAI API
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides accurate gold price information for chennai in India. Always return today's current data in the requested format. Use the context provided to extract the most accurate information."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Extract the JSON response
        json_response = json.loads(response.choices[0].message.content)
        
        # Validate that the response contains the required fields
        if not all(key in json_response for key in ['gold_24k_price', 'gold_22k_price']):
            print("Incomplete data received from API")
            return fallback_data()
            
        # Get current date
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        # Create data dictionary
        result = {
            'date': current_date,
            'gold_24k_price': float(json_response['gold_24k_price']),
            'gold_22k_price': float(json_response['gold_22k_price'])
        }
        
        # Log the source of the data
        print(f"Successfully retrieved gold prices for {current_date}")
        
        return result
    
    except Exception as e:
        print(f"Error fetching gold price data: {e}")
        return fallback_data()

def fallback_data():
    """Returns fallback data if API call fails."""
    current_date = datetime.now().strftime('%d/%m/%Y')
    print(f"Using fallback gold price data for {current_date}")
    
    return {
        'date': current_date,
        'gold_24k_price': 6450.75,  # Sample price for 24K gold per gram
        'gold_22k_price': 5915.25   # Sample price for 22K gold per gram
    }

def save_gold_data_to_csv(data, filename="./data/gold_price_data.csv"):
    """Saves gold price data to CSV file."""
    if not data:
        print("No data to save.")
        return
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Create DataFrame from data
    df = pd.DataFrame([data])
    print(df)
    try:
        # If file exists, append to it
        if os.path.exists(filename):
            existing_df = pd.read_csv(filename)
            df = pd.concat([existing_df, df], ignore_index=True)
            
        # Remove duplicates based on date
        df.drop_duplicates(subset=['date'], keep='last', inplace=True)
        
        # Save to CSV
        df.to_csv(filename, index=False)
        print(f"Gold price data saved to {filename}")
        
    except Exception as e:
        print(f"Error saving gold price data: {e}")

def plot_gold_price_trend(filename="./data/gold_price_data.csv", output_file="./src/gold_price_trend.png"):
    """Creates a visualization of gold price trends."""
    try:
        if not os.path.exists(filename):
            print(f"File {filename} does not exist.")
            return
        
        # Read data
        df = pd.read_csv(filename)
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'], format='mixed', dayfirst=True)
        
        # Sort by date
        df = df.sort_values('date')
        
        # Filter last 30 days
        start_date = datetime.today() - timedelta(days=30)
        df = df[df['date'] >= start_date]
        
        # Create date strings for display
        df['date_str'] = df['date'].dt.strftime('%d/%m/%Y')
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        
        # Plot using the categorical x positions
        ax.plot(df['date'], df['gold_22k_price'], marker='o', label='22K Gold (₹/gram)', color='green' )
        ax.plot(df['date'], df['gold_24k_price'], marker='o', label='24K Gold (₹/gram)', color='blue')
        
        # Add labels to data points
        for i, row in df.iterrows():
            idx = df.index.get_loc(i)
            ax.text(row['date'], row['gold_22k_price'], f"₹{row['gold_22k_price']:.0f}",
                    fontsize=9, ha='right', va='bottom')
            ax.text(row['date'], row['gold_24k_price'], f"₹{row['gold_24k_price']:.0f}",
                    fontsize=9, ha='right', va='top')
        
        # Customize plot
        ax.set_title('Gold Price Trend in India (per gram)')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price (₹)')
        ax.grid(True)
        ax.legend()
        
       # Improve date label readability
        plt.xticks(rotation=45, ha='right')  # Rotate and align labels to the right
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        # Adjust x-axis limits
        ax.set_xlim(start_date, datetime.today())
        
        plt.tight_layout()
        
        # Save plot
        plt.savefig(output_file)
        print(f"Gold price trend visualization saved to {output_file}")
        
        # Close plot
        plt.close()
        
    except Exception as e:
        print(f"Error creating gold price visualization: {e}")

def main():
    """Main function to orchestrate the process."""
    data = get_gold_price_data()
    save_gold_data_to_csv(data)
    plot_gold_price_trend()

if __name__ == "__main__":
    main() 