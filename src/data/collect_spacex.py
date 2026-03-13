import requests
import pandas as pd
import os

# SpaceX 발사 데이터 v4 API 엔드포인트
API_URL = "https://api.spacexdata.com/v4/launches"

def fetch_spacex_launches():
    print("Fetching SpaceX launch data...")
    response = requests.get(API_URL)
    response.raise_for_status()
    data = response.json()
    
    # 필요한 필드만 추출
    launches = []
    for item in data:
        launch = {
            'id': item.get('id'),
            'name': item.get('name'),
            'date_utc': item.get('date_utc'),
            'date_unix': item.get('date_unix'),
            'success': item.get('success'),
            'rocket': item.get('rocket'),
            'launchpad': item.get('launchpad'),
            'payloads': item.get('payloads', []),
            'details': item.get('details')
        }
        launches.append(launch)
        
    df = pd.DataFrame(launches)
    print(f"SpaceX 발사 데이터 수집 완료: {len(df)}건")
    
    # 발사 패드 좌표 정보 추가 수집
    print("발사 패드 상세 정보 수집 중...")
    pad_url = "https://api.spacexdata.com/v4/launchpads"
    pad_response = requests.get(pad_url)
    pad_response.raise_for_status()
    pads_data = pad_response.json()
    
    pads = {}
    for pad in pads_data:
        pads[pad['id']] = {
            'pad_name': pad.get('name'),
            'latitude': pad.get('latitude'),
            'longitude': pad.get('longitude')
        }
        
    # 발사 패드 정보를 발사 데이터프레임에 병합
    def get_pad_info(pad_id, info_type):
        if pd.isna(pad_id) or pad_id not in pads:
            return None
        return pads[pad_id].get(info_type)
        
    df['pad_name'] = df['launchpad'].apply(lambda x: get_pad_info(x, 'pad_name'))
    df['latitude'] = df['launchpad'].apply(lambda x: get_pad_info(x, 'latitude'))
    df['longitude'] = df['launchpad'].apply(lambda x: get_pad_info(x, 'longitude'))
    
    output_dir = 'data/raw'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'spacex_launches.csv')
    df.to_csv(output_path, index=False)
    print(f"SpaceX data saved to {output_path}")

if __name__ == "__main__":
    fetch_spacex_launches()
