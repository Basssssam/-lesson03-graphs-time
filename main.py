import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")

st.caption(
    "KOBIS 일별 박스오피스 10위권 데이터를 시간의 흐름에 따라 살펴봅니다."
)


# =========================================================
# 데이터 주소
# =========================================================

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/kobis_daily.csv"
)


# =========================================================
# 데이터 불러오기
# =========================================================

@st.cache_data
def load_data():

    df = pd.read_csv(DATA_URL)

    # -----------------------------------------------------
    # 날짜를 실제 날짜 형식으로 변환
    # -----------------------------------------------------

    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d",
        errors="coerce",
    )

    # -----------------------------------------------------
    # 숫자 열을 숫자형으로 변환
    # -----------------------------------------------------

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

    # 날짜가 잘못된 행 제거
    df = df.dropna(subset=["날짜"])

    return df


# =========================================================
# 데이터 가져오기
# =========================================================

try:
    df = load_data()

except Exception as e:

    st.error(
        "데이터를 불러오지 못했습니다.\n\n"
        f"오류 내용: {e}"
    )

    st.stop()


# =========================================================
# 데이터 기본 정보
# =========================================================

min_date = df["날짜"].min()
max_date = df["날짜"].max()

movie_count = df["영화코드"].nunique()

st.caption(
    f"데이터 기간: "
    f"{min_date:%Y-%m-%d} ~ {max_date:%Y-%m-%d}"
    f" · 영화 {movie_count:,}편"
)


# =========================================================
# 그래프 1
# 영화별 일관객 변화
# =========================================================

st.divider()

st.header("1. 영화별 일관객 변화")

st.write(
    "영화를 선택하면 그 영화가 10위권에 기록된 날짜별 "
    "일관객 변화를 볼 수 있습니다."
)


# =========================================================
# 영화 목록 만들기
# =========================================================

movie_info = (
    df.groupby(
        ["영화코드", "영화명"],
        as_index=False,
    )
    .agg(
        기록일수=("날짜", "nunique")
    )
)

# 기록일수가 많은 영화부터 정렬
movie_info = movie_info.sort_values(
    by=["기록일수", "영화명"],
    ascending=[False, True],
)

movie_codes = (
    movie_info["영화코드"]
    .astype(int)
    .tolist()
)


def movie_label(movie_code):
    """드롭다운에 표시할 영화 이름"""

    row = movie_info[
        movie_info["영화코드"] == movie_code
    ].iloc[0]

    return (
        f"{row['영화명']} "
        f"· {row['기록일수']}일 기록"
    )


selected_movie_code = st.selectbox(
    "🎬 영화를 선택하세요",
    options=movie_codes,
    index=0,
    format_func=movie_label,
)


selected_movie_row = movie_info[
    movie_info["영화코드"] == selected_movie_code
].iloc[0]

selected_movie_name = selected_movie_row["영화명"]
selected_record_days = int(
    selected_movie_row["기록일수"]
)


# =========================================================
# 선택한 영화 데이터
# =========================================================

movie_df = (
    df[
        df["영화코드"] == selected_movie_code
    ]
    .sort_values("날짜")
    .copy()
)


# =========================================================
# 선택한 영화 정보
# =========================================================

first_date = movie_df["날짜"].min()
last_date = movie_df["날짜"].max()

st.caption(
    f"📌 {selected_movie_name} · "
    f"10위권 기록 {selected_record_days}일 · "
    f"{first_date:%Y-%m-%d} ~ {last_date:%Y-%m-%d}"
)


if selected_record_days == 1:

    st.warning(
        "이 영화는 현재 데이터에서 10위권에 하루만 기록되어 "
        "변화를 나타내는 선이 없습니다. "
        "드롭다운에서 기록일수가 많은 영화를 선택해 보세요."
    )


# =========================================================
# 그래프 1 만들기
# =========================================================

fig = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
)


fig.update_layout(
    title=f"{selected_movie_name} · 날짜별 일관객",
    height=500,

    margin=dict(
        l=20,
        r=20,
        t=70,
        b=30,
    ),

    xaxis_title="날짜",
    yaxis_title="일관객수(명)",

    hovermode="closest",
)


# 마우스를 올렸을 때 표시할 내용
fig.update_traces(
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}"
        "<br>"
        "일관객: %{y:,}명"
        "<extra></extra>"
    )
)


# =========================================================
# 그래프 1 날짜 축
# =========================================================

if selected_record_days == 1:

    selected_day = movie_df["날짜"].iloc[0]

    start_day = selected_day - pd.Timedelta(days=1)
    end_day = selected_day + pd.Timedelta(days=1)

    fig.update_xaxes(
        type="date",
        range=[
            start_day,
            end_day,
        ],
        dtick=24 * 60 * 60 * 1000,
        tick0=start_day,
        tickformat="%m/%d",
    )

else:

    date_span = (
        movie_df["날짜"].max()
        - movie_df["날짜"].min()
    ).days

    if date_span <= 14:

        fig.update_xaxes(
            type="date",
            dtick=24 * 60 * 60 * 1000,
            tickformat="%m/%d",
        )

    elif date_span <= 60:

        fig.update_xaxes(
            type="date",
            dtick=7 * 24 * 60 * 60 * 1000,
            tickformat="%m/%d",
        )

    else:

        fig.update_xaxes(
            type="date",
            tickformat="%m/%d",
        )


fig.update_yaxes(
    separatethousands=True,
)


st.plotly_chart(
    fig,
    use_container_width=True,
)


# =========================================================
# 그래프 1 해석
# =========================================================

st.markdown(
    "### 이 그래프로 알 수 있는 것"
)

st.info(
    "영화의 날짜별 일관객 변화를 통해 "
    "시간이 지나면서 관객수가 어떻게 증가하거나 감소했는지 살펴볼 수 있습니다."
)


# =========================================================
# 그래프 2
# 기간 일관객 합계 상위 5편
# =========================================================

st.divider()

st.header("2. 기간 일관객 합계 상위 5편")

st.write(
    "전체 데이터 기간 동안 일관객의 합계가 큰 5편의 "
    "날짜별 관객 변화를 한 그래프에서 비교합니다."
)


# =========================================================
# 영화별 일관객 합계 계산
# =========================================================

top_5_movies = (
    df.groupby(
        ["영화코드", "영화명"],
        as_index=False,
    )
    .agg(
        기간일관객합계=("일관객", "sum")
    )
    .sort_values(
        "기간일관객합계",
        ascending=False,
    )
    .head(5)
)


# 상위 5편의 영화코드
top_5_codes = top_5_movies["영화코드"].tolist()


# =========================================================
# 상위 5편의 날짜별 데이터
# =========================================================

top_5_df = (
    df[
        df["영화코드"].isin(top_5_codes)
    ]
    [
        [
            "날짜",
            "영화코드",
            "영화명",
            "일관객",
        ]
    ]
    .sort_values(
        ["날짜", "영화명"]
    )
    .copy()
)


# =========================================================
# 그래프 2
# =========================================================

fig_top5 = px.line(
    top_5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,

    labels={
        "날짜": "날짜",
        "일관객": "일관객수(명)",
        "영화명": "영화",
    },
)


fig_top5.update_layout(
    title="기간 일관객 합계 상위 5편 · 날짜별 일관객",
    height=600,

    margin=dict(
        l=20,
        r=20,
        t=70,
        b=30,
    ),

    xaxis_title="날짜",
    yaxis_title="일관객수(명)",

    hovermode="x unified",

    # 범례를 그래프 오른쪽에 표시
    legend=dict(
        title="영화",
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.02,
    ),
)


# =========================================================
# 마우스 오버
# =========================================================

fig_top5.update_traces(
    hovertemplate=(
        "%{fullData.name}"
        "<br>"
        "날짜: %{x|%Y-%m-%d}"
        "<br>"
        "일관객: %{y:,}명"
        "<extra></extra>"
    )
)


# =========================================================
# 날짜 축
# =========================================================

fig_top5.update_xaxes(
    type="date",
    tickformat="%m/%d",
)


# =========================================================
# Y축
# =========================================================

fig_top5.update_yaxes(
    separatethousands=True,
)


# =========================================================
# 그래프 출력
# =========================================================

st.plotly_chart(
    fig_top5,
    use_container_width=True,
)


# =========================================================
# 상위 5편 합계 표시
# =========================================================

st.markdown("#### 기간 일관객 합계")

summary_data = top_5_movies.copy()

summary_data["기간일관객합계"] = (
    summary_data["기간일관객합계"]
    .astype(int)
)

summary_data = summary_data[
    [
        "영화명",
        "기간일관객합계",
    ]
]

st.dataframe(
    summary_data,
    use_container_width=True,
    hide_index=True,
    column_config={
        "영화명": st.column_config.TextColumn(
            "영화명",
        ),
        "기간일관객합계": st.column_config.NumberColumn(
            "기간 일관객 합계",
            format="%d명",
        ),
    },
)


# =========================================================
# 그래프 2 해석
# =========================================================

st.markdown(
    "### 이 그래프로 알 수 있는 것"
)

st.info(
    "이 기간 동안 일관객 합계가 큰 5편의 관객 규모와 "
    "날짜별 관객 변화 양상을 한눈에 비교할 수 있습니다."
)


# =========================================================
# 그래프 3
# =========================================================

st.divider()

st.header("3. 다음 그래프")

st.write(
    "앞으로 새로운 그래프를 이 영역에 추가합니다."
)


# ---------------------------------------------------------
# 다음 그래프를 추가할 자리
# ---------------------------------------------------------

# 예시:
#
# st.subheader("3-1. 그래프 제목")
#
# fig = ...
#
# st.plotly_chart(
#     fig,
#     use_container_width=True,
# )
#
# st.markdown("### 이 그래프로 알 수 있는 것")
#
# st.info(
#     "이 그래프를 통해 알 수 있는 내용을 한 문장으로 작성합니다."
# )


# =========================================================
# 데이터 일부 보기
# =========================================================

with st.expander("📋 데이터 일부 보기"):

    st.dataframe(
        df.head(20),
        use_container_width=True,
        hide_index=True,
    )
