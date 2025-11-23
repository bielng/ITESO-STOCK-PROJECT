
# import streamlit as st
# import plotly.graph_objects as go
# import pandas as pd
# from datetime import datetime

# from data_loader import AlpacaAPI
# from config import STOCK_DATA, TIMEFRAME_MAP

# # ---------- Page ----------
# st.set_page_config(page_title="Stock Dashboard", layout="wide")

# # ---------- Custom CSS (AdventureWorks Style) ----------
# st.markdown(
#     """
#     <style>
#     .reportview-container {background: #0E1117;}
#     .sidebar .sidebar-content {background: #161B22;}
#     .kpi-card {
#         background: #1A1F2E;
#         padding: 18px;
#         border-radius: 16px;
#         text-align: center;
#         box-shadow: 0 4px 12px rgba(0,212,170,0.15);
#         border: 1px solid #2A2F3E;
#     }
#     .kpi-value {
#         font-size: 36px;
#         font-weight: bold;
#         color: #00D4AA;
#         margin: 0;
#     }
#     .kpi-label {
#         font-size: 14px;
#         color: #B0B8C4;
#         margin-top: 6px;
#         text-transform: uppercase;
#         letter-spacing: 1px;
#     }
#     .big-title {
#         font-size: 42px !important;
#         font-weight: bold;
#         color: #00D4AA;
#         text-align: center;
#         margin-bottom: 10px;
#     }
#     .stSelectbox > div > div {background-color: #1A1F2E; color: white;}
#     .stTextInput > div > div > input {background-color: #1A1F2E; color: white; border: 1px solid #00D4AA;}
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# # ---------- Title ----------
# st.markdown('<p class="big-title">STOCK DASHBOARD</p>', unsafe_allow_html=True)

# # ---------- Hard-coded Keys ----------
# API_KEY    = "PKWE76NAVGFRCDGOPHQA2RH33F"
# API_SECRET = "FpX7LTMiUtJGCNTrW83cEz4J1PG2XhYA2J1Ls3HfzBwf"

# # ---------- Group by Sector ----------
# SECTORS = {}
# for sym, info in STOCK_DATA.items():
#     SECTORS.setdefault(info["sector"], []).append(sym)

# # ---------- Sidebar ----------
# with st.sidebar:
#     st.markdown("### Stock Selector")

#     # Search
#     search = st.text_input("Search company...", "")
#     filtered = {
#         sym: info for sym, info in STOCK_DATA.items()
#         if search.lower() in info["name"].lower() or search.upper() in sym
#     }

#     # Sector Filter
#     sector_filter = st.selectbox("Sector", options=["All"] + list(SECTORS.keys()))
#     if sector_filter != "All":
#         filtered = {sym: info for sym, info in filtered.items() if info["sector"] == sector_filter}

#     # Symbol Select
#     symbol = st.selectbox(
#         "Select Stock",
#         options=list(filtered.keys()),
#         format_func=lambda x: f"{x} – {filtered[x]['name']}"
#     )
#     sector = filtered[symbol]["sector"]

#     period = st.selectbox("Period", options=list(TIMEFRAME_MAP.keys()))
#     chart_type = st.radio("Chart Type", ["Candlestick", "Line"])

#     st.markdown("### Indicators")
#     sma = st.checkbox("SMA 20", True)
#     ema = st.checkbox("EMA 20", True)
#     bb  = st.checkbox("Bollinger Bands", True)

#     st.markdown(f"**{symbol}** – {STOCK_DATA[symbol]['name']}\n*Sector: {sector}*")

# # ---------- Choose Feed ----------
# cfg = TIMEFRAME_MAP[period]
# feed = "sip" if cfg["days"] > 35 else "iex"
# alpaca = AlpacaAPI(API_KEY, API_SECRET, feed=feed)

# # ---------- Fetch ----------
# start_iso, end_iso = alpaca.get_market_range(cfg["days"])

# with st.spinner(f"Fetching {symbol} {period} ({feed.upper()})…"):
#     df = alpaca.get_bars(symbol, cfg["alpaca"], start_iso, end_iso)

# if df.empty:
#     if feed == "iex":
#         st.error("No data – IEX free tier only gives ~30 days. Try 1d/1wk/1mo.")
#     else:
#         st.error("No data – SIP access required. Upgrade to AlgoTrader Plus.")
#     st.stop()

# # ---------- KPIs (Top Row) ----------
# latest = df.iloc[-1]
# prev   = df.iloc[-2] if len(df) > 1 else latest
# delta  = latest["Close"] - prev["Close"]
# delta_pct = (delta / prev["Close"]) * 100

# col1, col2, col3, col4, col5 = st.columns(5)

# with col1:
#     st.markdown(
#         f"""
#         <div class="kpi-card">
#             <div class="kpi-value">${latest['Close']:.2f}</div>
#             <div class="kpi-label">Last Close</div>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

# with col2:
#     st.markdown(
#         f"""
#         <div class="kpi-card">
#             <div class="kpi-value" style="color: {'#00ff85' if delta >= 0 else '#ff4d4d'}">
#                 {delta:+.2f}
#             </div>
#             <div class="kpi-label">Change ($)</div>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

# with col3:
#     st.markdown(
#         f"""
#         <div class="kpi-card">
#             <div class="kpi-value" style="color: {'#00ff85' if delta_pct >= 0 else '#ff4d4d'}">
#                 {delta_pct:+.2f}%
#             </div>
#             <div class="kpi-label">Change (%)</div>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

# with col4:
#     st.markdown(
#         f"""
#         <div class="kpi-card">
#             <div class="kpi-value">{latest['Volume']:,.0f}</div>
#             <div class="kpi-label">Volume</div>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

# with col5:
#     st.markdown(
#         f"""
#         <div class="kpi-card">
#             <div class="kpi-value">${df['High'].max():.2f}</div>
#             <div class="kpi-label">Period High</div>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

# # ---------- Chart ----------
# fig = go.Figure()
# if chart_type == "Candlestick":
#     fig.add_trace(go.Candlestick(
#         x=df.index, open=df["Open"], high=df["High"],
#         low=df["Low"], close=df["Close"], name=symbol,
#         increasing_line_color='#00D4AA', decreasing_line_color='#ff4d4d'
#     ))
# else:
#     fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", line=dict(color="#00D4AA"), name="Close"))

# # Indicators
# if sma:
#     df["SMA20"] = df["Close"].rolling(20).mean()
#     fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], name="SMA 20", line=dict(color="#FFA500", dash="dash")))
# if ema:
#     df["EMA20"] = df["Close"].ewm(span=20).mean()
#     fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], name="EMA 20", line=dict(color="#00D4AA", dash="dot")))
# if bb:
#     df["BB_Mid"] = df["Close"].rolling(20).mean()
#     df["BB_Std"] = df["Close"].rolling(20).std()
#     df["BB_Upper"] = df["BB_Mid"] + 2 * df["BB_Std"]
#     df["BB_Lower"] = df["BB_Mid"] - 2 * df["BB_Std"]
#     fig.add_trace(go.Scatter(x=df.index, y=df["BB_Upper"], name="BB Upper", line=dict(color="#666", width=1)))
#     fig.add_trace(go.Scatter(x=df.index, y=df["BB_Lower"], name="BB Lower", line=dict(color="#666", width=1)))
#     fig.add_trace(go.Scatter(x=df.index, y=df["BB_Mid"], fill='tonexty', fillcolor='rgba(0,212,170,0.1)', name="BB Fill"))

# fig.update_layout(
#     title=f"{symbol} – {period.upper()} ({feed.upper()})",
#     xaxis_title="Date", yaxis_title="Price ($)",
#     height=600,
#     plot_bgcolor='#0E1117',
#     paper_bgcolor='#0E1117',
#     font=dict(color="#B0B8C4"),
#     legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="#161B22"),
#     xaxis=dict(gridcolor="#2A2F3E"),
#     yaxis=dict(gridcolor="#2A2F3E")
# )
# st.plotly_chart(fig, use_container_width=True)

# # ---------- Table ----------
# st.subheader("Historical Data")
# disp = df.copy()
# disp.index = disp.index.strftime("%Y-%m-%d")
# disp = disp.round(2)
# st.dataframe(disp, use_container_width=True)

# # ---------- CSV ----------
# csv = df.to_csv().encode()
# st.download_button("Download CSV", csv, f"{symbol}_{period}.csv", "text/csv")


# =============================================
# app.py – Stock Dashboard with Gemini AI (2025)
# =============================================
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import google.generativeai as genai  # Gemini API

from data_loader import AlpacaAPI
from config import STOCK_DATA, TIMEFRAME_MAP

# ---------- Gemini Setup ----------
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")  # Add to .streamlit/secrets.toml
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# ---------- Page ----------
st.set_page_config(page_title="Stock Dashboard Pro", layout="wide")
st.markdown(
    """
    <style>
    .big-font {font-size: 42px !important; font-weight: bold; color: #00D4AA;}
    .kpi-card {background-color: #161B22; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.2);}
    .kpi-value {font-size: 28px; font-weight: 600; color: #00D4AA;}
    .kpi-label {font-size: 14px; color: #B0B8C4; margin-top: 5px;}
    .ai-card {background: linear-gradient(135deg, #161B22 0%, #1A1F2E 100%); padding: 20px; border-radius: 12px; border-left: 4px solid #00D4AA;}
    .ai-title {color: #00D4AA; font-weight: bold; margin-bottom: 10px;}
    .ai-response {color: #FAFAFA; line-height: 1.6; font-size: 16px;}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Title ----------
st.markdown('<h1 class="big-font">STOCK DASHBOARD PRO</h1>', unsafe_allow_html=True)

# ---------- Hard-coded Keys ----------
API_KEY    = "PKIB3ZFEANA46ZPRPIUZR5DOHN"
API_SECRET = "5vz3pZvr5anSeT3V7jQDyZVRgsnh7suhJtXDf27khFtG"

# ---------- Group by Sector ----------
SECTORS = {}
for sym, info in STOCK_DATA.items():
    SECTORS.setdefault(info["sector"], []).append(sym)

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Stock Selector")

    # Search
    search = st.text_input("Search company...", "")
    filtered = {
        sym: info for sym, info in STOCK_DATA.items()
        if search.lower() in info["name"].lower() or search.upper() == sym
    }

    # Sector Filter
    sector_filter = st.selectbox("Sector", options=["All"] + list(SECTORS.keys()))
    if sector_filter != "All":
        filtered = {sym: info for sym, info in filtered.items() if info["sector"] == sector_filter}

    # Symbol Select
    symbol = st.selectbox(
        "Select Stock",
        options=list(filtered.keys()),
        format_func=lambda x: f"{x} – {filtered[x]['name']}"
    )
    sector = filtered[symbol]["sector"]

    period = st.selectbox("Period", options=list(TIMEFRAME_MAP.keys()))
    chart_type = st.radio("Chart Type", ["Candlestick", "Line"])

    st.subheader("Indicators")
    sma = st.checkbox("SMA 20", True)
    ema = st.checkbox("EMA 20", True)
    bb  = st.checkbox("Bollinger Bands", True)

    st.info(f"**{symbol}** – {STOCK_DATA[symbol]['name']}\nSector: {sector}")

# ---------- Choose Feed ----------
cfg = TIMEFRAME_MAP[period]
feed = "sip" if cfg["days"] > 35 else "iex"
alpaca = AlpacaAPI(API_KEY, API_SECRET, feed=feed)

# ---------- Fetch ----------
start_iso, end_iso = alpaca.get_market_range(cfg["days"])

with st.spinner(f"Fetching {symbol} {period} ({feed.upper()})…"):
    df = alpaca.get_bars(symbol, cfg["alpaca"], start_iso, end_iso)

if df.empty:
    if feed == "iex":
        st.error(f"No data for **{symbol}** ({period}). Try 1d/1wk/1mo.")
    else:
        st.error(f"No data for **{symbol}** ({period}). Upgrade to SIP for full history.")
    st.stop()

# ---------- KPIs (Top Row) ----------
latest = df.iloc[-1]
prev   = df.iloc[-2] if len(df) > 1 else latest
delta  = latest["Close"] - prev["Close"]
delta_pct = (delta / prev["Close"]) * 100

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-value">${latest['Close']:.2f}</div>
            <div class="kpi-label">Last Close</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-value" style="color: {'#00ff85' if delta >= 0 else '#ff4d4d'}">
                {delta:+.2f}
            </div>
            <div class="kpi-label">Change ($)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-value" style="color: {'#00ff85' if delta_pct >= 0 else '#ff4d4d'}">
                {delta_pct:+.2f}%
            </div>
            <div class="kpi-label">Change (%)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-value">{latest['Volume']:,.0f}</div>
            <div class="kpi-label">Volume</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col5:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-value">${df['High'].max():.2f}</div>
            <div class="kpi-label">Period High</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------- Chart ----------
fig = go.Figure()
if chart_type == "Candlestick":
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name=symbol
    ))
else:
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close"))

# Indicators
if sma:
    df["SMA20"] = df["Close"].rolling(20).mean()
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], name="SMA 20", line=dict(dash="dash")))
if ema:
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], name="EMA 20", line=dict(dash="dot")))
if bb:
    df["BB_Mid"] = df["Close"].rolling(20).mean()
    df["BB_Std"] = df["Close"].rolling(20).std()
    df["BB_Upper"] = df["BB_Mid"] + 2 * df["BB_Std"]
    df["BB_Lower"] = df["BB_Mid"] - 2 * df["BB_Std"]
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Upper"], name="BB Upper", line=dict(width=1)))
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Lower"], name="BB Lower", line=dict(width=1)))

fig.update_layout(
    title=f"{symbol} – {period.upper()} ({feed.upper()})",
    xaxis_title="Date", yaxis_title="Price ($)",
    height=600, template="plotly_dark"
)
st.plotly_chart(fig, use_container_width=True)

# ---------- Gemini AI Recommendation ----------
# st.subheader("AI Stock Recommendation")
# if st.button("Generate Recommendation", type="primary"):
#     with st.spinner("Analyzing with Gemini AI..."):
#         # Prepare prompt with stock data summary
#         summary = f"""
#         Stock: {symbol} ({STOCK_DATA[symbol]['name']})
#         Period: {period}
#         Current Price: ${latest['Close']:.2f}
#         Change: {delta:+.2f} ({delta_pct:+.2f}%)
#         Volume: {latest['Volume']:,.0f}
#         High: ${df['High'].max():.2f} | Low: ${df['Low'].min():.2f}
#         SMA20: ${df['SMA20'].iloc[-1]:.2f if 'SMA20' in df else 'N/A'}
#         EMA20: ${df['EMA20'].iloc[-1]:.2f if 'EMA20' in df else 'N/A'}
#         Trend: {'Upward' if delta_pct > 0 else 'Downward'} over last {len(df)} days.
        
#         Recommend BUY, SELL, or HOLD. Give 1-2 sentence reason based on trends, volume, and indicators. Keep it concise and neutral (not financial advice).
#         """
        
#         response = model.generate_content(summary)
#         st.markdown(
#             f"""
#             <div class="ai-card">
#                 <div class="ai-title">Gemini AI Recommendation</div>
#                 <div class="ai-response">{response.text}</div>
#             </div>
#             """,
#             unsafe_allow_html=True
#         )
# ---------- Gemini AI Recommendation ----------
st.subheader("Gemini AI Stock Recommendation")

if st.button("Generate AI Recommendation", type="primary", use_container_width=True):
    with st.spinner("Gemini is analyzing the market..."):
        # Safely get indicator values (avoid format error)
        sma20_val = df['SMA20'].iloc[-1] if 'SMA20' in df.columns and not df['SMA20'].isna().all() else None
        ema20_val = df['EMA20'].iloc[-1] if 'EMA20' in df.columns and not df['EMA20'].isna().all() else None

        sma_text = f"${sma20_val:.2f}" if sma20_val is not None else "Not available"
        ema_text = f"${ema20_val:.2f}" if ema20_val is not None else "Not available"

        # Build clean summary
        summary = f"""
        Analyze {symbol} ({STOCK_DATA[symbol]['name']}) over the last {period} period:
        - Current price: ${latest['Close']:.2f}
        - Daily change: {delta:+.2f} ({delta_pct:+.2f}%)
        - Volume: {latest['Volume']:,.0f}
        - Period high: ${df['High'].max():.2f}
        - Period low: ${df['Low'].min():.2f}
        - SMA20: {sma_text}
        - EMA20: {ema_text}
        - Price vs SMA20: {'Above' if latest['Close'] > sma20_val else 'Below' if sma20_val else 'N/A'}
        
        Give a short, clear recommendation: BUY, SELL or HOLD.
        One sentence reason. Keep it neutral and technical (not financial advice).
        """

        try:
            response = model.generate_content(summary)
            st.success("Gemini AI Analysis Complete")
            st.markdown(
                f"""
                <div class="ai-card">
                    <div class="ai-title">Gemini AI Recommendation</div>
                    <div class="ai-response"><strong>{response.text}</strong></div>
                    <small>Powered by Google Gemini • Not financial advice</small>
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Gemini API error: {str(e)}")
            st.info("Check your API key in `.streamlit/secrets.toml` or rate limits.")
# ---------- Table ----------
st.subheader("Historical Data")
disp = df.copy()
disp.index = disp.index.strftime("%Y-%m-%d")

disp = disp.round(2)
st.dataframe(disp, use_container_width=True)

# ---------- CSV ----------
csv = df.to_csv().encode()
st.download_button("Download CSV", csv, f"{symbol}_{period}.csv", "text/csv")