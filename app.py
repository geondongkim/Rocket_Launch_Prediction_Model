"""
로켓 발사 예측 모델 - Flask 웹 대시보드
"""
import os
import base64
import joblib
import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 프로젝트 루트 디렉토리 기준 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIGURES_DIR = os.path.join(BASE_DIR, 'reports', 'figures')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')


def img_to_base64(filename: str) -> str | None:
    """PNG 파일을 base64 인코딩된 문자열로 변환합니다."""
    path = os.path.join(FIGURES_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def load_model_comparison() -> list[dict]:
    """모델 성능 비교 CSV를 로드합니다."""
    csv_path = os.path.join(REPORTS_DIR, 'model_comparison.csv')
    if not os.path.exists(csv_path):
        return []
    df = pd.read_csv(csv_path)
    # 숫자 컬럼 반올림
    for col in ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']:
        if col in df.columns:
            df[col] = df[col].round(4)
    return df.to_dict(orient='records')


def get_available_models() -> list[str]:
    """models/ 디렉토리에서 사용 가능한 모델 목록을 반환합니다."""
    if not os.path.exists(MODELS_DIR):
        return []
    return [f.replace('_model.pkl', '') for f in os.listdir(MODELS_DIR) if f.endswith('_model.pkl')]


# ─── 라우트 ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """홈 대시보드 — 모델 성능 비교표 및 주요 인사이트"""
    model_data = load_model_comparison()
    # 최고 성능 모델 (ROC-AUC 기준)
    best_model = model_data[0] if model_data else None
    return render_template('index.html', model_data=model_data, best_model=best_model)


@app.route('/eda')
def eda():
    """탐색적 데이터 분석(EDA) 시각화 페이지"""
    charts = {
        'success_distribution': {
            'title': '임무 성공/실패 분포',
            'desc': '전체 데이터셋에서 성공(1)과 실패(0) 레이블의 분포를 보여줍니다. '
                    '데이터의 약 90%가 성공 사례로 심각한 클래스 불균형이 존재합니다.',
            'img': img_to_base64('success_distribution.png'),
        },
        'correlation_matrix': {
            'title': '수치형 피처 상관관계 행렬',
            'desc': 'Year(연도)가 성공 여부와 가장 높은 양의 상관관계를 보입니다. '
                    '시간이 갈수록 기술 발전으로 성공률이 높아졌음을 의미합니다.',
            'img': img_to_base64('correlation_matrix.png'),
        },
        'success_rate_by_country': {
            'title': '국가별 임무 성공률 (최소 50회 발사)',
            'desc': '발사 50회 이상인 국가만 필터링했습니다. 러시아, 미국 등 주요 우주 강국의 '
                    '성공률 차이를 비교할 수 있습니다.',
            'img': img_to_base64('success_rate_by_country.png'),
        },
        'success_rate_over_time': {
            'title': '연도별 임무 성공률 추이',
            'desc': '1957년 이후 전체 우주 발사의 성공률 변화 추이입니다. '
                    '1960~70년대의 낮은 성공률에서 현대로 올수록 90% 이상으로 급격히 개선되었습니다.',
            'img': img_to_base64('success_rate_over_time.png'),
        },
    }
    return render_template('eda.html', charts=charts)


@app.route('/models')
def model_results():
    """모델 평가 결과 — ROC 곡선, 혼동 행렬, 피처 중요도"""
    model_names = ['logisticregression', 'svm', 'randomforest', 'xgboost', 'lightgbm']
    model_labels = {
        'logisticregression': 'Logistic Regression',
        'svm': 'SVM',
        'randomforest': 'Random Forest',
        'xgboost': 'XGBoost',
        'lightgbm': 'LightGBM',
    }

    # 혼동 행렬 (5개)
    confusion_matrices = []
    for name in model_names:
        img = img_to_base64(f'cm_{name}.png')
        if img:
            confusion_matrices.append({'name': model_labels[name], 'img': img})

    # 피처 중요도 (트리 모델 3개)
    feature_importances = []
    for name in ['randomforest', 'xgboost', 'lightgbm']:
        img = img_to_base64(f'feature_imp_{name}.png')
        if img:
            feature_importances.append({'name': model_labels[name], 'img': img})

    roc_img = img_to_base64('roc_comparison.png')
    model_data = load_model_comparison()

    return render_template(
        'model_results.html',
        roc_img=roc_img,
        confusion_matrices=confusion_matrices,
        feature_importances=feature_importances,
        model_data=model_data,
    )


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """인터랙티브 발사 성공 예측 페이지"""
    available_models = get_available_models()
    result = None

    if request.method == 'POST':
        try:
            model_name = request.form.get('model_name', 'logisticregression')
            launch_data = {
                'Year':               [int(request.form['year'])],
                'Month':              [int(request.form['month'])],
                'DayOfWeek':          [int(request.form['day_of_week'])],
                'Country':            [request.form['country'].strip()],
                'Company_Grp':        [request.form['company'].strip()],
                'temperature_2m_mean': [float(request.form['temperature'])],
                'precipitation_sum':  [float(request.form['precipitation'])],
                'wind_speed_10m_max': [float(request.form['wind_speed'])],
            }

            model_path = os.path.join(MODELS_DIR, f'{model_name.lower()}_model.pkl')
            if not os.path.exists(model_path):
                result = {'error': f'모델 파일을 찾을 수 없습니다: {model_name}'}
            else:
                pipeline = joblib.load(model_path)
                df = pd.DataFrame(launch_data)
                prediction = int(pipeline.predict(df)[0])
                prob = float(pipeline.predict_proba(df)[0][1]) if hasattr(pipeline, 'predict_proba') else None

                result = {
                    'model': model_name.upper(),
                    'prediction': prediction,
                    'label': '성공 🚀' if prediction == 1 else '실패 ❌',
                    'probability': round(prob * 100, 2) if prob is not None else None,
                    'input': launch_data,
                }
        except Exception as e:
            result = {'error': f'예측 오류: {str(e)}'}

    return render_template('predict.html', available_models=available_models, result=result)


@app.route('/api/predict', methods=['POST'])
def api_predict():
    """JSON API 예측 엔드포인트"""
    try:
        data = request.get_json(force=True)
        model_name = data.get('model_name', 'logisticregression')
        required_fields = ['Year', 'Month', 'DayOfWeek', 'Country', 'Company_Grp',
                           'temperature_2m_mean', 'precipitation_sum', 'wind_speed_10m_max']

        # 필수 필드 검증
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({'error': f'필수 필드 누락: {missing}'}), 400

        launch_data = {field: [data[field]] for field in required_fields}

        model_path = os.path.join(MODELS_DIR, f'{model_name.lower()}_model.pkl')
        if not os.path.exists(model_path):
            return jsonify({'error': f'모델을 찾을 수 없습니다: {model_name}'}), 404

        pipeline = joblib.load(model_path)
        df = pd.DataFrame(launch_data)
        prediction = int(pipeline.predict(df)[0])
        prob = float(pipeline.predict_proba(df)[0][1]) if hasattr(pipeline, 'predict_proba') else None

        return jsonify({
            'model': model_name.upper(),
            'prediction': prediction,
            'result': '성공' if prediction == 1 else '실패',
            'success_probability': round(prob * 100, 2) if prob is not None else None,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
