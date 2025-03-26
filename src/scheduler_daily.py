import subprocess
import time
from run_all_reports import main as all_reports_main
import os
from custom_dirs import RootDirectory
from nifty50_gainers_losers import process_and_save_data

def git_workflow():
    try:
        print(f"Current directory: {os.getcwd()}")
        # Set the repo path (replace with your actual path)
        repo_path = RootDirectory.path
        os.chdir(repo_path)
        print(f"Switched to: {os.getcwd()}")
        # check git is accessible
        subprocess.run(["git", "--version"], check=True)
        # Add files
        subprocess.run(["git", "add", "."], check=True)
        # Commit
        subprocess.run(["git", "commit", "-m", f"Auto commit {time.ctime()}"], check=True)
        # Optional: Push
        subprocess.run(["git", "push"], check=True)
        print("Git workflow completed")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

def main():
    try:
        # Run all existing reports
        all_reports_main()
        
        # Fetch Nifty 50 data
        print("Fetching Nifty 50 data...")
        process_and_save_data()
        print("Nifty 50 data fetched successfully")
        
        # Run git workflow
        git_workflow()
    except Exception as e:
        print(f"Error in main workflow: {e}")

if __name__ == "__main__":
    main()