# 로켓 발사 예측 모델 구현 계획 (Implementation Plan)

목표: 과거의 로켓 발사 기록(성공/실패)과 발사 당시의 기상 데이터를 결합하여, 향후 로켓 발사의 성공 여부를 예측하는 머신러닝 파이프라인을 구축합니다.

## API 및 데이터 소스 요금 분석 (유료 여부 확인)
사용자가 언급한 3가지 데이터 소스는 **기본적으로 모두 무료로 학업/비상업적 용도 사용이 가능**합니다. 다만 접근 방식에 차이가 있습니다.

1. **r/SpaceX API**: **무료 (오픈소스)**
   - SpaceX의 발사 기록, 로켓 제원, 발사장 정보 등을 제공하는 무료 REST API입니다. 제한 없이 사용할 수 있습니다.
2. **Open-Meteo Historical Weather API**: **무료 (비상업적 용도)**
   - 비상업적 오픈소스 프로젝트나 학업 용도의 경우 하루 10,000회 호출까지 완전 무료입니다. 로켓 발사 횟수가 수천 건이므로 하루 내에 충분히 무료로 과거 데이터를 수집할 수 있습니다.
3. **Kaggle 데이터셋 (Astronautix 대체)**: **무료**
   - 과거 우주 임무 데이터를 정리한 Kaggle의 'All Space Missions from 1957' 데이터셋(.csv)을 활용합니다.
   - 이를 통해 1957년 이후의 방대한 과거 발사 기록을 쉽게 수집하고 분석할 수 있습니다.

## 제안하는 프로젝트 구조 (Proposed Changes)

프로젝트는 데이터 수집, 전처리, 모델링 3단계로 구성됩니다.

### 데이터 파이프라인 스크립트 (`src/data/`)
- `collect_spacex.py`: r/SpaceX API와 연동해 최신 데이터 수집.
- `collect_historical.py`: Kaggle 등에서 구한 CSV 파일을 읽어들이거나, 지정된 아카이브에서 기초 데이터를 추출.
- `collect_weather.py`: 로켓 발사 시간(UTC)과 발사장 위도/경도를 바탕으로 Open-Meteo API에서 기상 데이터(풍속, 온도, 강수량 등) 풀링.
- `preprocess.py`: 위 3가지 데이터를 하나로 병합(Merge)하고 결측치를 처리하는 전처리 역할.

### ML 모델 스크립트 (`src/models/`)
- `train.py`: 전처리된 데이터를 바탕으로 다양한 머신러닝 분류기(Logistic Regression, SVM, Random Forest, XGBoost, LightGBM 등)를 학습시키고, 각 모델의 성능을 비교합니다.
- `evaluate.py`: 모델 평가 지표(Accuracy, Precision, Recall, F1-Score, ROC-AUC)를 계산합니다.
- `visualize.py`: 혼동 행렬(Confusion Matrix), ROC 곡선, 피처 중요도(Feature Importance) 등을 시각화하여 로켓 발사 성공에 중요한 요인이 무엇인지 인사이트를 도출합니다.

## 검증 계획 (Verification Plan)
- **API 응답 테스트**: 각 수집 스크립트가 200 OK 상태의 JSON을 떨어뜨리는지 샘플 확인.
- **데이터 정합성**: 최종 병합된 DataFrame에 타겟 라벨(Success/Failure)과 필수 피처(날씨, 발사장 등)가 NULL 없이 채워졌는지 검증.
- **수치적 모델 평가**: 로켓 발사 특성상 데이터 불균형(성공 압도적 다수)이 발생할 수 있으므로, 단순 정확도(Accuracy)뿐만 아니라 F1-Score와 ROC-AUC 지표로 모델의 예측 성능을 확인합니다.
