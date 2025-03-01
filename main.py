import sys
import logging
import os
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    logger.info("Importing required packages...")
    import streamlit as st
    import pandas as pd
    import matplotlib.pyplot as plt
    from utils.stock_data import (
        JSE_TOP_50, get_stock_data, get_financial_metrics,
        get_available_sectors, get_stocks_by_sector, calculate_portfolio_metrics
    )
    from utils.analysis import prepare_chart_data
    logger.info("All imports successful")

    # Color palette
    COLORS = {
        'price': '#FF4B4B',
        'volume': '#4ECDC4',
        'grid': '#2F4F4F'
    }

    # Page config
    st.set_page_config(
        page_title="JSE Stock Analysis",
        page_icon="📈",
        layout="wide"
    )

    # Title and description
    st.title("📈 JSE Stock Analysis Tool")
    st.markdown("""
    Analyze JSE Top 50 stocks with real-time data and interactive visualizations.
    Select 3-15 stocks to create your portfolio analysis.
    """)

    # Sidebar for stock selection
    st.sidebar.header("Portfolio Selection")

    # Year range selector
    current_year = datetime.now().year
    min_year = current_year - 10  # Data available for last 10 years
    years_back = st.sidebar.slider(
        "Select Time Range (Years)",
        min_value=1,
        max_value=10,
        value=5,
        help="Choose how many years of historical data to display"
    )
    start_date = datetime.now() - timedelta(days=365 * years_back)

    # Sector filter
    available_sectors = get_available_sectors()
    selected_sector = st.sidebar.selectbox(
        "Filter by Sector",
        ["All Sectors"] + available_sectors,
        help="Filter stocks by sector"
    )

    # Get stocks for selected sector
    if selected_sector == "All Sectors":
        available_stocks = list(JSE_TOP_50.keys())
        default_stocks = []
    else:
        sector_stocks = get_stocks_by_sector(selected_sector)
        available_stocks = list(sector_stocks.keys())
        default_stocks = available_stocks[:3]  # Select first 3 stocks by default

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
            logger.info(f"Processing {len(selected_stocks)} stocks")

            valid_stocks = []
            for symbol in selected_stocks:
                try:
                    hist, info = get_stock_data(symbol)
                    if hist is not None and not hist.empty:
                        valid_stocks.append(symbol)
                except Exception as e:
                    logger.error(f"Error loading stock data for {symbol}: {str(e)}")
                    continue

            if len(valid_stocks) >= 3:
                # Calculate and display portfolio metrics
                try:
                    portfolio_metrics = calculate_portfolio_metrics(valid_stocks)

                    # Portfolio Overview Section
                    st.header("Portfolio Overview")
                    overview_col1, overview_col2, overview_col3 = st.columns(3)

                    with overview_col1:
                        st.metric(
                            "Total Market Cap",
                            f"R{portfolio_metrics['Total Market Cap']/1e9:.2f}B"
                        )

                    with overview_col2:
                        st.metric(
                            "Weighted P/E Ratio",
                            f"{portfolio_metrics['Weighted P/E']:.2f}"
                        )

                    with overview_col3:
                        st.metric(
                            "Weighted Dividend Yield",
                            f"{portfolio_metrics['Weighted Dividend Yield']*100:.2f}%"
                        )
                except Exception as e:
                    logger.error(f"Error calculating portfolio metrics: {str(e)}", exc_info=True)

                # Display Selected Stocks
                st.header("Selected Stocks")
                for symbol in valid_stocks:
                    try:
                        hist, info = get_stock_data(symbol)
                        metrics = get_financial_metrics(symbol)

                        st.header(f"{JSE_TOP_50[symbol]['name']} ({symbol})")

                        # Create three columns for metrics
                        col1, col2, col3 = st.columns(3)

                        # Current price and daily change
                        current_price = hist['Close'].iloc[-1]
                        prev_price = hist['Close'].iloc[-2]
                        price_change = ((current_price - prev_price) / prev_price) * 100

                        with col1:
                            st.metric(
                                "Current Price",
                                f"R{current_price:.2f}",
                                f"{price_change:+.2f}%"
                            )
                            st.metric(
                                "Market Cap",
                                f"R{metrics['Market Cap']/1e9:.2f}B" if isinstance(metrics['Market Cap'], (int, float)) else "N/A"
                            )
                            st.metric(
                                "52W High/Low",
                                f"R{metrics['52 Week High']:.2f} / R{metrics['52 Week Low']:.2f}" if isinstance(metrics['52 Week High'], (int, float)) else "N/A"
                            )

                        with col2:
                            st.metric(
                                "P/E Ratio",
                                f"{metrics['P/E Ratio']:.2f}" if isinstance(metrics['P/E Ratio'], (int, float)) else "N/A"
                            )
                            st.metric(
                                "Price/Book",
                                f"{metrics['Price/Book']:.2f}" if isinstance(metrics['Price/Book'], (int, float)) else "N/A"
                            )
                            st.metric(
                                "ROE",
                                f"{metrics['ROE']*100:.1f}%" if isinstance(metrics['ROE'], (int, float)) else "N/A"
                            )

                        with col3:
                            div_text = (f"R{metrics['Latest Dividend']:.2f} ({metrics['Latest Dividend Date']})" 
                                      if metrics['Latest Dividend'] > 0 else "No recent dividend")
                            div_delta = (f"{metrics['Dividend Change']:+.1f}%" 
                                       if metrics['Dividend Change'] != 0 else None)

                            st.metric(
                                "Latest Dividend",
                                div_text,
                                div_delta
                            )
                            st.metric(
                                "Dividend Yield",
                                f"{metrics['Dividend Yield']*100:.2f}%" if isinstance(metrics['Dividend Yield'], (int, float)) else "N/A"
                            )
                            st.metric(
                                "Beta",
                                f"{metrics['Beta']:.2f}" if isinstance(metrics['Beta'], (int, float)) else "N/A"
                            )

                        try:
                            # Create price and volume chart
                            processed_data = hist[hist.index >= start_date].copy()

                            if not processed_data.empty:
                                # Create figure with two y-axes
                                fig, ax1 = plt.subplots(figsize=(12, 6))

                                # Plot price on primary y-axis
                                ax1.plot(processed_data.index, processed_data['Close'], 
                                       color=COLORS['price'], linewidth=2)
                                ax1.set_xlabel('Date')
                                ax1.set_ylabel('Price (R)', color=COLORS['price'])
                                ax1.tick_params(axis='y', labelcolor=COLORS['price'])
                                ax1.grid(True, alpha=0.2)

                                # Plot volume on secondary y-axis
                                ax2 = ax1.twinx()
                                ax2.bar(processed_data.index, processed_data['Volume'], 
                                      alpha=0.3, color=COLORS['volume'])
                                ax2.set_ylabel('Volume', color=COLORS['volume'])
                                ax2.tick_params(axis='y', labelcolor=COLORS['volume'])

                                # Set title
                                plt.title(f"{JSE_TOP_50[symbol]['name']} - Price and Volume Chart")

                                # Show the plot
                                st.pyplot(fig)
                                plt.close()
                            else:
                                st.warning(f"No data available for the selected time period for {symbol}")

                        except Exception as e:
                            logger.error(f"Error creating chart for {symbol}: {str(e)}")
                            st.error(f"Could not create chart for {symbol}")

                    except Exception as e:
                        logger.error(f"Error displaying stock data for {symbol}: {str(e)}")
                        continue
            else:
                st.warning("Please select at least 3 stocks with available data")
    else:
        st.info("Please select stocks to analyze")

except Exception as e:
    logger.error(f"Error in app execution: {str(e)}")
    st.error("An unexpected error occurred. Please check the logs for details.")
    sys.exit(1)