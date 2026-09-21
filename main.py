import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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


first_date = movie_df["날짜"].min()
last_date = movie_df["날짜"].max()

st.caption(
    f"📌 {selected_movie_name} · "
    f"10위권 기록 {selected_record_days}일 · "
    f"{first_date:%Y-%m-%d} ~ {last_date:%Y-%m-%d}"
)


# =========================================================
# 하루만 기록된 영화 안내
# =========================================================

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


# =========================================================
# 그래프 1 마우스 오버
# =========================================================

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


# =========================================================
# 그래프 1 Y축
# =========================================================

fig.update_yaxes(
    separatethousands=True,
)


# =========================================================
# 그래프 1 출력
# =========================================================

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
# 영화별 일관객 합계
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


top_5_codes = top_5_movies["영화코드"].tolist()


# =========================================================
# 상위 5편 날짜별 데이터
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
# 그래프 2 만들기
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
# 그래프 2 마우스 오버
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
# 그래프 2 날짜 축
# =========================================================

fig_top5.update_xaxes(
    type="date",
    tickformat="%m/%d",
)


# =========================================================
# 그래프 2 Y축
# =========================================================

fig_top5.update_yaxes(
    separatethousands=True,
)


# =========================================================
# 그래프 2 출력
# =========================================================

st.plotly_chart(
    fig_top5,
    use_container_width=True,
)


# =========================================================
# 상위 5편 합계 표
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
# 날짜별 10위권 일관객 합계
# =========================================================

st.divider()

st.header("3. 날짜별 10위권 일관객 합계")

st.write(
    "매일 박스오피스 10위권에 오른 영화들의 일관객을 "
    "모두 더해 날짜별 전체 관객 규모를 살펴봅니다."
)


# =========================================================
# 날짜별 일관객 합계
# =========================================================

daily_audience = (
    df.groupby(
        "날짜",
        as_index=False,
    )
    .agg(
        일관객합계=("일관객", "sum")
    )
    .sort_values("날짜")
)


# =========================================================
# 일관객 합계가 큰 날짜 3일
# =========================================================

top_3_days = (
    daily_audience
    .sort_values(
        "일관객합계",
        ascending=False,
    )
    .head(3)
    .copy()
)


# =========================================================
# 그래프 3 영역 그래프
# =========================================================

fig_daily = go.Figure()


fig_daily.add_trace(
    go.Scatter(
        x=daily_audience["날짜"],
        y=daily_audience["일관객합계"],

        mode="lines",

        name="10위권 일관객 합계",

        line=dict(
            color="#4C78A8",
            width=3,
        ),

        fill="tozeroy",

        fillcolor="rgba(76, 120, 168, 0.25)",

        hovertemplate=(
            "날짜: %{x|%Y-%m-%d}"
            "<br>"
            "10위권 일관객 합계: %{y:,}명"
            "<extra></extra>"
        ),
    )
)


# =========================================================
# 그래프 위에 상위 3일 표시
# =========================================================

rank_colors = [
    "#E74C3C",
    "#F39C12",
    "#8E44AD",
]

rank_labels = [
    "1위",
    "2위",
    "3위",
]


for i, (_, row) in enumerate(
    top_3_days.iterrows()
):

    st_date = row["날짜"]

    fig_daily.add_annotation(
        x=st_date,

        y=row["일관객합계"],

        text=(
            f"<b>{rank_labels[i]}</b>"
            f"<br>"
            f"{st_date:%m/%d}"
            f"<br>"
            f"{row['일관객합계']:,}명"
        ),

        showarrow=True,

        arrowhead=2,

        arrowsize=1,

        arrowwidth=2,

        arrowcolor=rank_colors[i],

        ax=0,

        ay=[
            -70,
            -120,
            -70,
        ][i],

        bgcolor="white",

        bordercolor=rank_colors[i],

        borderwidth=2,

        borderpad=5,

        font=dict(
            color=rank_colors[i],
            size=13,
        ),
    )


# =========================================================
# 그래프 3 레이아웃
# =========================================================

fig_daily.update_layout(
    title="날짜별 10위권 일관객 합계",

    height=600,

    margin=dict(
        l=20,
        r=20,
        t=90,
        b=30,
    ),

    xaxis_title="날짜",

    yaxis_title="10위권 일관객 합계(명)",

    hovermode="x unified",

    showlegend=False,
)


# =========================================================
# 그래프 3 날짜 축
# =========================================================

date_span = (
    daily_audience["날짜"].max()
    - daily_audience["날짜"].min()
).days


if date_span <= 14:

    fig_daily.update_xaxes(
        type="date",
        dtick=24 * 60 * 60 * 1000,
        tickformat="%m/%d",
    )

elif date_span <= 60:

    fig_daily.update_xaxes(
        type="date",
        dtick=7 * 24 * 60 * 60 * 1000,
        tickformat="%m/%d",
    )

else:

    fig_daily.update_xaxes(
        type="date",
        tickformat="%m/%d",
    )


# =========================================================
# 그래프 3 Y축
# =========================================================

fig_daily.update_yaxes(
    separatethousands=True,
)


# =========================================================
# 그래프 3 출력
# =========================================================

st.plotly_chart(
    fig_daily,
    use_container_width=True,
)


# =========================================================
# 상위 3일 표
# =========================================================

st.markdown(
    "#### 일관객 합계가 가장 컸던 3일"
)

top_3_table = top_3_days[
    [
        "날짜",
        "일관객합계",
    ]
].copy()

top_3_table["날짜"] = (
    top_3_table["날짜"]
    .dt.strftime("%Y-%m-%d")
)

top_3_table.insert(
    0,
    "구분",
    [
        "1위",
        "2위",
        "3위",
    ],
)

st.dataframe(
    top_3_table,
    use_container_width=True,
    hide_index=True,
    column_config={
        "구분": st.column_config.TextColumn(
            "구분",
        ),
        "날짜": st.column_config.TextColumn(
            "날짜",
        ),
        "일관객합계": st.column_config.NumberColumn(
            "10위권 일관객 합계",
            format="%d명",
        ),
    },
)


# =========================================================
# 그래프 3 해석
# =========================================================

st.markdown(
    "### 이 그래프로 알 수 있는 것"
)

st.info(
    "날짜별 10위권 일관객 합계를 통해 "
    "전체적으로 영화관 관객이 많았던 날과 적었던 날의 차이를 살펴볼 수 있습니다."
)


# =========================================================
# 그래프 4
# 기간 일관객 합계 TOP 10
# =========================================================

st.divider()

st.header("4. 기간 일관객 합계 TOP 10")

st.write(
    "전체 데이터 기간 동안 영화별 일관객을 모두 더해 "
    "관객수가 많은 영화 10편을 비교합니다."
)


# =========================================================
# 영화별 일관객 합계 + 기록일수
# =========================================================

top_10_movies = (
    df.groupby(
        ["영화코드", "영화명"],
        as_index=False,
    )
    .agg(
        기간일관객합계=("일관객", "sum"),
        기록일수=("날짜", "nunique"),
    )
    .sort_values(
        "기간일관객합계",
        ascending=False,
    )
    .head(10)
    .copy()
)


# =========================================================
# 그래프 4 가로 막대그래프
# =========================================================

fig_top10 = px.bar(
    top_10_movies,

    x="기간일관객합계",

    y="영화명",

    orientation="h",

    text="기간일관객합계",

    labels={
        "기간일관객합계": "기간 일관객 합계(명)",
        "영화명": "영화",
    },
)


# =========================================================
# 그래프 4 막대 설정
# =========================================================

fig_top10.update_traces(
    texttemplate="%{x:,}명",

    textposition="outside",

    marker_color="#4C78A8",

    customdata=top_10_movies[
        ["기록일수"]
    ].values,

    hovertemplate=(
        "<b>%{y}</b>"
        "<br>"
        "기간 일관객 합계: %{x:,}명"
        "<br>"
        "10위권 기록일수: %{customdata[0]}일"
        "<extra></extra>"
    ),
)


# =========================================================
# 그래프 4 레이아웃
# =========================================================

fig_top10.update_layout(
    title="기간 일관객 합계 TOP 10",

    height=600,

    margin=dict(
        l=20,
        r=120,
        t=70,
        b=30,
    ),

    xaxis_title="기간 일관객 합계(명)",

    yaxis_title="",

    showlegend=False,
)


# =========================================================
# 관객이 많은 영화가 위에 오도록
# =========================================================

fig_top10.update_yaxes(
    categoryorder="array",

    categoryarray=top_10_movies[
        "영화명"
    ].tolist(),

    autorange="reversed",
)


# =========================================================
# 그래프 4 X축
# =========================================================

fig_top10.update_xaxes(
    separatethousands=True,
)


# =========================================================
# 그래프 4 출력
# =========================================================

st.plotly_chart(
    fig_top10,
    use_container_width=True,
)


# =========================================================
# 그래프 4 해석
# =========================================================

st.markdown(
    "### 이 그래프로 알 수 있는 것"
)

st.info(
    "이 기간 동안 10위권에 기록된 일관객을 모두 합쳐 "
    "영화별 누적 관객 규모를 비교하고, 각 영화가 10위권에 "
    "며칠 동안 기록되었는지도 함께 살펴볼 수 있습니다."
)


# =========================================================
# 데이터 일부 보기
# =========================================================

st.divider()

with st.expander("📋 데이터 일부 보기"):

    st.dataframe(
        df.head(20),
        use_container_width=True,
        hide_index=True,
    )
