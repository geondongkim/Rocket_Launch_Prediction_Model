import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def main():
    print("Loading preprocessed data for EDA...")
    data_path = 'data/processed/model_data.csv'
    if not os.path.exists(data_path):
        print("Model data not found! Run preprocess.py first.")
        return
        
    df = pd.read_csv(data_path)
    
    # 출력 디렉토리 생성
    out_dir = 'reports/figures'
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. 타겟 변수 분포 시각화
    plt.figure(figsize=(6, 4))
    sns.countplot(data=df, x='Success', palette='Set2')
    plt.title('임무 성공 여부 분포 (1=성공, 0=실패)')
    plt.savefig(os.path.join(out_dir, 'success_distribution.png'))
    plt.close()
    
    # 2. 수치형 피처 상관관계 행렬
    num_cols = ['Success', 'Year', 'Month', 'temperature_2m_mean', 'precipitation_sum', 'wind_speed_10m_max']
    corr = df[num_cols].corr()
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, fmt=".2f")
    plt.title('수치형 피처 상관관계 행렬')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'correlation_matrix.png'))
    plt.close()
    
    # 3. 국가별 성공률
    # 시각화 명확성을 위해 발사 횟수 50회 이상인 국가만 필터링
    country_counts = df['Country'].value_counts()
    significant_countries = country_counts[country_counts >= 50].index
    
    df_sig_country = df[df['Country'].isin(significant_countries)]
    success_by_country = df_sig_country.groupby('Country')['Success'].mean().sort_values(ascending=False)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=success_by_country.index, y=success_by_country.values, palette='Blues_d')
    plt.title('국가별 임무 성공률 (최소 50회 이상 발사)')
    plt.ylabel('성공률')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'success_rate_by_country.png'))
    plt.close()
    
    # 4. 연도별 성공률 추이
    success_by_year = df.groupby('Year')['Success'].agg(['mean', 'count'])
    # 합리적인 수로 발사가 있는 연도만 플롯
    success_by_year = success_by_year[success_by_year['count'] > 5]
    
    plt.figure(figsize=(12, 5))
    plt.plot(success_by_year.index, success_by_year['mean'], marker='o', linestyle='-', color='indigo')
    plt.title('연도별 임무 성공률 추이')
    plt.xlabel('연도')
    plt.ylabel('성공률')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'success_rate_over_time.png'))
    plt.close()

    print(f"EDA 완료. 4개 차트가 {out_dir}에 저장되었습니다")

if __name__ == "__main__":
    main()
