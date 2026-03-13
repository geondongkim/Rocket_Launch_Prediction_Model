import pandas as pd
import requests
import os
import time
from geopy.geocoders import ArcGIS
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

def geocode_locations(locations):
    geolocator = ArcGIS(user_agent="rocket_launch_predictor", timeout=10)
    lat_lon_map = {}
    print(f"Geocoding {len(locations)} unique locations...")
    
    for loc in tqdm(locations):
        try:
            # 전체 주소 문자열로 지오코딩 시도
            location_info = geolocator.geocode(loc)
            if location_info:
                lat_lon_map[loc] = (location_info.latitude, location_info.longitude)
            else:
                # 실패 시 국가/주 단위로 축약해서 재시도
                parts = [p.strip() for p in loc.split(',')]
                fallback = ", ".join(parts[-2:]) if len(parts) >= 2 else loc
                location_info = geolocator.geocode(fallback)
                if location_info:
                    lat_lon_map[loc] = (location_info.latitude, location_info.longitude)
                else:
                    # 최후 수단: 국가명만으로 재시도
                    fallback_country = parts[-1]
                    location_info = geolocator.geocode(fallback_country)
                    if location_info:
                        lat_lon_map[loc] = (location_info.latitude, location_info.longitude)
                    else:
                        lat_lon_map[loc] = (None, None)
            time.sleep(1)  # API 요청 속도 제한 준수
        except Exception as e:
            print(f"{loc} 지오코딩 오류: {e}")
            lat_lon_map[loc] = (None, None)
            time.sleep(1)
            
    return lat_lon_map

def fetch_weather_single(row, session):
    lat, lon, date_str, location = row['latitude'], row['longitude'], row['Datum'], row['Location']
    if pd.isna(lat) or pd.isna(lon):
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
                    'Location': location,
                    'Datum': date_str,
                    "temperature_2m_mean": data["daily"].get("temperature_2m_mean", [None])[0],
                    "precipitation_sum": data["daily"].get("precipitation_sum", [None])[0],
                    "wind_speed_10m_max": data["daily"].get("wind_speed_10m_max", [None])[0]
                }
    except Exception as e:
        pass
    return None

def main():
    historical_path = 'data/raw/Space_Corrected.csv'
    if not os.path.exists(historical_path):
        print(f"File not found: {historical_path}")
        return
        
    df = pd.read_csv(historical_path)
    # 동일한 발사 위치/날짜 중복 제거
    df['Datum_YMD'] = pd.to_datetime(df['Datum'], format='mixed', utc=True).dt.strftime('%Y-%m-%d')
    unique_launches = df[['Location', 'Datum', 'Datum_YMD']].drop_duplicates()
    
    locations = unique_launches['Location'].unique()
    lat_lon_map = geocode_locations(locations)
    
    unique_launches['latitude'] = unique_launches['Location'].apply(lambda l: lat_lon_map.get(l, (None, None))[0])
    unique_launches['longitude'] = unique_launches['Location'].apply(lambda l: lat_lon_map.get(l, (None, None))[1])
    
    print(f"{len(unique_launches)}개 고유 발사 기록에 대한 날씨 데이터 수집 중...")
    
    # HTTP 커넥션 풀링 설정 (속도 향상)
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=3)
    session.mount('https://', adapter)
    
    weather_results = []
    
    # Open-Meteo 동시 요청 지원, 최대 10개 스레드 병륬 실행
    with ThreadPoolExecutor(max_workers=10) as executor:
        # 모든 작업 제시
        futures = [executor.submit(fetch_weather_single, row, session) for _, row in unique_launches.iterrows()]
        
        for future in tqdm(as_completed(futures), total=len(futures)):
            result = future.result()
            if result:
                weather_results.append(result)
                
    weather_df = pd.DataFrame(weather_results)
    
    output_dir = 'data/raw'
    os.makedirs(output_dir, exist_ok=True)
    weather_df.to_csv(os.path.join(output_dir, 'weather_data.csv'), index=False)
    print(f"Saved weather data to data/raw/weather_data.csv. Fetched {len(weather_df)} records.")

if __name__ == "__main__":
    main()
