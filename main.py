import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------
# 페이지 설정
# ------------------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide",
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

st.markdown(
    """
데이터 출처: [KOBIS 박스오피스 요약표](https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv)

최근 1년간 박스오피스 10위권에 든 영화 가운데, 해당 기간에 개봉한 216편의 요약 데이터입니다.
장르가 여러 개(`|`로 구분) 표기된 영화는 첫 번째 장르만 사용합니다.
"""
)


# ------------------------------------------------------------
# 데이터 로드
# ------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # 첫 번째 장르만 사용
    df["genre_main"] = df["genre"].astype(str).str.split("|").str[0]

    # 개봉일(여덟 자리 숫자) -> datetime
    df["openDt"] = pd.to_datetime(df["openDt"], format="%Y%m%d", errors="coerce")

    return df


df = load_data()


# ------------------------------------------------------------
# 그래프 1. 장르별 영화 편수 - 도넛 그래프
# ------------------------------------------------------------
st.header("1. 장르별 영화 편수")

genre_counts = (
    df["genre_main"]
    .value_counts()
    .reset_index()
)
genre_counts.columns = ["genre", "count"]

fig_donut = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.5,
)
fig_donut.update_traces(
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
)
fig_donut.update_layout(
    legend_title_text="장르",
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig_donut, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** ")
st.info("여기에 그래프 해석 문장을 작성하세요.")

st.divider()


# ------------------------------------------------------------
# 그래프 2. 장르 > 영화 트리맵 (크기: 총 관객수)
# ------------------------------------------------------------
st.header("2. 장르 안의 영화별 총 관객수")

fig_treemap = px.treemap(
    df,
    path=["genre_main", "movieNm"],
    values="total_audi",
)
fig_treemap.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객: %{value:,}명<extra></extra>",
)
fig_treemap.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig_treemap, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** ")
st.info("여기에 그래프 해석 문장을 작성하세요.")

st.divider()
