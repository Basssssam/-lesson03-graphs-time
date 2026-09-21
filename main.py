import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------------------------------------
# 기본 설정
# ---------------------------------------------------------

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")


# ---------------------------------------------------------
# 데이터 불러오기
# ---------------------------------------------------------

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/kobis_daily.csv"
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜 열을 문자열로 읽은 뒤 실제 날짜 타입으로 변환합니다.
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d",
    )

    # 숫자 열을 숫자형으로 변환합니다.
    numeric_columns = [
        "순위",
        "영화코드",
        "일관객",
        "누적관객",
        "스크린수",
        "상영횟수",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    return df


try:
    df = load_data()

except Exception as e:
    st.error(
        "데이터를 불러오는 중 문제가 발생했습니다.\n\n"
        f"오류 내용: {e}"
    )
    st.stop()


# ---------------------------------------------------------
# 데이터 기본 정보
# ---------------------------------------------------------

min_date = df["날짜"].min()
max_date = df["날짜"].max()

st.caption(
    f"데이터 기간: {min_date:%Y년 %m월 %d일} ~ "
    f"{max_date:%Y년 %m월 %d일} · "
    f"총 {len(df):,}개 기록"
)


# =========================================================
# 그래프 1. 영화별 일관객 변화
# =========================================================

st.divider()

st.header("1. 영화별 일관객 변화")

st.write(
    "영화를 하나 선택하면 해당 영화의 날짜별 일관객 변화를 확인할 수 있습니다."
)


# 영화 목록을 가나다순으로 정렬합니다.
movie_names = sorted(
    df["영화명"].dropna().unique().tolist()
)


selected_movie = st.selectbox(
    "🎬 영화를 선택하세요",
    movie_names,
)


# 선택한 영화만 필터링합니다.
movie_df = df[
    df["영화명"] == selected_movie
].sort_values("날짜")


# ---------------------------------------------------------
# Plotly 선 그래프
# ---------------------------------------------------------

fig = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"{selected_movie} · 날짜별 일관객",
    labels={
        "날짜": "날짜",
        "일관객": "일관객수(명)",
    },
)


# 마우스를 올렸을 때 날짜와 관객수가 표시됩니다.
fig.update_traces(
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}"
        "<br>일관객: %{y:,}명"
        "<extra></extra>"
    )
)


fig.update_layout(
    hovermode="x unified",
    height=500,
)


st.plotly_chart(
    fig,
    use_container_width=True,
)


# ---------------------------------------------------------
# 그래프 해석 문구 자리
# ---------------------------------------------------------

st.markdown("**이 그래프로 알 수 있는 것**")

st.info(
    "선택한 영화의 날짜별 일관객 변화를 통해 "
    "관객이 언제 증가하고 감소했는지 살펴볼 수 있습니다."
)


# =========================================================
# 앞으로 추가할 그래프 영역
# =========================================================

st.divider()

st.header("2. 다음 그래프")

st.caption(
    "앞으로 새로운 영화 데이터 그래프를 이 영역에 추가합니다."
)


# =========================================================
# 다음 그래프를 추가할 때 사용할 자리
# =========================================================

# st.subheader("2-1. 새로운 그래프 제목")
#
# 새로운 그래프 코드를 이곳에 작성합니다.
#
# st.plotly_chart(
#     fig,
#     use_container_width=True,
# )
#
# st.markdown("**이 그래프로 알 수 있는 것**")
#
# st.info(
#     "이 그래프에서 발견할 수 있는 내용을 한 문장으로 설명합니다."
# )
