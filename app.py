
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# PAGE CONFIG
st.set_page_config(
    page_title="StockVision | Analytics",
    page_icon="📈",
    layout="wide"
)

# CUSTOM DESIGN

# PREMIUM DARK BACKGROUND THEME

st.markdown("""
<style>

/* Main Background */
.stApp {
    background: linear-gradient(
        135deg,
        #080E1B 0%,
        #101B30 50%,
        #080E1B 100%
    );
    color: #F1F5F9;
}

/* Main content spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0B1425;
    border-right: 1px solid #26364D;
}

/* Headings */
h1, h2, h3 {
    color: #F8FAFC !important;
    font-weight: 700;
}

/* KPI Cards */
[data-testid="stMetric"] {
    background: linear-gradient(
        145deg,
        #172943,
        #101D32
    );
    border: 1px solid #29415F;
    border-radius: 16px;
    padding: 22px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.25);
}

/* Metric Labels */
[data-testid="stMetricLabel"] {
    color: #A5B4C8;
}

/* Metric Values */
[data-testid="stMetricValue"] {
    color: #38D6C5;
}

/* Buttons */
.stButton > button {
    background: #173B55;
    color: white;
    border: 1px solid #38D6C5;
    border-radius: 10px;
}

/* Input Fields */
.stSelectbox, .stDateInput {
    border-radius: 10px;
}

/* Dividers */
hr {
    border-color: #26364D;
}

/* Plotly Chart Containers */
div[data-testid="stPlotlyChart"] {
    background: #101D32;
    border: 1px solid #263B56;
    border-radius: 15px;
    padding: 10px;
}

/* Footer */
footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# SIDEBAR
st.sidebar.title("📈 StockVision")
st.sidebar.caption("Market Intelligence Platform")
st.sidebar.divider()

st.sidebar.subheader("Navigation")
page = st.sidebar.radio(
    "Select Section",
    ["Market Overview", "Stock Analysis"]
)

st.sidebar.divider()
st.sidebar.info("Data Source: Historical CSV Dataset")

# LOAD DATA
file_path = "stock_dataset/AAPL.csv"

if not os.path.exists(file_path):
    st.error("AAPL.csv not found in stock_dataset folder.")
    st.stop()

df = pd.read_csv(file_path)

# CLEAN DATA
df.columns = df.columns.str.strip()

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

for col in ["Open", "High", "Low", "Close", "Volume"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["Date", "Close"])
df = df.sort_values("Date").drop_duplicates("Date")

# FEATURE ENGINEERING
df["MA_50"] = df["Close"].rolling(50).mean()
df["MA_200"] = df["Close"].rolling(200).mean()

df["Daily_Return"] = df["Close"].pct_change() * 100

# HEADER
st.title("📈 StockVision")
st.markdown(
    "#### Professional Stock Market Analysis Dashboard"
)

st.caption(
    "Historical market data | Apple Inc. (AAPL) | USD"
)

st.divider()

# DATE FILTER
st.sidebar.subheader("Date Filter")

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

selected_dates = st.sidebar.date_input(
    "Select Period",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
    start_date, end_date = selected_dates

    data = df[
        (df["Date"].dt.date >= start_date) &
        (df["Date"].dt.date <= end_date)
    ].copy()
else:
    data = df.copy()

if data.empty:
    st.warning("No stock data available for selected dates.")
    st.stop()

# ADVANCED STOCK ANALYSIS PAGE

if page == "Stock Analysis":

    st.title("📊 Advanced Stock Analysis")
    st.caption("Technical indicators and risk analytics")

    st.divider()

    # CANDLESTICK CHART
    st.subheader("🕯️ Candlestick Analysis")

    candle = go.Figure()

    candle.add_trace(go.Candlestick(
        x=data["Date"],
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="AAPL"
    ))

    candle.update_layout(
        template="plotly_dark",
        height=480,
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(candle, use_container_width=True)

    st.divider()

    # DAILY RETURNS
    st.subheader("📈 Daily Returns Distribution")

    returns = data["Close"].pct_change() * 100
    returns = returns.dropna()

    fig_returns = go.Figure()

    fig_returns.add_trace(go.Histogram(
        x=returns,
        nbinsx=50,
        name="Daily Returns",
        marker_color="#00d4aa"
    ))

    fig_returns.update_layout(
        template="plotly_dark",
        height=350,
        xaxis_title="Daily Return (%)",
        yaxis_title="Frequency"
    )

    st.plotly_chart(fig_returns, use_container_width=True)

    st.divider()

    # VOLATILITY ANALYSIS
    st.subheader("⚡ Risk and Volatility Analysis")

    volatility = returns.rolling(20).std()

    fig_vol = go.Figure()

    fig_vol.add_trace(go.Scatter(
        x=data["Date"].iloc[1:],
        y=volatility,
        mode="lines",
        name="20 Day Volatility",
        line=dict(color="#ff5470", width=2)
    ))

    fig_vol.update_layout(
        template="plotly_dark",
        height=350,
        xaxis_title="Date",
        yaxis_title="Volatility (%)"
    )

    st.plotly_chart(fig_vol, use_container_width=True)

    # ANALYSIS METRICS
    st.subheader("📋 Statistical Analysis")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average Daily Return",
        f"{returns.mean():.3f}%"
    )

    col2.metric(
        "Return Volatility",
        f"{returns.std():.3f}%"
    )

    col3.metric(
        "Best Daily Return",
        f"{returns.max():.2f}%"
    )

    st.info(
        "Higher volatility indicates greater historical price fluctuation. "
        "These statistics describe historical data, not future performance."
    )

    st.stop()

    # PROFESSIONAL RISK ANALYSIS

    st.divider()

    st.title("🛡️ Risk Analysis Dashboard")

    # Use adjusted close when available
    price_column = (
        "Adj Close" if "Adj Close" in data.columns
        else "Close"
    )

    prices = pd.to_numeric(
        data[price_column], errors="coerce"
    ).dropna()

    daily_returns = prices.pct_change().dropna()

    if len(daily_returns) > 1:

        # Annualized volatility
        annual_volatility = (
            daily_returns.std() * (252 ** 0.5) * 100
        )

        # Sharpe ratio (assuming 0% risk-free rate)
        sharpe_ratio = (
            daily_returns.mean() /
            daily_returns.std()
        ) * (252 ** 0.5)

        # Maximum drawdown
        cumulative_max = prices.cummax()
        drawdown = (prices / cumulative_max) - 1
        max_drawdown = drawdown.min() * 100

        # Average daily return
        avg_return = daily_returns.mean() * 100

        st.subheader("📊 Risk Performance Indicators")

        r1, r2 = st.columns(2)
        r3, r4 = st.columns(2)

        r1.metric(
            "Annualized Volatility",
            f"{annual_volatility:.2f}%"
        )

        r2.metric(
            "Sharpe Ratio",
            f"{sharpe_ratio:.2f}"
        )

        r3.metric(
            "Maximum Drawdown",
            f"{max_drawdown:.2f}%"
        )

        r4.metric(
            "Average Daily Return",
            f"{avg_return:.3f}%"
        )

        # Drawdown chart
        st.subheader("📉 Historical Drawdown")

        drawdown_fig = go.Figure()

        drawdown_fig.add_trace(go.Scatter(
            x=data.loc[prices.index, "Date"],
            y=drawdown * 100,
            fill="tozeroy",
            name="Drawdown",
            line=dict(color="#ff5470", width=2)
        ))

        drawdown_fig.update_layout(
            template="plotly_dark",
            height=350,
            xaxis_title="Date",
            yaxis_title="Drawdown (%)"
        )

        st.plotly_chart(
            drawdown_fig,
            use_container_width=True
        )

        st.info(
            "Risk metrics are calculated using historical "
            "adjusted closing prices where available. "
            "Sharpe Ratio assumes a 0% risk-free rate and "
            "252 trading days per year."
        )

    else:
        st.warning("Not enough data for risk analysis.")



# MARKET OVERVIEW
st.subheader("Market Overview")

latest = data.iloc[-1]

previous = data.iloc[-2] if len(data) > 1 else latest

change = latest["Close"] - previous["Close"]

daily_return = latest["Daily_Return"]

# KPI CARDS
c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Latest Closing Price",
    f"${latest['Close']:.2f}",
    f"{change:+.2f}"
)

c2.metric(
    "Daily Return",
    f"{daily_return:.2f}%" if pd.notna(daily_return) else "N/A"
)

c3.metric(
    "Highest Price",
    f"${data['Close'].max():.2f}"
)

c4.metric(
    "Lowest Price",
    f"${data['Close'].min():.2f}"
)

st.divider()

# STOCK PRICE CHART
st.subheader("Stock Price Performance")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=data["Date"],
    y=data["Close"],
    mode="lines",
    name="Closing Price",
    line=dict(color="#00d4aa", width=2)
))

fig.add_trace(go.Scatter(
    x=data["Date"],
    y=data["MA_50"],
    name="MA 50",
    line=dict(color="#ffaa00", width=1.5)
))

fig.add_trace(go.Scatter(
    x=data["Date"],
    y=data["MA_200"],
    name="MA 200",
    line=dict(color="#ff5470", width=1.5)
))

fig.update_layout(
    template="plotly_dark",
    height=450,
    xaxis_title="Date",
    yaxis_title="Stock Price (USD)",
    hovermode="x unified",
    paper_bgcolor="#0b1120",
    plot_bgcolor="#111a2d"
)

st.plotly_chart(fig, use_container_width=True)

# VOLUME CHART
st.subheader("Trading Volume Analysis")

volume_fig = go.Figure()

volume_fig.add_trace(go.Bar(
    x=data["Date"],
    y=data["Volume"],
    name="Trading Volume",
    marker_color="#5271ff"
))

volume_fig.update_layout(
    template="plotly_dark",
    height=300,
    paper_bgcolor="#0b1120",
    plot_bgcolor="#111a2d",
    xaxis_title="Date",
    yaxis_title="Volume"
)

st.plotly_chart(volume_fig, use_container_width=True)

# SUMMARY
st.subheader("Market Summary")

total_return = (
    (data["Close"].iloc[-1] - data["Close"].iloc[0])
    / data["Close"].iloc[0]
) * 100

st.metric("Selected Period Return", f"{total_return:.2f}%")

st.info(
    "This dashboard analyzes historical Apple stock data. "
    "It does not provide live prices or guaranteed predictions."
)

# FOOTER
st.divider()

st.caption(
    "StockVision | Built using Python, Pandas, Streamlit and Plotly"
)
