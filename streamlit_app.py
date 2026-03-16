import streamlit as st
import pandas as pd
import random
import math

st.set_page_config(page_title="📈 Stock Market Simulator", page_icon="📈", layout="wide")

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
body, .main { background-color: #0e1117; color: white; }

.card {
    background: #1e2130;
    border-radius: 12px;
    padding: 16px 20px;
    border: 1px solid #2e3450;
    margin-bottom: 10px;
}

.label {
    color: #8b95b5;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 1px;
}

.val {
    color: #ffffff;
    font-size: 28px;
    font-weight: 800;
}

.green { color: #00d4aa !important; }
.red { color: #ff4d6d !important; }

.stButton > button {
    background: linear-gradient(135deg,#00d4aa,#0088cc);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
STARTING_CASH = 10_000.0

STOCK_INFO = {
    "AAPL":  {"name": "Apple",              "base": 213.0,  "vol": 0.012, "trend": 0.0003},
    "TSLA":  {"name": "Tesla",              "base": 175.0,  "vol": 0.055, "trend": 0.0002},
    "GOOGL": {"name": "Google",             "base": 178.0,  "vol": 0.014, "trend": 0.0004},
    "MSFT":  {"name": "Microsoft",          "base": 415.0,  "vol": 0.010, "trend": 0.0005},
    "AMZN":  {"name": "Amazon",             "base": 195.0,  "vol": 0.016, "trend": 0.0003},
    "META":  {"name": "Meta",               "base": 580.0,  "vol": 0.050, "trend": 0.0007},
    "NVDA":  {"name": "NVIDIA",             "base": 875.0,  "vol": 0.060, "trend": 0.0010},
    "NFLX":  {"name": "Netflix",            "base": 980.0,  "vol": 0.022, "trend": 0.0002},
    "JPM":   {"name": "JPMorgan",           "base": 230.0,  "vol": 0.009, "trend": 0.0002},
    "BRK-B": {"name": "Berkshire Hathaway", "base": 455.0,  "vol": 0.007, "trend": 0.0001},
}

TICKERS = list(STOCK_INFO.keys())

# ── Generate price paths ──────────────────────────────────────────────────────
def _gen_paths(n):
    paths = {}

    for t, info in STOCK_INFO.items():
        prices = [info["base"]]

        for _ in range(n - 1):
            shock = random.gauss(info["trend"], info["vol"])
            prices.append(round(prices[-1] * math.exp(shock), 2))

        paths[t] = prices

    return paths

# ── Session State Initialization ──────────────────────────────────────────────
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.player = ""
    st.session_state.cash = STARTING_CASH
    st.session_state.portfolio = {}
    st.session_state.trades = []
    st.session_state.pv_history = []
    st.session_state.tick = 100
    st.session_state.price_paths = _gen_paths(1000)
    st.session_state.last_msg = None

# ── Clean portfolio (removes invalid tickers like BTC) ────────────────────────
clean_portfolio = {}
for t, s in st.session_state.portfolio.items():
    if t in STOCK_INFO:
        clean_portfolio[t] = s

st.session_state.portfolio = clean_portfolio


# ── Helper Functions ──────────────────────────────────────────────────────────
def current_price(ticker):

    if ticker not in st.session_state.price_paths:
        return 0

    tick = min(
        st.session_state.tick,
        len(st.session_state.price_paths[ticker]) - 1
    )

    return st.session_state.price_paths[ticker][tick]


def portfolio_value():

    val = st.session_state.cash

    for t, s in st.session_state.portfolio.items():

        if t not in STOCK_INFO:
            continue

        val += current_price(t) * s

    return val


def snap():

    st.session_state.pv_history.append({
        "Trade #": len(st.session_state.pv_history) + 1,
        "Portfolio Value ($)": round(portfolio_value(), 2),
    })


# ── Landing Page ──────────────────────────────────────────────────────────────
if not st.session_state.started:

    st.markdown("<h1 style='text-align:center;font-size:3rem'>📈 Stock Market Simulator</h1>", unsafe_allow_html=True)

    st.markdown(
        "<p style='text-align:center;color:#8b95b5;font-size:1.1rem'>Start with $10,000 virtual money · Trade stocks · Master the market!</p>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    c1, c2, c3 = st.columns([1,2,1])

    with c2:

        name = st.text_input("👤 Enter your name")

        if st.button("🚀 Start Trading!", use_container_width=True):

            if name.strip():

                st.session_state.player = name.strip()
                st.session_state.started = True
                snap()
                st.rerun()

            else:
                st.warning("Please enter your name")

    st.stop()


# ── Main App ─────────────────────────────────────────────────────────────────
st.markdown(
    f"<h1>📈 Stock Market Simulator <span style='font-size:1rem;color:#8b95b5'>| {st.session_state.player}</span></h1>",
    unsafe_allow_html=True
)

tabs = st.tabs(["💹 Trade", "📊 My Portfolio", "📈 Price Charts"])


# ══════════════════════════════════════════════
# TAB 1 — TRADE
# ══════════════════════════════════════════════
with tabs[0]:

    pv = portfolio_value()
    gain = pv - STARTING_CASH
    gp = gain / STARTING_CASH * 100
    gc = "green" if gain >= 0 else "red"

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"<div class='card'><div class='label'>CASH</div><div class='val green'>${st.session_state.cash:,.2f}</div></div>", unsafe_allow_html=True)

    with c2:
        st.markdown(f"<div class='card'><div class='label'>TOTAL VALUE</div><div class='val'>${pv:,.2f}</div></div>", unsafe_allow_html=True)

    with c3:
        st.markdown(f"<div class='card'><div class='label'>GAIN / LOSS</div><div class='val {gc}'>${gain:,.2f} ({gp:+.1f}%)</div></div>", unsafe_allow_html=True)

    st.markdown("### 📋 Live Market Prices")

    rows = []

    for t in TICKERS:

        p = current_price(t)
        prev = st.session_state.price_paths[t][max(st.session_state.tick-1,0)]
        chg = (p-prev)/prev*100
        owned = st.session_state.portfolio.get(t,0)

        rows.append({
            "Ticker": t,
            "Company": STOCK_INFO[t]["name"],
            "Price ($)": p,
            "Change": f"{'▲' if chg>=0 else '▼'} {abs(chg):.2f}%",
            "Owned": owned,
            "Value ($)": round(p*owned,2)
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 🛒 Place a Trade")

    col1,col2,col3 = st.columns(3)

    with col1:
        sel = st.selectbox("Stock", TICKERS, format_func=lambda x:f"{x} — {STOCK_INFO[x]['name']}")

    with col2:
        action = st.selectbox("Action",["Buy","Sell"])

    with col3:
        cp = current_price(sel)
        max_q = int(st.session_state.cash // cp) if action=="Buy" else st.session_state.portfolio.get(sel,0)
        qty = st.number_input("Shares",1,max(max_q,1),1)

    cost = round(cp*qty,2)

    if st.button("Execute Trade",use_container_width=True):

        if action=="Buy" and cost<=st.session_state.cash:

            st.session_state.cash-=cost
            st.session_state.portfolio[sel]=st.session_state.portfolio.get(sel,0)+qty

        elif action=="Sell" and qty<=st.session_state.portfolio.get(sel,0):

            st.session_state.cash+=cost
            st.session_state.portfolio[sel]-=qty

            if st.session_state.portfolio[sel]==0:
                del st.session_state.portfolio[sel]

        else:
            st.error("Insufficient funds or shares")
            st.stop()

        st.session_state.tick+=1
        snap()
        st.rerun()


# ══════════════════════════════════════════════
# TAB 2 — PORTFOLIO
# ══════════════════════════════════════════════
with tabs[1]:

    if not st.session_state.portfolio:
        st.info("No stocks owned yet")

    else:

        rows=[]

        for t,s in st.session_state.portfolio.items():

            p=current_price(t)
            v=p*s

            rows.append({
                "Ticker":t,
                "Shares":s,
                "Price":p,
                "Value":v
            })

        st.dataframe(pd.DataFrame(rows),use_container_width=True)

    if len(st.session_state.pv_history)>1:
        st.line_chart(pd.DataFrame(st.session_state.pv_history).set_index("Trade #"))


# ══════════════════════════════════════════════
# TAB 3 — CHARTS
# ══════════════════════════════════════════════
with tabs[2]:

    current_tick = st.session_state.tick

    st.markdown("### Individual Stock History")

    chart_t = st.selectbox(
        "Select Stock",
        TICKERS,
        format_func=lambda x:f"{x} — {STOCK_INFO[x]['name']}"
    )

    window = st.slider("Historical Window",10,200,50)

    start = max(0,current_tick-window)
    end = current_tick+1

    data = st.session_state.price_paths[chart_t][start:end]

    st.line_chart(pd.DataFrame({"Price":data}))

    st.markdown("---")
    st.markdown("### Relative Performance Comparison")

    # Initialize state
    if "selected_stocks" not in st.session_state:
        st.session_state.selected_stocks = TICKERS[:5]
    
    # Buttons FIRST
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("Select All"):
            st.session_state.selected_stocks = TICKERS.copy()
    
    with col_btn2:
        if st.button("Clear"):
            st.session_state.selected_stocks = []
    
    # Multiselect
    selected_stocks = st.multiselect(
        "Select stocks to compare",
        TICKERS,
        default=st.session_state.selected_stocks,
        format_func=lambda x: f"{x} — {STOCK_INFO[x]['name']}"
    )
    
    # Save selection
    st.session_state.selected_stocks = selected_stocks
    
    # Build plot
    plot = {}
    
    for t in selected_stocks:
    
        prices = st.session_state.price_paths[t][start:end]
    
        if len(prices) > 0:
            base = prices[0]
            plot[t] = [(p/base - 1) * 100 for p in prices]
    
    if plot:
        df = pd.DataFrame(plot)
        st.line_chart(df)
    
    st.caption("Relative % change from start of window")
