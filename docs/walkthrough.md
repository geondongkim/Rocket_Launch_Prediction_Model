# 로켓 발사 예측 모델 프로젝트 회고 (Walkthrough)

과거 NASA/SpaceX 등의 로켓 발사 기록과 해당 시점의 날씨 데이터를 결합하여 **머신러닝 기반 발사 성공 예측 모델** 구축을 완료했습니다.

## 1. 사용된 데이터 원천
* **SpaceX API**: r/SpaceX v4 API를 통해 최근 발사 기록 및 발사장 상세 위치(위도/경도) 수집.
* **Kaggle**: 1957년부터의 전 세계 우주 임무 기록이 담긴 'All Space Missions from 1957' 데이터 4,324건 수집.
* **Open-Meteo API**: 위 두 데이터의 발사 시점과 위치를 바탕으로, 해당 날짜의 기상 관측 데이터(평균 온도, 강수량, 최대 풍속) 수집 후 병합 (`ArcGIS` geocoder 사용으로 제한 없이 빠른 위경도 맵핑 구현).

## 2. 예측 모델 개발 결과
모델은 Logistic Regression, SVM, Random Forest, XGBoost, LightGBM 5가지를 비교 평가했습니다. 가장 성능이 좋았던 모델은 놀랍게도 **Logistic Regression**과 **LightGBM**입니다.

### 성능 지표 비교
데이터 세트의 대부분(약 90%)이 성공 사례인 불균형 데이터라는 점을 고려하여 향후 예측력(ROC-AUC)과 F1 스코어를 중점적으로 확인했습니다.

| 모델 | Accuracy (정확도) | F1-Score | ROC-AUC |
|---|---|---|---|
| **LogisticRegression** | **90.3%** | **0.949** | **0.734** |
| **LightGBM** | 89.9% | 0.946 | 0.711 |
| **RandomForest** | 89.7% | 0.944 | 0.708 |
| **XGBoost** | 89.5% | 0.943 | 0.695 |
| **SVM** | 90.0% | 0.947 | 0.661 |

## 3. 데이터 시각화 및 인사이트 도출

````carousel
![Mission Success Rate Over Time](/absolute/c:/Users/EL035/dataschool/Rocket_Launch_Prediction_Model/reports/figures/success_rate_over_time.png)
<!-- slide -->
![Mission Success Rate by Country](/absolute/c:/Users/EL035/dataschool/Rocket_Launch_Prediction_Model/reports/figures/success_rate_by_country.png)
<!-- slide -->
![Feature Importance (Random Forest)](/absolute/c:/Users/EL035/dataschool/Rocket_Launch_Prediction_Model/reports/figures/feature_imp_randomforest.png)
<!-- slide -->
![Feature Importance (LightGBM)](/absolute/c:/Users/EL035/dataschool/Rocket_Launch_Prediction_Model/reports/figures/feature_imp_lightgbm.png)
<!-- slide -->
![ROC Curve Comparison](/absolute/c:/Users/EL035/dataschool/Rocket_Launch_Prediction_Model/reports/figures/roc_comparison.png)
````

**주요 인사이트:**
1. **발사 연도(Year)의 중요성**: 모든 의사결정나무 모델(RF, LightGBM) 특성 중요도(Feature Importance)에서 `Year`가 압도적으로 1위를 차지했습니다. 시간이 지날수록 기술 발전으로 인해 성공률이 극적으로 향상되었기 때문입니다.
2. **국가와 기업**: 러시아, 미국 순으로 안정적인 성공률을 보인 반면, 특정 발사장과 운영 기업 간에도 성공률의 차이가 분명하게 드러납니다.
3. **날씨 변수**: `temperature_2m_mean` (온도)와 `wind_speed_10m_max` (최대 풍속)이 예측에 꽤 기여를 합니다. 다만 극단적인 악천후 시에는 발사 자체가 보류(Scrub)되기 때문에, 실패 데이터를 설명하는 절대적인 요인보다는 부수적 요인으로 작용하고 있습니다.

## 4. 모델 테스트 (추론)
완성된 모델을 테스트해 볼 수 있도록 [src/models/inference.py](file:///c:/Users/EL035/dataschool/Rocket_Launch_Prediction_Model/src/models/inference.py)를 작성했습니다.
```bash
# 기본 데이터(임의의 기상 조건과 SpaceX 기준)로 예측 테스트
python src/models/inference.py --model logisticregression 
```

**✅ 프로젝트가 지정해주신 Github 리포지토리(`geondongkim/Rocket_Launch_Prediction_Model`)에 성공적으로 푸시되었습니다.**
