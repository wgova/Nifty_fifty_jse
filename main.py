import sys
import logging
import os

# Configure logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Starting Streamlit App...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")

try:
    logger.info("Importing required packages...")
    import streamlit as st
    import pandas as pd
    from utils.stock_data import (
        JSE_TOP_50, get_stock_data, get_financial_metrics,
        get_available_sectors
    )
    logger.info("All imports successful")

    # Page config
    st.set_page_config(
        page_title="JSE Stock Analysis",
        page_icon="📈",
        layout="wide"
    )
    logger.info("Page config set")

    # Title and description
    st.title("📈 JSE Stock Analysis Tool")
    st.markdown("""
    Analyze JSE Top 50 stocks with real-time data and interactive visualizations.
    Select a stock from the sidebar to begin.
    """)

    # Sidebar for stock selection
    st.sidebar.header("Stock Selection")

    # Sector filter
    selected_sector = st.sidebar.selectbox(
        "Select Sector",
        ["All Sectors"] + get_available_sectors(),
        help="Filter stocks by sector"
    )

    # Stock selection
    available_stocks = [
        symbol for symbol, data in JSE_TOP_50.items()
        if selected_sector == "All Sectors" or data['sector'] == selected_sector
    ]

    selected_stock = st.sidebar.selectbox(
        "Select Stock",
        available_stocks,
        format_func=lambda x: f"{x} - {JSE_TOP_50[x]['name']} ({JSE_TOP_50[x]['sector']})"
    )

    if selected_stock:
        try:
            with st.spinner('Loading stock data...'):
                # Get stock data
                hist, info = get_stock_data(selected_stock)

                if hist is not None and not hist.empty:
                    # Display basic stock info
                    st.subheader(f"{JSE_TOP_50[selected_stock]['name']} ({selected_stock})")

                    # Financial metrics
                    metrics = get_financial_metrics(selected_stock)

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
                else:
                    st.error("No data available for the selected stock")
        except Exception as e:
            logger.error(f"Error loading stock data: {str(e)}", exc_info=True)
            st.error(f"Error loading stock data: {str(e)}")
    else:
        st.info("Please select a stock to analyze")

except Exception as e:
    logger.error(f"Error in app execution: {str(e)}", exc_info=True)
    sys.exit(1)