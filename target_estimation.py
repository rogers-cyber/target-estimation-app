import streamlit as st
import ccxt
import pandas as pd
from ta.trend import EMAIndicator, MACD, ADXIndicator
from datetime import datetime
from zoneinfo import ZoneInfo
import plotly.graph_objects as go

# ================================
# Streamlit Setup
# ================================
st.set_page_config(page_title="Crypto TA Dashboard", layout="wide")
st.title("📈 Crypto Technical Analysis Dashboard")

# ================================
# JavaScript Auto-Refresh (60 sec)
# ================================
refresh_interval_sec = 60
st.markdown(f"""
    <script>
        setTimeout(function() {{
            window.location.reload();
        }}, {refresh_interval_sec * 1000});
    </script>
""", unsafe_allow_html=True)

# ================================
# Manual Refresh Button
# ================================
if st.button("🔄 Manual Refresh"):
    st.experimental_rerun()

# ================================
# Input Controls
# ================================
col1, col2 = st.columns(2)
with col1:
    base_symbol = st.text_input("Enter symbol (e.g., BTC, DOGE, SHIB):", "BTC").upper()
with col2:
    timeframe = st.selectbox("Select timeframe:", ["1m", "5m", "15m", "1h", "4h", "1d"], index=4)

symbol = f"{base_symbol}/USDT"
limit = 200

# ================================
# Fetch OHLCV Data
# ================================
@st.cache_data(show_spinner=False)
def fetch_ohlcv_data(symbol, timeframe, limit):
    exchange = ccxt.kucoin()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# ================================
# Format Price
# ================================
def format_price(value):
    if value >= 1:
        return f"{value:.4f}"
    elif value >= 0.01:
        return f"{value:.6f}"
    else:
        return f"{value:.8f}"

# ================================
# Plot Candlestick Chart
# ================================
def plot_price_chart(df, symbol):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Price',
        increasing_line_color='green',
        decreasing_line_color='red',
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['ema50'],
        line=dict(color='blue', width=1.5),
        name='EMA 50'))

    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['ema200'],
        line=dict(color='orange', width=1.5),
        name='EMA 200'))

    fig.update_layout(
        title=f'{symbol} Price Chart ({timeframe})',
        xaxis_title='Time',
        yaxis_title='Price (USDT)',
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        height=600,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    return fig

# ================================
# Technical Analysis Logic
# ================================
try:
    exchange = ccxt.kucoin()
    df = fetch_ohlcv_data(symbol, timeframe, limit)
    ticker = exchange.fetch_ticker(symbol)
    current_price = ticker['last']
    last_candle_time = df['timestamp'].iloc[-1]

    # Indicators
    df['ema50'] = EMAIndicator(df['close'], window=50).ema_indicator()
    df['ema200'] = EMAIndicator(df['close'], window=200).ema_indicator()
    macd = MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    adx = ADXIndicator(df['high'], df['low'], df['close'], window=14)
    df['adx'] = adx.adx()
    latest = df.iloc[-1]

    bullish_trend = latest['ema50'] > latest['ema200']
    macd_bullish = latest['macd'] > latest['macd_signal']
    strong_trend = latest['adx'] > 25

    # Fibonacci Targets
    swing_low = df['low'].min()
    swing_high = df['high'].max()
    fib_target_1 = swing_high + (swing_high - swing_low) * 0.618
    fib_target_2 = swing_high + (swing_high - swing_low) * 1.0

    # Display Info
    time_now = datetime.now(ZoneInfo("Asia/Phnom_Penh")).strftime("%Y-%m-%d %I:%M %p ICT")
    st.subheader(f"📊 Analysis for {symbol}")
    st.write(f"🕒 *Now:* `{time_now}`")
    st.write(f"🕯️ *Last candle:* `{last_candle_time}`")

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Price", format_price(current_price))
    col2.metric("EMA50", format_price(latest['ema50']))
    col3.metric("EMA200", format_price(latest['ema200']))

    st.write(f"**MACD:** `{format_price(latest['macd'])}` | **Signal:** `{format_price(latest['macd_signal'])}`")
    st.write(f"**ADX:** `{format_price(latest['adx'])}`")

    if bullish_trend and macd_bullish and strong_trend:
        st.success("✅ **STRONG BUY SIGNAL** based on EMA, MACD, and ADX confirmation.")
        st.write(f"🎯 **Target 1 (0.618 Fib):** `{format_price(fib_target_1)}`")
        st.write(f"🎯 **Target 2 (1.000 Fib):** `{format_price(fib_target_2)}`")
    else:
        st.warning("🚫 No strong buy signal yet. Wait for further confirmation.")

    st.plotly_chart(plot_price_chart(df, symbol), use_container_width=True)

except Exception as e:
    st.error(f"❌ Error fetching data or indicators: {e}")

# ================================
# Donation Section
# ================================
st.markdown("---")
st.markdown("## 💖 Crypto Donations Welcome")
st.markdown("""
If this app helped you, consider donating:

- **BTC:** `bc1qlaact2ldakvwqa7l9xd3lhp4ggrvezs0npklte`  
- **TRX / USDT (TRC20):** `TBMrjoyxAuKTxBxPtaWB6uc9U5PX4JMfFu`

You can also scan the QR code below 👇
""")
try:
    st.image("eth_qr.png", width=180, caption="ETH / USDT QR")
except:
    st.warning("⚠️ QR image not found. Add `eth_qr.png` to your folder.")
