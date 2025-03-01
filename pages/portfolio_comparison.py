import streamlit as st
import pandas as pd
import numpy as np
from utils.stock_data import JSE_TOP_50, get_stock_data
from utils.analysis import calculate_portfolio_value, get_summary_statistics

st.set_page_config(
    page_title="Portfolio Comparison",
    page_icon="💼",
    layout="wide"
)

# Title and description
st.title("💼 Portfolio Comparison")

# Educational section
with st.expander("📚 Understanding Portfolio Analysis"):
    st.markdown("""
    ### Portfolio Theory Basics
    
    1. **Diversification** 🎯
       - Spreading investments across different stocks
       - Reducing company-specific risk
       - Not putting all eggs in one basket
    
    2. **Correlation** 🔄
       - How stocks move in relation to each other
       - Positive correlation: stocks move together
       - Negative correlation: stocks move opposite
    
    3. **Risk vs Return** ⚖️
       - Higher potential returns often come with higher risk
       - Diversification can help optimize this trade-off
       - Consider your risk tolerance when investing
    
    ### Using This Page
    
    1. Select stocks to compare
    2. View correlation analysis
    3. Compare historical performance
    4. Understand risk metrics
    """)

# Stock Selection
st.header("Stock Comparison")
st.info("""
🔍 **How to Use Comparison Tools**
- Select up to 5 stocks to compare
- View correlation between selected stocks
- Analyze historical performance patterns
- Understand risk-return relationships
""")

# Multi-stock selector with sector grouping
sectors = list(set(data['sector'] for data in JSE_TOP_50.values()))
selected_stocks = []

for sector in sectors:
    sector_stocks = {symbol: data for symbol, data in JSE_TOP_50.items() 
                    if data['sector'] == sector}
    
    st.subheader(f"{sector} Sector")
    sector_selections = st.multiselect(
        f"Select {sector} stocks",
        options=list(sector_stocks.keys()),
        format_func=lambda x: f"{x} - {JSE_TOP_50[x]['name']}",
        key=f"select_{sector}",
        max_selections=2,
        help=f"Choose up to 2 stocks from the {sector} sector"
    )
    selected_stocks.extend(sector_selections)

if len(selected_stocks) > 1:
    # Fetch historical data for selected stocks
    stock_data = {}
    for symbol in selected_stocks:
        hist, _ = get_stock_data(symbol)
        if hist is not None and not hist.empty:
            stock_data[symbol] = hist['Close']
    
    if stock_data:
        # Create DataFrame with all stock prices
        df = pd.DataFrame(stock_data)
        
        # Calculate correlation matrix
        st.subheader("Stock Price Correlation")
        st.caption("""
        This heatmap shows how closely the selected stocks' prices move together.
        - 1.0 = Perfect positive correlation (move exactly together)
        - 0.0 = No correlation (move independently)
        - -1.0 = Perfect negative correlation (move opposite)
        """)
        
        corr_matrix = df.corr()
        st.dataframe(
            corr_matrix.style.background_gradient(cmap='RdYlGn')
                           .format("{:.2f}")
        )
        
        # Performance Comparison
        st.subheader("Performance Comparison")
        st.caption("""
        Compare how R100 invested in each stock would have grown over time.
        This helps visualize relative performance between stocks.
        """)
        
        # Normalize prices to start at 100
        normalized_df = df * 100 / df.iloc[0]
        st.line_chart(normalized_df)
        
        # Risk-Return Analysis
        st.subheader("Risk-Return Analysis")
        
        # Calculate metrics for each stock
        metrics_data = []
        for symbol in selected_stocks:
            returns = df[symbol].pct_change().dropna()
            metrics_data.append({
                'Stock': f"{symbol} ({JSE_TOP_50[symbol]['name']})",
                'Avg Return (%)': returns.mean() * 100,
                'Risk (Std Dev)': returns.std() * 100,
                'Max Drawdown (%)': ((df[symbol].cummax() - df[symbol]) / df[symbol].cummax()).max() * 100
            })
        
        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(
            metrics_df.style.format({
                'Avg Return (%)': '{:.2f}%',
                'Risk (Std Dev)': '{:.2f}%',
                'Max Drawdown (%)': '{:.2f}%'
            })
        )
        
        # Educational interpretation
        st.info("""
        📊 **Understanding the Metrics**
        
        1. **Average Return**: The mean daily return, annualized
        2. **Risk (Standard Deviation)**: Measure of price volatility
        3. **Maximum Drawdown**: Largest peak-to-trough decline
        
        Higher returns often come with higher risk. Consider these 
        metrics alongside your investment goals and risk tolerance.
        """)

# Disclaimer
st.warning("""
⚠️ **Important Disclaimer**

This tool provides historical analysis and comparisons for educational purposes only:
- Past performance does not predict future results
- Consider consulting a financial advisor
- Research thoroughly before investing
- Diversification does not guarantee profits
""")
