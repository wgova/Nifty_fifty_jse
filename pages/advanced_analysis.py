import streamlit as st
import pandas as pd
import numpy as np
import logging
from utils.stock_data import (
    JSE_TOP_50, get_stock_data, get_financial_metrics,
    calculate_sector_metrics, calculate_portfolio_metrics
)
from utils.forecasting import create_forecast, calculate_forecast_returns
from utils.analysis import calculate_portfolio_value, get_summary_statistics
from components.animated_loader import show_stock_loader

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    logger.info("Initializing Advanced Analysis page...")

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

        1. Select 3-15 stocks for analysis
        2. Choose investment amount
        3. View projected returns
        4. Analyze risk metrics
        """)

    # Stock Selection
    st.header("Stock Selection")

    try:
        logger.info("Setting up stock selection...")

        # Sector selection
        available_sectors = ["All Sectors"] + list(set(data['sector'] for data in JSE_TOP_50.values()))
        selected_sector = st.selectbox(
            "Choose Sector for Analysis",
            options=available_sectors,
            help="Select a sector to analyze all its stocks, or choose 'All Sectors' for custom selection"
        )
        logger.info(f"Selected sector: {selected_sector}")

        # Initialize selected stocks in session state
        if 'selected_stocks' not in st.session_state:
            st.session_state.selected_stocks = []

        # Auto-select all stocks in sector if sector is chosen
        if selected_sector != "All Sectors":
            sector_stocks = [
                symbol for symbol, data in JSE_TOP_50.items()
                if data['sector'] == selected_sector
            ]
            st.session_state.selected_stocks = sector_stocks
            st.info(f"✨ Auto-selected all {len(sector_stocks)} stocks in the {selected_sector} sector")
        else:
            # Manual stock selection
            selected_stocks = st.multiselect(
                "Select Stocks for Analysis (3-15 stocks)",
                options=list(JSE_TOP_50.keys()),
                format_func=lambda x: f"{x} - {JSE_TOP_50[x]['name']} ({JSE_TOP_50[x]['sector']})",
                help="Choose between 3 and 15 stocks for comprehensive analysis",
                default=st.session_state.selected_stocks
            )
            st.session_state.selected_stocks = selected_stocks

        # Display selection counter
        num_selected = len(st.session_state.selected_stocks)
        st.write(f"Selected stocks: {num_selected}/15")

        # Validation
        if num_selected < 3:
            st.warning("⚠️ Please select at least 3 stocks for meaningful analysis")
            st.stop()
        elif num_selected > 15:
            st.error("⚠️ Maximum selection is 15 stocks. Please reduce your selection.")
            st.stop()

        # Analysis section - only show if we have valid selection
        if num_selected >= 3:
            # Show loading animation
            loader = show_stock_loader("Calculating portfolio metrics...")

            try:
                # Calculate portfolio metrics
                portfolio_metrics = calculate_portfolio_metrics(st.session_state.selected_stocks)
                loader.empty()

                # Display metrics in columns
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Total Portfolio Value",
                        f"R{portfolio_metrics['Total Market Cap']/1e9:.2f}B",
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
                for stock in st.session_state.selected_stocks:
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

            except Exception as e:
                logger.error(f"Error in portfolio analysis: {str(e)}")
                st.error("Error calculating portfolio metrics. Please try again.")
                if loader:
                    loader.empty()

    except Exception as e:
        logger.error(f"Error in stock selection: {str(e)}")
        st.error("Error in stock selection. Please try again.")

    # Disclaimer
    st.warning("""
    ⚠️ **Important Disclaimer**

    This tool provides historical analysis and simulated projections for educational purposes only:
    - Past performance does not guarantee future results
    - All projections are based on historical data and assumptions
    - Market conditions can change rapidly
    - Consider consulting a financial advisor for personalized advice
    """)

except Exception as e:
    logger.error(f"Unexpected error in Advanced Analysis page: {str(e)}")
    st.error("An unexpected error occurred. Please try again later.")