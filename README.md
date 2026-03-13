# 🚀 Rocket Launch Prediction Model

과거 로켓 발사 기록(성공/실패)과 발사 당시의 기상 데이터를 결합하여 **머신러닝으로 로켓 발사 성공 여부를 예측**하는 파이프라인 및 Flask 웹 애플리케이션입니다.

---

## 📋 목차

- [프로젝트 개요](#프로젝트-개요)
- [데이터 소스](#데이터-소스)
- [프로젝트 구조](#프로젝트-구조)
- [설치 및 실행](#설치-및-실행)
- [모델 성능](#모델-성능)
- [주요 인사이트](#주요-인사이트)
- [모델 추론 테스트](#모델-추론-테스트)

---

## 프로젝트 개요

이 프로젝트는 1957년 이후 전 세계 우주 임무 데이터와 SpaceX API, 기상 데이터를 통합하여 로켓 발사의 성공 가능성을 예측합니다.

**주요 과제:**
- 다중 소스 데이터 수집 및 통합 파이프라인 구축
- 불균형 데이터(성공 약 90%) 처리 전략 적용
- 5가지 분류 모델 비교 평가
- Flask 기반 예측 웹 인터페이스 제공

---

## 데이터 소스

| 소스 | 설명 | 비용 |
|------|------|------|
| **r/SpaceX API (v4)** | 최근 SpaceX 발사 기록, 로켓 제원, 발사장 위도/경도 | 무료 |
| **Kaggle - All Space Missions from 1957** | 1957년 이후 전 세계 4,324건의 우주 임무 기록 CSV | 무료 |
| **Open-Meteo Historical Weather API** | 발사 시점·위치 기반 기상 데이터 (온도, 강수량, 풍속) | 무료 (비상업적) |

---

## 프로젝트 구조

```
Rocket_Launch_Prediction_Model/
├── app.py                    # Flask 웹 애플리케이션 진입점
├── requirements.txt          # 의존 패키지 목록
│
├── data/
│   ├── raw/                  # 원본 수집 데이터
│   │   ├── Space_Corrected.csv
│   │   ├── spacex_launches.csv
│   │   └── weather_data.csv
│   └── processed/            # 전처리 완료 데이터
│       ├── model_data.csv
│       ├── X_test.csv
│       └── y_test.csv
│
├── src/
│   ├── data/
│   │   ├── collect_spacex.py      # SpaceX API 데이터 수집
│   │   ├── collect_historical.py  # Kaggle CSV 데이터 로드
│   │   ├── collect_weather.py     # Open-Meteo 기상 데이터 수집
│   │   ├── preprocess.py          # 데이터 병합 및 전처리
│   │   └── eda.py                 # 탐색적 데이터 분석
│   └── models/
│       ├── train.py               # 모델 학습 및 비교
│       ├── evaluate.py            # 모델 성능 평가
│       └── inference.py           # 단일 예측 추론 스크립트
│
├── models/                   # 학습된 모델 저장 (.pkl)
├── reports/
│   ├── model_comparison.csv  # 모델별 성능 지표 비교
│   └── figures/              # 시각화 결과 이미지
│
├── templates/                # Flask HTML 템플릿
│   ├── base.html
│   ├── index.html
│   ├── eda.html
│   ├── predict.html
│   └── model_results.html
├── static/
│   └── style.css
└── docs/
    ├── task.md               # 프로젝트 태스크 체크리스트
    ├── implementation_plan.md # 구현 계획 및 API 분석
    └── walkthrough.md        # 프로젝트 회고 및 결과 정리
```

---

## 설치 및 실행

### 1. 가상환경 생성 및 활성화

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. 의존 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 데이터 수집 (선택)

```bash
python src/data/collect_spacex.py
python src/data/collect_historical.py
python src/data/collect_weather.py
python src/data/preprocess.py
```

### 4. 모델 학습

```bash
python src/models/train.py
python src/models/evaluate.py
```

### 5. Flask 웹 앱 실행

```bash
python app.py
```

브라우저에서 `http://localhost:5000` 접속

---

## 모델 성능

데이터의 약 90%가 성공 사례인 불균형 데이터임을 고려하여 **F1-Score**와 **ROC-AUC**를 핵심 지표로 평가했습니다.

| 모델 | Accuracy | F1-Score | ROC-AUC |
|------|----------|----------|---------|
| **Logistic Regression** | **90.3%** | **0.949** | **0.734** |
| SVM | 90.0% | 0.947 | 0.661 |
| LightGBM | 89.9% | 0.946 | 0.711 |
| Random Forest | 89.7% | 0.944 | 0.708 |
| XGBoost | 89.5% | 0.943 | 0.695 |

> **최고 성능 모델**: Logistic Regression (Accuracy 90.3%, ROC-AUC 0.734)

---

## 주요 인사이트

1. **발사 연도(Year)의 압도적 중요성**  
   Random Forest, LightGBM 등 트리 기반 모델의 Feature Importance에서 `Year`가 1위. 기술 발전에 따라 시간이 지날수록 성공률이 극적으로 향상된 패턴 반영.

2. **국가 및 기업의 영향**  
   러시아, 미국의 안정적 성공률이 두드러지며, 특정 발사장·운영 기업 간 성공률 차이가 유의미하게 나타남.

3. **기상 변수의 역할**  
   `temperature_2m_mean`(평균 온도)과 `wind_speed_10m_max`(최대 풍속)이 예측에 기여하나, 극단적 악천후 시 발사 자체가 보류(Scrub)되기 때문에 실패의 절대 요인보다는 부수적 요인으로 작용.

---

## 모델 추론 테스트

학습된 모델로 단일 예측을 수행할 수 있습니다.

```bash
# Logistic Regression 모델로 예측 테스트
python src/models/inference.py --model logisticregression

# LightGBM 모델로 예측 테스트
python src/models/inference.py --model lightgbm
```

---

## 기술 스택

| 분류 | 라이브러리 |
|------|-----------|
| 데이터 처리 | `pandas`, `numpy` |
| 머신러닝 | `scikit-learn`, `xgboost`, `lightgbm` |
| 시각화 | `matplotlib`, `seaborn` |
| 웹 프레임워크 | `flask` |
| 지오코딩 | `geopy` |
| 기타 | `requests`, `joblib`, `python-dotenv` |
