```python
import streamlit as st
import pandas as pd
import altair as alt


# --------------------------------------------------
# 기본 설정
# --------------------------------------------------

st.set_page_config(
    page_title="서울 연평균 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

DATA_URL = (
    "https://raw.githubusercontent.com/"
    "greatsong/modudata/main/data/seoul.csv"
)


# --------------------------------------------------
# 제목
# --------------------------------------------------

st.title("🌡️ 서울의 100년 연평균 기온 변화")
st.write(
    "서울의 일별 기온 데이터를 연도별로 평균 내어 "
    "장기간의 기온 변화를 살펴봅니다."
)


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    # 날짜를 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

    # 평균기온을 숫자로 변환
    df["평균기온"] = pd.to_numeric(
        df["평균기온"],
        errors="coerce"
    )

    # 필요한 데이터만 남김
    df = df.dropna(subset=["날짜", "평균기온"])

    # 연도 추출
    df["연도"] = df["날짜"].dt.year

    return df


try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.exception(e)
    st.stop()


# --------------------------------------------------
# 연평균 기온 계산
# --------------------------------------------------

yearly = (
    df.groupby("연도", as_index=False)["평균기온"]
    .mean()
    .rename(columns={"평균기온": "연평균기온"})
)

yearly["연평균기온"] = yearly["연평균기온"].round(2)


# --------------------------------------------------
# 100년 구간 선택
# --------------------------------------------------

min_year = int(yearly["연도"].min())
max_year = int(yearly["연도"].max())

st.sidebar.header("📊 기간 선택")

default_start = max(min_year, max_year - 99)

start_year, end_year = st.sidebar.slider(
    "그래프에 표시할 기간",
    min_value=min_year,
    max_value=max_year,
    value=(default_start, max_year),
    step=1
)

chart_data = yearly[
    (yearly["연도"] >= start_year)
    & (yearly["연도"] <= end_year)
].copy()


# --------------------------------------------------
# 요약 정보
# --------------------------------------------------

if not chart_data.empty:
    first_row = chart_data.iloc[0]
    last_row = chart_data.iloc[-1]

    change = last_row["연평균기온"] - first_row["연평균기온"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "시작 연도",
            f"{int(first_row['연도'])}년",
            f"{first_row['연평균기온']:.1f}℃"
        )

    with col2:
        st.metric(
            "마지막 연도",
            f"{int(last_row['연도'])}년",
            f"{last_row['연평균기온']:.1f}℃"
        )

    with col3:
        st.metric(
            "기간 내 기온 변화",
            f"{change:+.1f}℃"
        )


st.divider()


# --------------------------------------------------
# 그래프
# --------------------------------------------------

st.subheader(
    f"📈 {start_year}년 ~ {end_year}년 연평균 기온"
)

chart = (
    alt.Chart(chart_data)
    .mark_line(
        color="#e4572e",
        strokeWidth=3,
        point=True
    )
    .encode(
        x=alt.X(
            "연도:Q",
            title="연도",
            axis=alt.Axis(
                format="d",
                labelAngle=0,
                tickCount=10
            )
        ),
        y=alt.Y(
            "연평균기온:Q",
            title="연평균 기온 (℃)",
            scale=alt.Scale(zero=False)
        ),
        tooltip=[
            alt.Tooltip(
                "연도:Q",
                title="연도",
                format="d"
            ),
            alt.Tooltip(
                "연평균기온:Q",
                title="연평균 기온",
                format=".2f"
            )
        ]
    )
    .properties(
        height=500
    )
)

st.altair_chart(
    chart,
    use_container_width=True
)


# --------------------------------------------------
# 안내
# --------------------------------------------------

st.caption(
    "※ 일별 평균기온을 연도별로 평균하여 계산했습니다. "
    "데이터 출처: 제공된 서울 기상 관측 CSV"
)


# --------------------------------------------------
# 데이터 표
# --------------------------------------------------

with st.expander("연도별 평균기온 데이터 보기"):
    st.dataframe(
        chart_data,
        use_container_width=True,
        hide_index=True
    )
```
