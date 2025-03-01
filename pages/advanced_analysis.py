import streamlit as st
import pandas as pd
import numpy as np
from utils.stock_data import (
    JSE_TOP_50, get_stock_data, get_financial_metrics,
    calculate_sector_metrics, calculate_portfolio_metrics
)
from utils.forecasting import create_forecast, calculate_forecast_returns
from utils.analysis import calculate_portfolio_value, get_summary_statistics

st.set_page_config(
    page_title="Advanced Stock Analysis",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 Advanced Stock Analysis")

# Educational section
with st.expander("🎓 Understanding Advanced Metrics"):
    st.markdown("""
    ### Technical Analysis Indicators
    
    1. **Moving Averages** 📈
       - 50-day MA: Short-term trend indicator
       - 200-day MA: Long-term trend indicator
       - Golden Cross: When 50-day crosses above 200-day (bullish)
       - Death Cross: When 50-day crosses below 200-day (bearish)
    
    2. **Volatility Measures** 📊
       - Standard Deviation: Measures price spread
       - Beta: Stock's volatility compared to market
    
    3. **Portfolio Metrics** 💼
       - Diversification Score: Spread across sectors
       - Risk-Adjusted Returns: Returns considering risk
       - Sharpe Ratio: Return per unit of risk
    
    ### Using This Page
    
    1. Select stocks for comparison
    2. Choose investment amount
    3. View projected returns
    4. Analyze risk metrics
    """)

# Sector Analysis
st.header("Sector Performance")
selected_sector = st.selectbox(
    "Choose Sector for Analysis",
    options=["All Sectors"] + list(set(data['sector'] for data in JSE_TOP_50.values())),
    help="Compare performance metrics across different sectors"
)

if selected_sector != "All Sectors":
    with st.spinner("Calculating sector metrics..."):
        sector_metrics = calculate_sector_metrics(selected_sector)
        
        # Display sector metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Market Cap",
                f"R{sector_metrics['Total Market Cap']/1e9:.2f}B",
                help="Combined market value of all companies in the sector"
            )
        
        with col2:
            st.metric(
                "Average P/E",
                f"{sector_metrics['Weighted P/E']:.2f}",
                help="Market cap weighted average P/E ratio"
            )
        
        with col3:
            st.metric(
                "Dividend Yield",
                f"{sector_metrics['Weighted Dividend Yield']*100:.2f}%",
                help="Market cap weighted average dividend yield"
            )
        
        with col4:
            st.metric(
                "Companies",
                sector_metrics['Number of Companies'],
                help="Number of companies in this sector"
            )

# Portfolio Simulation
st.header("Portfolio Simulation")
st.info("""
🔍 **How to Use Portfolio Simulation**
- Select up to 3 stocks for your portfolio
- Enter your monthly investment amount
- View projected returns and risk metrics
- Analyze historical performance
""")

selected_stocks = st.multiselect(
    "Select Stocks for Portfolio (max 3)",
    options=list(JSE_TOP_50.keys()),
    max_selections=3,
    format_func=lambda x: f"{x} - {JSE_TOP_50[x]['name']}",
    help="Choose up to 3 stocks to simulate a portfolio"
)

if selected_stocks:
    monthly_investment = st.number_input(
        "Monthly Investment Amount (Rands)",
        min_value=100,
        value=1000,
        step=100,
        help="Amount to invest monthly in your selected portfolio"
    )
    
    st.subheader("Portfolio Analysis")
    
    # Calculate portfolio metrics
    portfolio_metrics = calculate_portfolio_metrics(selected_stocks, monthly_investment)
    
    # Display metrics in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Portfolio Value",
            f"R{portfolio_metrics['Total Market Cap']/1e6:.2f}M",
            help="Combined value of selected stocks"
        )
    
    with col2:
        st.metric(
            "Average P/E",
            f"{portfolio_metrics['Weighted P/E']:.2f}",
            help="Portfolio weighted P/E ratio"
        )
    
    with col3:
        st.metric(
            "Dividend Yield",
            f"{portfolio_metrics['Weighted Dividend Yield']*100:.2f}%",
            help="Portfolio weighted dividend yield"
        )
    
    # Risk Analysis
    st.subheader("Risk Analysis")
    st.caption("""
    Understanding your portfolio's risk profile helps make informed investment decisions.
    Consider these metrics when evaluating your investment strategy.
    """)
    
    # Calculate and display risk metrics for each stock
    for stock in selected_stocks:
        hist, _ = get_stock_data(stock)
        if hist is not None and not hist.empty:
            stats = get_summary_statistics(hist)
            
            st.write(f"**{JSE_TOP_50[stock]['name']} ({stock})**")
            risk_col1, risk_col2, risk_col3, risk_col4 = st.columns(4)
            
            with risk_col1:
                st.metric(
                    "Average Price",
                    f"R{stats['Mean']:.2f}",
                    help="Mean price over the period"
                )
            
            with risk_col2:
                st.metric(
                    "Volatility",
                    f"R{stats['Std Dev']:.2f}",
                    help="Standard deviation of price"
                )
            
            with risk_col3:
                st.metric(
                    "Lowest Price",
                    f"R{stats['Min']:.2f}",
                    help="Minimum price in period"
                )
            
            with risk_col4:
                st.metric(
                    "Highest Price",
                    f"R{stats['Max']:.2f}",
                    help="Maximum price in period"
                )

# Disclaimer
st.warning("""
⚠️ **Important Disclaimer**

This tool provides historical analysis and simulated projections for educational purposes only:
- Past performance does not guarantee future results
- All projections are based on historical data and assumptions
- Market conditions can change rapidly
- Consider consulting a financial advisor for personalized advice
""")
