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
logger.info(f"Python version: {sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Start time: {datetime.now()}")

try:
    logger.info("Importing required packages...")
    import streamlit as st
    import pandas as pd
    from utils.stock_data import (
        JSE_TOP_50, get_stock_data, get_financial_metrics,
        get_available_sectors, get_stocks_by_sector
    )
    logger.info("All imports successful")

    # Page config
    logger.info("Setting up page configuration...")
    st.set_page_config(
        page_title="JSE Stock Analysis",
        page_icon="📈",
        layout="wide"
    )
    logger.info("Page configuration completed successfully")

    # Title and description
    logger.info("Setting up main page content...")
    st.title("📈 JSE Stock Analysis Tool")
    st.markdown("""
    Analyze JSE Top 50 stocks with real-time data and interactive visualizations.
    Select 3-15 stocks to create your portfolio analysis.
    """)
    logger.info("Main page content setup completed")

    # Sidebar for stock selection
    logger.info("Setting up sidebar...")
    st.sidebar.header("Portfolio Selection")

    # Sector filter
    logger.info("Loading available sectors...")
    available_sectors = get_available_sectors()
    logger.info(f"Found {len(available_sectors)} sectors")

    selected_sector = st.sidebar.selectbox(
        "Filter by Sector",
        ["All Sectors"] + available_sectors,
        help="Filter stocks by sector"
    )
    logger.info(f"User selected sector: {selected_sector}")

    # Get stocks for selected sector
    if selected_sector == "All Sectors":
        available_stocks = list(JSE_TOP_50.keys())
        default_stocks = []  # No default selection for All Sectors
    else:
        sector_stocks = get_stocks_by_sector(selected_sector)
        available_stocks = list(sector_stocks.keys())
        default_stocks = available_stocks  # Pre-select all stocks in the sector

    logger.info(f"Available stocks for selected sector: {len(available_stocks)}")

    selected_stocks = st.sidebar.multiselect(
        "Select Stocks (3-15)",
        available_stocks,
        default=default_stocks,
        format_func=lambda x: f"{x} - {JSE_TOP_50[x]['name']} ({JSE_TOP_50[x]['sector']})",
        help="Select between 3 and 15 stocks for your portfolio"
    )

    # Validate stock selection
    if len(selected_stocks) > 0:
        if len(selected_stocks) < 3:
            st.warning("Please select at least 3 stocks for portfolio analysis")
        elif len(selected_stocks) > 15:
            st.warning("Please select no more than 15 stocks")
        else:
            logger.info(f"User selected {len(selected_stocks)} stocks")
            # Display selected stocks
            st.subheader("Selected Stocks")
            for symbol in selected_stocks:
                st.write(f"• {JSE_TOP_50[symbol]['name']} ({symbol}) - {JSE_TOP_50[symbol]['sector']}")

            #Processing selected stocks 
            for stock in selected_stocks:
                try:
                    logger.info(f"Fetching data for {stock}...")
                    with st.spinner(f'Loading data for {stock}...'):
                        hist, info = get_stock_data(stock)
                        logger.info(f"Data fetched successfully for {stock}")
                        if hist is not None and not hist.empty:
                            #Display basic stock info
                            st.subheader(f"{JSE_TOP_50[stock]['name']} ({stock})")

                            # Financial metrics
                            metrics = get_financial_metrics(stock)
                            logger.info("Financial metrics retrieved successfully")

                            # Create columns for metrics
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                st.metric(
                                    "Current Price",
                                    f"R{hist['Close'].iloc[-1]:.2f}",
                                    f"{((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100):+.2f}%"
                                )

                            with col2:
                                st.metric(
                                    "Market Cap",
                                    f"R{metrics.get('Market Cap', 0)/1e9:.2f}B"
                                )

                            with col3:
                                st.metric(
                                    "P/E Ratio",
                                    f"{metrics.get('P/E Ratio', 'N/A')}"
                                )

                            # Show recent price history
                            st.subheader("Recent Price History")
                            st.dataframe(
                                hist.tail().style.format({
                                    'Open': 'R{:.2f}',
                                    'High': 'R{:.2f}',
                                    'Low': 'R{:.2f}',
                                    'Close': 'R{:.2f}',
                                    'Volume': '{:,.0f}'
                                })
                            )
                            logger.info("All data displayed successfully")
                        else:
                            logger.warning(f"No data available for {stock}")
                            st.error(f"No data available for {stock}")
                except Exception as e:
                    logger.error(f"Error loading stock data for {stock}: {str(e)}", exc_info=True)
                    st.error(f"Error loading stock data for {stock}: {str(e)}")




    else:
        logger.info("No stock selected yet")
        st.info("Please select a stock to analyze")

except Exception as e:
    logger.error(f"Error in app execution: {str(e)}", exc_info=True)
    st.error("An unexpected error occurred. Please check the logs for details.")
    sys.exit(1)

logger.info("App initialization completed successfully")