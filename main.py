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

        2. **Stock Selection** 📊
           - Select a specific stock to analyze
           - View company name, ticker symbol, and sector

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
    Select a stock from the sidebar to begin your analysis.
    """)

    # Sidebar for stock selection with enhanced help text
    st.sidebar.header("Stock Selection")

    # Sector filter with tooltip
    selected_sector = st.sidebar.selectbox(
        "Select Sector",
        ["All Sectors"] + get_available_sectors(),
        help="Filter stocks by their business sector (e.g., Banking, Mining, Technology)"
    )

    # Stock selection with detailed tooltip
    available_stocks = [
        symbol for symbol, data in JSE_TOP_50.items()
        if selected_sector == "All Sectors" or data['sector'] == selected_sector
    ]

    selected_stock = st.sidebar.selectbox(
        "Select Stock",
        available_stocks,
        format_func=lambda x: f"{x} - {JSE_TOP_50[x]['name']} ({JSE_TOP_50[x]['sector']})",
        help="Choose a stock to analyze. Format: Ticker - Company Name (Sector)"
    )

    if selected_stock:
        try:
            with st.spinner('Loading stock data...'):
                # Get stock data
                hist, info = get_stock_data(selected_stock)

                if hist is not None and not hist.empty:
                    # Display basic stock info with explanation
                    st.subheader(f"{JSE_TOP_50[selected_stock]['name']} ({selected_stock})")

                    # Add sector description
                    st.markdown(f"**Sector**: {JSE_TOP_50[selected_stock]['sector']}")

                    # Financial metrics with explanations
                    metrics = get_financial_metrics(selected_stock)

                    # Metrics explanation
                    st.info("""
                    📊 **Understanding the Metrics Below**
                    - Current Price: Latest trading price in Rands (ZAR)
                    - Market Cap: Total company value in billions of Rands
                    - P/E Ratio: Lower values generally indicate better value
                    """)

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

                    # Add disclaimer
                    st.warning("""
                    ⚠️ **Disclaimer**: Historical performance does not guarantee future results. 
                    Always conduct thorough research and consider consulting with a financial advisor 
                    before making investment decisions.
                    """)
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