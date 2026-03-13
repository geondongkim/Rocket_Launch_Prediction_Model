import os
import zipfile
import subprocess
import pandas as pd

def fetch_historical_launches():
    # The Kaggle dataset ID for "All Space Missions from 1957"
    dataset_name = "agilesif/space-missions-1957"
    output_dir = "data/raw"
    os.makedirs(output_dir, exist_ok=True)
    expected_file = os.path.join(output_dir, "Space_Corrected.csv")
    
    if os.path.exists(expected_file):
        print(f"Dataset already exists at {expected_file}. Skipping download.")
        df = pd.read_csv(expected_file)
        print(f"Total historical launches fetched: {len(df)}")
        return

    print("Attempting to download Kaggle dataset using kaggle CLI...")
    try:
        # Try to run the kaggle cli
        result = subprocess.run(
            ["kaggle", "datasets", "download", "-d", dataset_name, "-p", output_dir, "--unzip"], 
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("Dataset downloaded and extracted successfully.")
        else:
            print("Kaggle CLI failed. Error output:")
            print(result.stdout)
            print(result.stderr)
            raise Exception("Kaggle CLI download failed.")
    except Exception as e:
        print(f"Error: {e}")
        print("--------------------------------------------------")
        print("Please ensure you have your Kaggle API credentials set up.")
        print("1. Go to kaggle.com -> Account -> Create New API Token (kaggle.json)")
        print("2. Place kaggle.json in ~/.kaggle/ (or C:\\Users\\<Username>\\.kaggle\\)")
        print("Alternatively, download manually from:")
        print("https://www.kaggle.com/datasets/agilesif/space-missions-1957")
        print("and extract 'Space_Corrected.csv' into 'data/raw/'")
        print("--------------------------------------------------")
        return
    
    if os.path.exists(expected_file):
        df = pd.read_csv(expected_file)
        print(f"Total historical launches fetched: {len(df)}")
    else:
        print(f"Could not find the expected file {expected_file} after download.")

if __name__ == "__main__":
    fetch_historical_launches()
