import os
from dotenv import load_dotenv
load_dotenv()

import kagglehub
import shutil
import pandas as pd

def download_dataset():
    dataset_handle = "agirlcoding/all-space-missions-from-1957"
    dest_path = "data/raw/"
    
    # 1. 최신 방식으로 데이터셋 다운로드 (자동 인증 및 캐싱)
    print(f"Attempting to download {dataset_handle} using kagglehub...")
    path = kagglehub.dataset_download(dataset_handle)
    
    # 2. 다운로드된 파일을 프로젝트의 data/raw/ 폴더로 복사
    os.makedirs(dest_path, exist_ok=True)
    filename = "Space_Corrected.csv"
    
    # 캐시 폴더에서 실제 프로젝트 폴더로 파일 이동/복사
    src_file = os.path.join(path, filename)
    if os.path.exists(src_file):
        shutil.copy(src_file, os.path.join(dest_path, filename))
        print(f"Successfully moved {filename} to {dest_path}")
        
        df = pd.read_csv(os.path.join(dest_path, filename))
        print(f"Total historical launches fetched: {len(df)}")
    else:
        print(f"Error: {filename} not found in downloaded files.")

if __name__ == "__main__":
    download_dataset()
