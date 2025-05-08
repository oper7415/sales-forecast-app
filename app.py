
import streamlit as st
import pandas as pd
from utils import load_sheet
import pickle

st.set_page_config(page_title="매출 예측 시스템", layout="wide")

st.title("📊 교타쿠 매출 예측 시스템")

# Google Sheets URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1amJjEsYbWHEnJuy6em3phSStqtyE4f9ryak0I0KBNf4/edit?usp=sharing"

# Load data
df = load_sheet(SHEET_URL)
st.subheader("📅 실제 데이터")
st.dataframe(df)

# Load model
st.subheader("🔮 매출 예측")
model = pickle.load(open("model.pkl", "rb"))

col1, col2, col3, col4, col5 = st.columns(5)
value1 = col1.number_input("울산이자카야 검색량", value=10)
value2 = col2.number_input("울산달동술집 검색량", value=10)
value3 = col3.number_input("울산술집 검색량", value=10)
value4 = col4.number_input("울산삼산술집 검색량", value=50)
value5 = col5.number_input("플레이스 유입수", value=200)
day = st.selectbox("요일", ["월", "화", "수", "목", "금", "토", "일"])

# 요일 인코딩
days = ["월", "화", "수", "목", "금", "토", "일"]
day_encoded = [1 if d == day else 0 for d in days]

X_input = [[value1, value2, value3, value4, value5] + day_encoded]
prediction = model.predict(X_input)[0]

st.success(f"💰 예측 매출: {round(prediction):,} 원")
