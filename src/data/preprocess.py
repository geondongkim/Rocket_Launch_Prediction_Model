import pandas as pd
import numpy as np
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def fetch_weather_direct(lat, lon, date_str, session):
    if pd.isna(lat) or pd.isna(lon) or pd.isna(date_str):
        return None
    try:
        dt = pd.to_datetime(date_str, format='mixed', utc=True)
        ymd = dt.strftime('%Y-%m-%d')
        
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": ymd,
            "end_date": ymd,
            "daily": ["temperature_2m_mean", "precipitation_sum", "wind_speed_10m_max"]
        }
        response = session.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "daily" in data:
                return {
                    "temperature_2m_mean": data["daily"].get("temperature_2m_mean", [None])[0],
                    "precipitation_sum": data["daily"].get("precipitation_sum", [None])[0],
                    "wind_speed_10m_max": data["daily"].get("wind_speed_10m_max", [None])[0]
                }
    except Exception:
        pass
    return None

def main():
    print("Loading data...")
    spacex_path = 'data/raw/spacex_launches.csv'
    hist_path = 'data/raw/Space_Corrected.csv'
    weather_path = 'data/raw/weather_data.csv'
    
    spacex_df = pd.read_csv(spacex_path) if os.path.exists(spacex_path) else pd.DataFrame()
    hist_df = pd.read_csv(hist_path) if os.path.exists(hist_path) else pd.DataFrame()
    weather_df = pd.read_csv(weather_path) if os.path.exists(weather_path) else pd.DataFrame()

    # 1. 역사 데이터 정제
    hist_clean = pd.DataFrame()
    if not hist_df.empty:
        hist_clean['Date'] = pd.to_datetime(hist_df['Datum'], format='mixed', utc=True)
        hist_clean['Company'] = hist_df['Company Name']
        hist_clean['Location'] = hist_df['Location']
        hist_clean['Rocket'] = hist_df['Detail']
        
        # 이진 타겟: 성공=1, 나머지=0
        hist_clean['Success'] = hist_df['Status Mission'].apply(lambda x: 1 if x == 'Success' else 0)
        hist_clean['Source'] = '\uad50리데이터'
        
        # 날씨 데이터 병합
        # 병합용 키 생성
        hist_df['Date_Key'] = pd.to_datetime(hist_df['Datum'], format='mixed', utc=True)
        weather_df['Date_Key'] = pd.to_datetime(weather_df['Datum'], format='mixed', utc=True, errors='coerce')
        
        # 몹록을 Location과 Date_Key로 병합
        hist_weather_merged = pd.merge(
            hist_clean.assign(Date_Key=hist_clean['Date']),
            weather_df[['Location', 'Date_Key', 'temperature_2m_mean', 'precipitation_sum', 'wind_speed_10m_max']].dropna(subset=['Date_Key']),
            on=['Location', 'Date_Key'],
            how='left'
        )
        hist_clean = hist_weather_merged.drop(columns=['Date_Key'])

    # 2. SpaceX 데이터 정제
    spacex_clean = pd.DataFrame()
    if not spacex_df.empty:
        spacex_clean['Date'] = pd.to_datetime(spacex_df['date_utc'], utc=True)
        spacex_clean['Company'] = 'SpaceX'
        spacex_clean['Location'] = spacex_df['pad_name']
        spacex_clean['Rocket'] = spacex_df['rocket'] # ID값 기록, 이후 매핑 가능
        
        # 이진 타겟: True=1, False/NaN=0
        spacex_clean['Success'] = spacex_df['success'].apply(lambda x: 1 if x == True else 0)
        spacex_clean['Source'] = 'SpaceX API'
        
        spacex_clean['latitude'] = spacex_df['latitude']
        spacex_clean['longitude'] = spacex_df['longitude']
        
        # SpaceX doesn't have weather yet, let's fetch it inline
        print("SpaceX 발사 노선의 날씨 데이터 수집 중...")
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=3)
        session.mount('https://', adapter)
        
        weather_results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(fetch_weather_direct, row['latitude'], row['longitude'], row['Date'], session): i
                for i, row in spacex_clean.iterrows()
            }
            for future in tqdm(as_completed(futures), total=len(futures)):
                idx = futures[future]
                weather_results.append((idx, future.result()))
                
        # Assign weather results
        spacex_clean['temperature_2m_mean'] = np.nan
        spacex_clean['precipitation_sum'] = np.nan
        spacex_clean['wind_speed_10m_max'] = np.nan
        
        for idx, res in weather_results:
            if res:
                spacex_clean.at[idx, 'temperature_2m_mean'] = res['temperature_2m_mean']
                spacex_clean.at[idx, 'precipitation_sum'] = res['precipitation_sum']
                spacex_clean.at[idx, 'wind_speed_10m_max'] = res['wind_speed_10m_max']
                
        spacex_clean.drop(columns=['latitude', 'longitude'], inplace=True)

    # 3. 데이터프레임 합치
    combined_df = pd.concat([hist_clean, spacex_clean], ignore_index=True)
    
    # 4. 피처 엔지니어링
    # 연도와 월 추출
    combined_df['Year'] = combined_df['Date'].dt.year
    combined_df['Month'] = combined_df['Date'].dt.month
    combined_df['DayOfWeek'] = combined_df['Date'].dt.dayofweek
    
    # 위치 문자열에서 국가 추출 (근사치)
    combined_df['Country'] = combined_df['Location'].astype(str).apply(lambda x: x.split(',')[-1].strip())
    
    # 결측치 처리
    # 수치형 날씨 데이터는 중앙값으로 대체입력
    weather_cols = ['temperature_2m_mean', 'precipitation_sum', 'wind_speed_10m_max']
    for col in weather_cols:
        median_val = combined_df[col].median()
        combined_df[col] = combined_df[col].fillna(median_val)
        
    print(f"Combined data shape: {combined_df.shape}")
    print(f"Success rate: {combined_df['Success'].mean():.2f}")
    
    output_dir = 'data/processed'
    os.makedirs(output_dir, exist_ok=True)
    combined_df.to_csv(os.path.join(output_dir, 'model_data.csv'), index=False)
    print("Preprocessed data saved to data/processed/model_data.csv")

if __name__ == "__main__":
    main()
