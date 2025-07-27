import streamlit as st
import ccxt
import pandas as pd
from ta.trend import EMAIndicator, MACD, ADXIndicator
from datetime import datetime
from zoneinfo import ZoneInfo

# ================================
# App Title
# ================================
st.title("📈 Crypto Technical Analysis App")

# ================================
# User Input
# ================================
base_symbol = st.text_input("Enter the symbol (e.g., BTC, DOGE, SHIB):", "BTC").upper()
timeframe = '4h'
limit = 200
symbol = f"{base_symbol}/USDT"

# ================================
# Fetch & Process Data
# ================================
@st.cache_data(show_spinner=False)
def fetch_data(symbol, timeframe, limit):
    exchange = ccxt.kucoin()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# Only proceed if input is valid
try:
    df = fetch_data(symbol, timeframe, limit)

    # Indicators
    df['ema50'] = EMAIndicator(df['close'], window=50).ema_indicator()
    df['ema200'] = EMAIndicator(df['close'], window=200).ema_indicator()
    macd = MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    adx = ADXIndicator(df['high'], df['low'], df['close'], window=14)
    df['adx'] = adx.adx()

    # Latest row
    latest = df.iloc[-1]
    current_price = latest['close']
    bullish_trend = latest['ema50'] > latest['ema200']
    macd_bullish = latest['macd'] > latest['macd_signal']
    strong_trend = latest['adx'] > 25

    # Fib Targets
    swing_low = df['low'].min()
    swing_high = df['high'].max()
    fib_target_1 = swing_high + (swing_high - swing_low) * 0.618
    fib_target_2 = swing_high + (swing_high - swing_low) * 1.000

    # Format prices
    def format_price(value):
        if value >= 1:
            return f"{value:.4f}"
        elif value >= 0.01:
            return f"{value:.6f}"
        else:
            return f"{value:.8f}"

    # Display results
    ts = datetime.now(ZoneInfo("Asia/Phnom_Penh")).strftime("%Y-%m-%d %I:%M %p ICT")
    st.subheader(f"📊 Analysis for {symbol} ({timeframe})")
    st.write(f"🕒 {ts} (Phnom Penh)")
    st.write(f"**Current Price:** `{format_price(current_price)}`")
    st.write(f"EMA50: `{format_price(latest['ema50'])}` | EMA200: `{format_price(latest['ema200'])}`")
    st.write(f"MACD: `{format_price(latest['macd'])}` | Signal: `{format_price(latest['macd_signal'])}`")
    st.write(f"ADX: `{format_price(latest['adx'])}`")

    if bullish_trend and macd_bullish and strong_trend:
        st.success("✅ **STRONG BUY SIGNAL** based on EMA, MACD, and ADX confirmation.")
        st.write(f"🎯 **Target 1 (0.618):** `{format_price(fib_target_1)}`")
        st.write(f"🎯 **Target 2 (1.000):** `{format_price(fib_target_2)}`")
    else:
        st.warning("🚫 No strong buy signal. **Wait for clearer confirmation.**")

    # Show recent price chart
    st.line_chart(df.set_index('timestamp')[['close', 'ema50', 'ema200']])

except Exception as e:
    st.error(f"Error fetching data or computing indicators: {e}")

# --- Donation Section ---
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
    st.warning("⚠️ eth_qr.png not found. Add it to your project folder to display donation QR.")
