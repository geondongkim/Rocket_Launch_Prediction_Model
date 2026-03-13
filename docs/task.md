# 로켓 발사 예측 모델 프로젝트 태스크

## 1. 프로젝트 기획 및 환경 설정
- [x] 데이터 소스 및 API 요금 분석 (완료)
- [x] 프로젝트 디렉토리 구조 및 가상 환경 생성
- [x] 필요 라이브러리 설치 (pandas, scikit-learn, requests 등)

## 2. 데이터 수집
- [x] r/SpaceX API를 통한 SpaceX 발사 기록 수집
- [x] Kaggle 'All Space Missions from 1957' CSV 데이터셋 다운로드 및 로드
- [x] Open-Meteo API를 통한 발사 시점/위치의 과거 날씨 데이터 수집

## 3. 데이터 전처리 및 탐색적 데이터 분석 (EDA)
- [x] 발사 기록 데이터 병합 및 정제 (결측치 처리, 날짜/위치 포맷 통일)
- [x] 날씨 데이터와 발사 기록 데이터 결합
- [x] EDA를 통한 변수 간 상관관계 파악 및 시각화

## 4. 모델 개발
- [x] 피처 엔지니어링 (발사 월, 발사장 위치, 기상 상태 등 파생 변수 생성)
- [x] 데이터셋 분리 (학습용 / 테스트용)
- [x] 다양한 머신러닝 모델 학습 및 비교 (Logistic Regression, SVM, Random Forest, XGBoost, LightGBM 등)
- [ ] 하이퍼파라미터 튜닝 최적화

## 5. 모델 평가 및 결과물 확보
- [x] 모델 성능 평가 (정확도, 정밀도, 재현율, F1-Score, ROC-AUC 등)
- [x] 인사이트 도출을 위한 결과 시각화 (Confusion Matrix, Feature Importance, ROC Curve)
- [x] 예측 결과를 테스트할 수 있는 간단한 추론 스크립트 작성
