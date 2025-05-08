import streamlit as st
import pandas as pd
import datetime
import pickle
from utils import load_sheet
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import numpy as np

st.set_page_config(page_title="매출 예측 시스템", layout="wide")
st.title("📊 교타쿠 매출 예측 시스템")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1amJjEsYbWHEnJuy6em3phSStqtyE4f9ryak0I0KBNf4/edit?usp=sharing"

# 🔁 모델 재학습 함수
def train_model_from_df(df):
    X = []
    y = []
    days = ["월", "화", "수", "목", "금", "토", "일"]

    for _, row in df.iterrows():
        try:
            inputs = [
                row["울산이자카야 검색량"],
                row["울산달동술집 검색량"],
                row["울산술집 검색량"],
                row["울산삼산술집 검색량"],
                row["플레이스 유입수"]
            ]
            weekday_index = days.index(row["요일"])
            day_encoded = [1 if i == weekday_index else 0 for i in range(7)]
            X.append(inputs + day_encoded)
            y.append(row["매출"])
        except:
            continue

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)

# 🔄 새로고침 + 재학습 버튼
if st.button("🔄 데이터 새로고침 및 모델 재학습"):
    st.cache_data.clear()
    try:
        df_temp = load_sheet(SHEET_URL, st.secrets["gcp_service_account"])
        train_model_from_df(df_temp)
    except Exception as e:
        st.error(f"❌ 새로고침 중 오류 발생: {e}")
        st.stop()
    st.rerun()

# 🔐 Google Sheets 데이터 로드
try:
    df = load_sheet(SHEET_URL, st.secrets["gcp_service_account"])
except KeyError:
    st.error("❌ secrets.toml에 'gcp_service_account'가 없습니다.")
    st.stop()
except Exception as e:
    st.error(f"❌ Google Sheets 로딩 중 오류 발생: {e}")
    st.stop()

st.subheader("📋 실제 데이터")
st.dataframe(df)

# 모델 로드 (없으면 학습)
try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
except:
    st.warning("⚠️ 모델 파일이 없어 새로 학습합니다.")
    train_model_from_df(df)
    model = pickle.load(open("model.pkl", "rb"))

# 오차 계산
def get_error_margin(df, model):
    X = []
    y = []
    days = ["월", "화", "수", "목", "금", "토", "일"]

    for _, row in df.iterrows():
        try:
            inputs = [
                row["울산이자카야 검색량"],
                row["울산달동술집 검색량"],
                row["울산술집 검색량"],
                row["울산삼산술집 검색량"],
                row["플레이스 유입수"]
            ]
            weekday_index = days.index(row["요일"])
            day_encoded = [1 if i == weekday_index else 0 for i in range(7)]
            X.append(inputs + day_encoded)
            y.append(row["매출"])
        except:
            continue

    if len(X) == 0:
        return 0.1

    y_pred = model.predict(X)
    mae = mean_absolute_error(y, y_pred)
    return mae / np.mean(y)

# 🔢 사용자 입력
col1, col2, col3, col4, col5 = st.columns(5)
value1 = col1.number_input("울산이자카야 검색량", value=10)
value2 = col2.number_input("울산달동술집 검색량", value=10)
value3 = col3.number_input("울산술집 검색량", value=10)
value4 = col4.number_input("울산삼산술집 검색량", value=50)
value5 = col5.number_input("플레이스 유입수", value=200)

# 📅 날짜 → 요일 변환
selected_date = st.date_input("예측할 날짜를 선택하세요", value=datetime.date.today())
days = ["월", "화", "수", "목", "금", "토", "일"]
weekday_index = selected_date.weekday()
day_encoded = [1 if i == weekday_index else 0 for i in range(7)]

# 📈 예측 수행
X_input = [[value1, value2, value3, value4, value5] + day_encoded]
prediction = model.predict(X_input)[0]
rounded = round(prediction)

# 📉 오차 적용
error_ratio = get_error_margin(df, model)
min_pred = round(rounded * (1 - error_ratio))
max_pred = round(rounded * (1 + error_ratio))

# ✅ 결과 출력 (만원 단위)
st.success(f"💰 예측 매출: {rounded}만원 (오차범위: {min_pred}만원 ~ {max_pred}만원 / ±{round(error_ratio * 100)}%)")
