# -*- coding: utf-8 -*-
"""
영화 데이터 그래프 도감 1 - 시간
KOBIS 일별 박스오피스(10위권) 데이터를 가지고,
'시간(날짜)'을 기준으로 한 그래프들을 모아두는 스트림릿 앱입니다.

■ 이 파일은 앞으로 그래프를 계속 추가할 예정이라서,
   그래프 하나하나를 '섹션'으로 나누어 두었습니다.
   새 그래프를 추가할 때는 맨 아래에 새로운 섹션을 이어 붙이면 됩니다.
"""

import pandas as pd             # 표 형태 데이터 처리에 사용
import plotly.express as px     # 플롯리(Plotly) 그래프를 쉽게 그리기 위한 라이브러리
import streamlit as st          # 화면(웹앱)을 그리는 라이브러리

CSV_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"

st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", page_icon="📈", layout="wide")


# ─────────────────────────────────────────────
# 0. 데이터 불러오기
#    (앱이 새로고침될 때마다 매번 인터넷에서 다시 받지 않도록 캐시해 둡니다.)
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="박스오피스 데이터를 불러오는 중입니다...")
def load_data() -> pd.DataFrame:
    """
    CSV 원본 열: 날짜(20250901 같은 8자리 숫자) · 순위 · 영화코드 · 영화명 ·
                일관객 · 누적관객 · 스크린수 · 상영횟수

    여기서는 '날짜'만 진짜 날짜(datetime) 타입으로 바꿔줍니다.
    나머지 숫자 열들은 원본 CSV에 이미 순수 숫자로 들어 있어서, pandas가
    자동으로 숫자 타입으로 읽어줍니다.
    """
    df = pd.read_csv(CSV_URL)

    # '날짜' 열(예: 20250901)을 진짜 날짜 타입으로 바꿉니다.
    # format="%Y%m%d"는 '연4자리+월2자리+일2자리' 형식이라는 뜻입니다.
    df["날짜"] = pd.to_datetime(df["날짜"], format="%Y%m%d")

    return df


df = load_data()

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.caption(
    "KOBIS 일별 박스오피스(TOP 10) 데이터를 가지고, "
    "'시간(날짜)'의 흐름에 따라 무엇이 달라지는지 살펴보는 그래프 모음입니다."
)
st.divider()


# ═══════════════════════════════════════════════════════════
# 섹션 1. 영화별 일별 관객수 변화 (선 그래프)
#   - 드롭다운으로 영화를 고르면, 그 영화의 날짜별 '일관객' 변화를 보여줍니다.
# ═══════════════════════════════════════════════════════════
st.header("1. 영화별 일별 관객수 변화")

# 드롭다운(selectbox)에 넣을 영화 이름 목록을 만듭니다.
# 가나다순으로 정렬해서, 원하는 영화를 더 쉽게 찾도록 합니다.
movie_options = sorted(df["영화명"].unique())

selected_movie = st.selectbox(
    "그래프로 볼 영화를 선택하세요",
    options=movie_options,
)

# 고른 영화의 기록만 뽑아서, 날짜 순서대로 정렬합니다.
movie_df = df[df["영화명"] == selected_movie].sort_values("날짜")

# 플롯리(Plotly) 선 그래프를 만듭니다.
# hover_data에 넣은 항목들은 마우스를 올렸을 때 함께 보여줍니다.
fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,  # 각 날짜마다 점을 찍어서 더 잘 보이게 합니다.
    labels={"날짜": "날짜", "일관객": "일일 관객수(명)"},
    hover_data={"날짜": "|%Y-%m-%d", "일관객": ":,"},  # 날짜는 보기 좋게, 관객수는 천단위 콤마로
)
fig1.update_layout(
    hovermode="x unified",  # 마우스를 올리면 그 날짜의 값이 위쪽에 정리되어 보입니다.
    yaxis_title="일일 관객수(명)",
    xaxis_title="날짜",
)

st.plotly_chart(fig1, use_container_width=True)

# '이 그래프로 알 수 있는 것' 자리 — 나중에 직접 문장을 채워 넣는 칸입니다.
st.text_input(
    "💡 이 그래프로 알 수 있는 것",
    key="insight_section1",
    placeholder="예: 개봉 첫 주에 관객수가 가장 높고, 이후 점차 줄어드는 흐름을 보인다.",
)

st.divider()


# ═══════════════════════════════════════════════════════════
# 섹션 2. 일관객 합계 상위 5편의 날짜별 추이 (여러 영화 비교)
#   - 이 기간 '일관객' 합계가 가장 큰 5편을 골라, 하나의 선 그래프에
#     색으로 구분해서 보여줍니다. 범례를 클릭하면 해당 영화를 껐다 켤 수 있습니다.
# ═══════════════════════════════════════════════════════════
st.header("2. 일관객 합계 TOP 5 영화의 날짜별 추이")

# 영화별로 '일관객'을 모두 더해서, 합계가 가장 큰 5편을 뽑습니다.
top5_total = (
    df.groupby("영화명")["일관객"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)
top5_movie_names = top5_total.index.tolist()

# 위에서 고른 5편에 해당하는 행만 골라서, 날짜 순서대로 정렬합니다.
top5_df = df[df["영화명"].isin(top5_movie_names)].sort_values("날짜")

# color="영화명"을 지정하면, 영화마다 다른 색깔의 선이 그려지고
# 오른쪽에 범례가 자동으로 생깁니다. 플롯리 그래프는 기본적으로
# 범례를 클릭하면 그 선을 화면에서 껐다 켤 수 있습니다.
fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    labels={"날짜": "날짜", "일관객": "일일 관객수(명)", "영화명": "영화"},
    hover_data={"날짜": "|%Y-%m-%d", "일관객": ":,"},
)
fig2.update_layout(
    hovermode="x unified",
    yaxis_title="일일 관객수(명)",
    xaxis_title="날짜",
    legend_title_text="영화(클릭해서 켜고 끄기)",
)

st.plotly_chart(fig2, use_container_width=True)

st.text_input(
    "💡 이 그래프로 알 수 있는 것",
    key="insight_section2",
    placeholder="예: 영화마다 관객수가 몰리는 시기가 다르며, 개봉 시점이 서로 겹치지 않는 편이다.",
)

st.divider()


# ═══════════════════════════════════════════════════════════
# 섹션 3. (다음 그래프를 위한 자리)
#   앞으로 그래프를 추가할 때는 이 아래에 새로운 st.header(...)부터 시작해서
#   위 섹션들과 같은 형태(그래프 + '이 그래프로 알 수 있는 것' 입력칸)로 이어 붙이면 됩니다.
# ═══════════════════════════════════════════════════════════
# st.header("3. (다음 그래프 제목)")
# ... 그래프 코드 ...
# st.text_input("💡 이 그래프로 알 수 있는 것", key="insight_section3", placeholder="...")
