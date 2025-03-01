import streamlit as st

st.set_page_config(
    page_title="Financial Education Hub",
    page_icon="📚",
    layout="wide"
)

# Title and introduction
st.title("📚 Financial Education Hub")
st.markdown("""
Welcome to your comprehensive guide to understanding stock market analysis and investment concepts.
Use this resource to learn about various terms, metrics, and strategies used throughout the application.
""")

# Financial Terms Section
st.header("📊 Financial Terms and Metrics")

with st.expander("Market Capitalization"):
    st.markdown("""
    ### Market Capitalization (Market Cap)
    
    **Definition**: The total value of a company's outstanding shares in the market.
    
    **Calculation**: Share Price × Number of Outstanding Shares
    
    **Categories**:
    - Large Cap: Over R100 billion
    - Mid Cap: R10 billion - R100 billion
    - Small Cap: Under R10 billion
    
    **Why It Matters**: Market cap helps you understand:
    - Company size and market position
    - Investment risk level
    - Stock liquidity
    """)

with st.expander("Price-to-Earnings (P/E) Ratio"):
    st.markdown("""
    ### Price-to-Earnings (P/E) Ratio
    
    **Definition**: A valuation metric comparing a company's stock price to its earnings per share.
    
    **Calculation**: Share Price ÷ Earnings Per Share
    
    **Interpretation**:
    - High P/E: Market expects high growth
    - Low P/E: Potentially undervalued
    - Negative P/E: Company is losing money
    
    **Industry Context**: Different sectors have different typical P/E ranges
    """)

# Technical Analysis Section
st.header("📈 Technical Analysis")

with st.expander("Moving Averages"):
    st.markdown("""
    ### Moving Averages
    
    **Types**:
    1. Simple Moving Average (SMA)
    2. Exponential Moving Average (EMA)
    
    **Common Periods**:
    - 50-day: Short-term trend
    - 200-day: Long-term trend
    
    **Trading Signals**:
    - Golden Cross: Short-term MA crosses above long-term MA (bullish)
    - Death Cross: Short-term MA crosses below long-term MA (bearish)
    """)

# Portfolio Management
st.header("💼 Portfolio Management")

with st.expander("Diversification"):
    st.markdown("""
    ### Diversification
    
    **Definition**: Spreading investments across different assets to reduce risk.
    
    **Benefits**:
    - Reduces company-specific risk
    - Smooths overall returns
    - Provides better risk-adjusted performance
    
    **Methods**:
    1. Sector Diversification
    2. Market Cap Diversification
    3. Geographic Diversification
    """)

# Risk Assessment
st.header("⚠️ Risk Assessment")

with st.expander("Risk Metrics"):
    st.markdown("""
    ### Common Risk Metrics
    
    **1. Volatility (Standard Deviation)**
    - Measures price variation
    - Higher values indicate more risk
    
    **2. Beta**
    - Measures stock's movement relative to market
    - Beta > 1: More volatile than market
    - Beta < 1: Less volatile than market
    
    **3. Maximum Drawdown**
    - Largest peak-to-trough decline
    - Indicates worst-case historical loss
    """)

# Important Disclaimers
st.warning("""
⚠️ **Educational Purpose Only**

This information is provided for educational purposes only:
- Not financial advice
- Past performance doesn't guarantee future results
- Always conduct your own research
- Consider consulting a financial advisor
""")

# Quick Navigation
st.sidebar.header("Quick Links")
st.sidebar.markdown("""
- [Market Capitalization](#market-capitalization)
- [P/E Ratio](#price-to-earnings-p-e-ratio)
- [Moving Averages](#moving-averages)
- [Diversification](#diversification)
- [Risk Metrics](#risk-metrics)
""")
