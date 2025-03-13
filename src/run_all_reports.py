import sys
import os

# Add the directory containing the scripts to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the main functions from each script
from fii_dii_report import main as run_fii_dii_report
from dollar_vs_inr import main as run_dollar_vs_inr
from gold_price_india import main as run_gold_price_india

def main():
    # Run each script's main function
    print("Running FII/DII Report...")
    run_fii_dii_report()
    
    print("Running Dollar vs INR Report...")
    run_dollar_vs_inr()
    
    print("Running Gold Price India Report...")
    run_gold_price_india()

if __name__ == "__main__":
    main()
