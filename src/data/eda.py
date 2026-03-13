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
    
    # Create output directory
    out_dir = 'reports/figures'
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Target Variable Distribution
    plt.figure(figsize=(6, 4))
    sns.countplot(data=df, x='Success', palette='Set2')
    plt.title('Distribution of Mission Success (1=Success, 0=Failure)')
    plt.savefig(os.path.join(out_dir, 'success_distribution.png'))
    plt.close()
    
    # 2. Correlation Matrix for numerical features
    num_cols = ['Success', 'Year', 'Month', 'temperature_2m_mean', 'precipitation_sum', 'wind_speed_10m_max']
    corr = df[num_cols].corr()
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, fmt=".2f")
    plt.title('Correlation Matrix of Numerical Features')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'correlation_matrix.png'))
    plt.close()
    
    # 3. Success Rate by Country
    # Filter countries with at least 50 launches for clearer visualization
    country_counts = df['Country'].value_counts()
    significant_countries = country_counts[country_counts >= 50].index
    
    df_sig_country = df[df['Country'].isin(significant_countries)]
    success_by_country = df_sig_country.groupby('Country')['Success'].mean().sort_values(ascending=False)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=success_by_country.index, y=success_by_country.values, palette='Blues_d')
    plt.title('Mission Success Rate by Country (Min 50 Launches)')
    plt.ylabel('Success Rate')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'success_rate_by_country.png'))
    plt.close()
    
    # 4. Success over Years
    success_by_year = df.groupby('Year')['Success'].agg(['mean', 'count'])
    # Only plot years with at least a few launches
    success_by_year = success_by_year[success_by_year['count'] > 5]
    
    plt.figure(figsize=(12, 5))
    plt.plot(success_by_year.index, success_by_year['mean'], marker='o', linestyle='-', color='indigo')
    plt.title('Mission Success Rate Over Time (Years)')
    plt.xlabel('Year')
    plt.ylabel('Success Rate')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'success_rate_over_time.png'))
    plt.close()

    print(f"EDA completed. 4 plots saved to {out_dir}")

if __name__ == "__main__":
    main()
