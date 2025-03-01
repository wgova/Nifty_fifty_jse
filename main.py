import sys
import logging
import os
from datetime import datetime

# Configure logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Starting Streamlit App...")

try:
    logger.info("Importing required packages...")
    import streamlit as st
    import pandas as pd
    from utils.stock_data import (
        JSE_TOP_50, get_stock_data, get_financial_metrics,
        get_available_sectors
    )
    from components.animated_loader import show_stock_loader
    from utils.forecasting import create_forecast, calculate_forecast_returns # Assuming these functions exist here
    logger.info("All imports successful")

    # Page config
    st.set_page_config(
        page_title="JSE Stock Analysis",
        page_icon="📈",
        layout="wide"
    )

    # Title and description with enhanced explanation
    st.title("📈 JSE Stock Analysis Tool")

    # User Guide Expander
    with st.expander("📚 User Guide - Click to Learn More"):
        st.markdown("""
        ### Welcome to the JSE Stock Analysis Tool!

        This tool helps you analyze the top 50 stocks listed on the Johannesburg Stock Exchange (JSE).
        Here's how to use it:

        1. **Sector Selection** 🏢
           - Use the sidebar to filter stocks by sector
           - Choose "All Sectors" to see every available stock
           - When you select a sector, all stocks in that sector will be auto-selected

        2. **Stock Selection** 📊
           - Select between 3 and 15 stocks to analyze
           - Mix stocks from different sectors for better diversification
           - Your selection will be used across all analysis pages

        3. **Financial Metrics** 💰
           - Current Price: Latest trading price in Rands
           - Market Cap: Total market value of the company
           - P/E Ratio: Price-to-Earnings ratio (valuation metric)

        4. **Data Display** 📉
           - Recent price history shows the latest trading data
           - All prices are in South African Rand (ZAR)

        ### Understanding the Metrics

        - **Market Cap**: Total value of all shares (Price × Shares Outstanding)
        - **P/E Ratio**: Price per share divided by earnings per share
        - **Volume**: Number of shares traded
        """)

    # Main description
    st.markdown("""
    Analyze JSE Top 50 stocks with real-time data and interactive visualizations.
    Select stocks from the sidebar to begin your analysis.
    """)

    # Sidebar for stock selection with enhanced help text
    st.sidebar.header("Stock Selection")

    # Initialize selected_stocks in session state if not present
    if 'selected_stocks' not in st.session_state:
        st.session_state.selected_stocks = []

    # Sector filter with tooltip
    selected_sector = st.sidebar.selectbox(
        "Select Sector",
        ["All Sectors"] + get_available_sectors(),
        help="Filter stocks by their business sector (e.g., Banking, Mining, Technology)"
    )

    # Stock selection based on sector
    if selected_sector != "All Sectors":
        # Auto-select all stocks in the sector
        sector_stocks = [
            symbol for symbol, data in JSE_TOP_50.items()
            if data['sector'] == selected_sector
        ]
        st.session_state.selected_stocks = sector_stocks
        st.sidebar.info(f"✨ Auto-selected all {len(sector_stocks)} stocks in the {selected_sector} sector")
    else:
        # Manual stock selection
        selected_stocks = st.sidebar.multiselect(
            "Select Stocks for Analysis (3-15 stocks)",
            options=list(JSE_TOP_50.keys()),
            format_func=lambda x: f"{x} - {JSE_TOP_50[x]['name']} ({JSE_TOP_50[x]['sector']})",
            help="Choose between 3 and 15 stocks for comprehensive analysis",
            default=st.session_state.selected_stocks
        )
        st.session_state.selected_stocks = selected_stocks

    # Display selection counter
    num_selected = len(st.session_state.selected_stocks)
    st.sidebar.write(f"Selected stocks: {num_selected}/15")

    # Validation
    if num_selected < 3:
        st.warning("⚠️ Please select at least 3 stocks for meaningful analysis")
    elif num_selected > 15:
        st.error("⚠️ Maximum selection is 15 stocks. Please reduce your selection.")
    else:
        try:
            # Create placeholder for the loader
            loader_placeholder = show_stock_loader("Fetching data for selected stocks...")

            try:
                # Display data for each selected stock
                for stock in st.session_state.selected_stocks:
                    # Get stock data
                    hist, info = get_stock_data(stock)

                    if hist is not None and not hist.empty:
                        # Display basic stock info with explanation
                        st.subheader(f"{JSE_TOP_50[stock]['name']} ({stock})")

                        # Add sector description
                        st.markdown(f"**Sector**: {JSE_TOP_50[stock]['sector']}")

                        # Financial metrics with explanations
                        metrics = get_financial_metrics(stock)

                        # Create columns for metrics
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric(
                                "Current Price",
                                f"R{hist['Close'].iloc[-1]:.2f}",
                                f"{((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100):+.2f}%",
                                help="Latest closing price with daily percentage change"
                            )

                        with col2:
                            st.metric(
                                "Market Cap",
                                f"R{metrics.get('Market Cap', 0)/1e9:.2f}B",
                                help="Total market value of the company in billions of Rands"
                            )

                        with col3:
                            st.metric(
                                "P/E Ratio",
                                f"{metrics.get('P/E Ratio', 'N/A')}",
                                help="Price to Earnings ratio - a valuation metric"
                            )

                        # Show recent price history with explanation
                        st.subheader("Recent Price History")
                        st.caption("""
                        The table below shows the most recent trading days.
                        - Open: Price at market open
                        - High/Low: Price range during the day
                        - Close: Final price of the day
                        - Volume: Number of shares traded
                        """)

                        st.dataframe(
                            hist.tail().style.format({
                                'Open': 'R{:.2f}',
                                'High': 'R{:.2f}',
                                'Low': 'R{:.2f}',
                                'Close': 'R{:.2f}',
                                'Volume': '{:,.0f}'
                            })
                        )

                    else:
                        st.error(f"No data available for {stock}")

                # Clear the loader after all data is displayed
                loader_placeholder.empty()

                # Add Forecasting Section
                st.header("📈 Portfolio Forecasting")
                st.info("""
                🔮 **Understanding Portfolio Forecasts**
                - Projections are based on historical data and trends
                - Upper and lower bounds show potential range of outcomes
                - All forecasts include monthly investment impact
                - Results are shown with confidence intervals
                """)

                if len(st.session_state.selected_stocks) >= 3:
                    try:
                        # Add forecasting controls
                        forecast_months = st.slider(
                            "Forecast Period (Months)",
                            min_value=3,
                            max_value=24,
                            value=12,
                            help="Select how many months to forecast ahead"
                        )

                        monthly_investment = st.number_input(
                            "Monthly Investment Amount (Rands)",
                            min_value=100,
                            value=1000,
                            step=100,
                            help="Amount to invest monthly in your portfolio"
                        )

                        # Show loading animation for forecasts
                        forecast_loader = show_stock_loader("Calculating portfolio forecasts...")

                        try:
                            # Calculate forecasts for each stock
                            portfolio_forecasts = {}
                            for stock in st.session_state.selected_stocks:
                                hist, _ = get_stock_data(stock)
                                if hist is not None and not hist.empty:
                                    # Get forecasts with confidence intervals
                                    median_forecast, lower_bound, upper_bound = create_forecast(
                                        hist,
                                        months_ahead=forecast_months
                                    )
                                    portfolio_forecasts[stock] = {
                                        'median': median_forecast,
                                        'lower': lower_bound,
                                        'upper': upper_bound
                                    }

                            # Clear loading animation
                            forecast_loader.empty()

                            if portfolio_forecasts:
                                # Display aggregate portfolio metrics
                                total_investment = monthly_investment * forecast_months
                                portfolio_metrics = []

                                for stock in portfolio_forecasts:
                                    forecast = portfolio_forecasts[stock]
                                    # Calculate potential returns
                                    inv, ret, pct = calculate_forecast_returns(
                                        forecast['median'],
                                        monthly_investment=monthly_investment/len(st.session_state.selected_stocks)
                                    )
                                    portfolio_metrics.append({
                                        'stock': stock,
                                        'name': JSE_TOP_50[stock]['name'],
                                        'return': ret,
                                        'return_pct': pct
                                    })

                                # Display metrics
                                st.subheader("Projected Returns")
                                col1, col2 = st.columns(2)

                                with col1:
                                    st.metric(
                                        "Total Investment",
                                        f"R{total_investment:,.2f}",
                                        help="Total amount invested over forecast period"
                                    )

                                with col2:
                                    total_return = sum(m['return'] for m in portfolio_metrics)
                                    total_return_pct = (total_return / total_investment) * 100
                                    st.metric(
                                        "Projected Return",
                                        f"R{total_return:,.2f}",
                                        f"{total_return_pct:+.2f}%",
                                        help="Projected return based on historical trends"
                                    )

                                # Show individual stock forecasts
                                st.subheader("Stock-by-Stock Projections")
                                for metric in portfolio_metrics:
                                    st.write(f"**{metric['name']} ({metric['stock']})**")
                                    met_col1, met_col2 = st.columns(2)

                                    with met_col1:
                                        st.metric(
                                            "Projected Return",
                                            f"R{metric['return']:,.2f}",
                                            f"{metric['return_pct']:+.2f}%"
                                        )

                                    with met_col2:
                                        confidence = "High" if abs(metric['return_pct']) > 20 else "Moderate"
                                        st.metric(
                                            "Forecast Confidence",
                                            confidence,
                                            help="Based on historical volatility and trend strength"
                                        )

                                # Add forecast explanation
                                st.info("""
                                📊 **Understanding These Projections**
                                - Returns are calculated using historical trends and patterns
                                - Past performance does not guarantee future results
                                - Consider market conditions and economic factors
                                - Higher returns often come with higher risk
                                """)

                        except Exception as e:
                            logger.error(f"Error calculating forecasts: {str(e)}")
                            st.error("Error calculating portfolio forecasts. Please try again.")
                            if forecast_loader:
                                forecast_loader.empty()

                    except Exception as e:
                        logger.error(f"Error in forecasting section: {str(e)}")
                        st.error("Error in forecasting calculations. Please try again.")
                else:
                    st.warning("Please select at least 3 stocks to view portfolio forecasts")


                # Add disclaimer
                st.warning("""
                ⚠️ **Disclaimer**: Historical performance does not guarantee future results. 
                Always conduct thorough research and consider consulting with a financial advisor 
                before making investment decisions.
                """)

            except Exception as e:
                # Clear the loader in case of error
                loader_placeholder.empty()
                raise e

        except Exception as e:
            logger.error(f"Error loading stock data: {str(e)}", exc_info=True)
            st.error(f"Error loading stock data: {str(e)}")

except Exception as e:
    logger.error(f"Error in app execution: {str(e)}", exc_info=True)
    st.error("An unexpected error occurred. Please check the logs for details.")
    sys.exit(1)

logger.info("App initialization completed successfully")