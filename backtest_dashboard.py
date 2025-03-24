# -*- coding: utf-8 -*-
"""backtest_dashboard.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1jZksgNdy8LN6vFwdd0Gi1V4ys7JNujHF
"""

# backtesting_dashboard.py
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(layout="wide", page_title="Backtest Dashboard")

st.title("📈 Moving Average Crossover Strategy")
st.markdown("Visualize and evaluate a simple backtesting strategy using short and long-term moving averages.")

# Layout
col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    ticker = st.text_input("Enter Ticker", value="AAPL")
with col2:
    short_window = st.slider("Short MA Window", 5, 50, 20)
with col3:
    long_window = st.slider("Long MA Window", 20, 200, 50)

col4, col5 = st.columns([1, 1])
with col4:
    start = st.date_input("Start Date", pd.to_datetime("2020-01-01"))
with col5:
    end = st.date_input("End Date", pd.to_datetime("2024-01-01"))

# Load data
df = yf.download(ticker, start=start, end=end)
df["ShortMA"] = df["Close"].rolling(short_window).mean()
df["LongMA"] = df["Close"].rolling(long_window).mean()
df["Signal"] = 0
df["Signal"][short_window:] = (df["ShortMA"][short_window:] > df["LongMA"][short_window:]).astype(int)
df["Position"] = df["Signal"].diff()
df["Return"] = df["Close"].pct_change()
df["Strategy"] = df["Signal"].shift(1) * df["Return"]
df.dropna(subset=["Strategy"], inplace=True)
df["Equity"] = (1 + df["Strategy"]).cumprod()


# Charts
st.subheader("📊 Price Chart with Signals")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Price", line=dict(color='gray')))
fig.add_trace(go.Scatter(x=df.index, y=df["ShortMA"], name=f"{short_window}-day MA", line=dict(color='blue')))
fig.add_trace(go.Scatter(x=df.index, y=df["LongMA"], name=f"{long_window}-day MA", line=dict(color='orange')))
fig.add_trace(go.Scatter(
    x=df[df["Position"] == 1].index,
    y=df["Close"][df["Position"] == 1],
    mode="markers", name="Buy Signal",
    marker=dict(symbol="triangle-up", size=10, color="green")))
fig.add_trace(go.Scatter(
    x=df[df["Position"] == -1].index,
    y=df["Close"][df["Position"] == -1],
    mode="markers", name="Sell Signal",
    marker=dict(symbol="triangle-down", size=10, color="red")))
fig.update_layout(height=500, margin=dict(t=10, b=10))
st.plotly_chart(fig, use_container_width=True)

# Equity Curve
st.subheader("📈 Strategy Equity Curve")
fig_eq = go.Figure()
fig_eq.add_trace(go.Scatter(x=df.index, y=df["Equity"], name="Equity Curve", line=dict(color='purple')))
fig_eq.update_layout(height=400, margin=dict(t=10, b=10))
st.plotly_chart(fig_eq, use_container_width=True)

# Metrics
st.subheader("📌 Strategy Performance Metrics")
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("Total Return", f"{(df['Equity'].iloc[-1] - 1) * 100:.2f}%")
with col_b:
    st.metric("Number of Trades", int(df["Position"].abs().sum() / 2))
with col_c:
    st.metric("Holding Period Return", f"{df['Strategy'].mean() * 100:.4f}% per day")
