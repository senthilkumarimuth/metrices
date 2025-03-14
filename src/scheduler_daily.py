import subprocess
import time
from run_all_reports import main as all_reports_main

def git_workflow():
    try:
        # Add files
        subprocess.run(["git", "add", "."], check=True)
        # Commit
        subprocess.run(["git", "commit", "-m", f"Auto commit {time.ctime()}"], check=True)
        # Optional: Push
        subprocess.run(["git", "push"], check=True)
        print("Git workflow completed")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

# Test it
all_reports_main()
git_workflow()