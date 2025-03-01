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
    import plotly.graph_objects as go
    from utils.stock_data import (
        JSE_TOP_50, get_stock_data, get_financial_metrics,
        get_available_sectors, get_stocks_by_sector, calculate_portfolio_metrics
    )
    logger.info("All imports successful")

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

    # Sector filter
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

            # Process and display only stocks with available data
            valid_stocks = []
            for symbol in selected_stocks:
                try:
                    hist, info = get_stock_data(symbol)
                    if hist is not None and not hist.empty:
                        valid_stocks.append(symbol)
                except Exception as e:
                    logger.error(f"Error loading stock data for {symbol}: {str(e)}", exc_info=True)
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
                        st.subheader(f"{JSE_TOP_50[symbol]['name']} ({symbol})")

                        # Financial metrics
                        metrics = get_financial_metrics(symbol)

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

                        logger.info(f"Creating chart for {symbol}")
                        try:
                            # Log data info for debugging
                            logger.debug(f"Data for {symbol}:")
                            logger.debug(f"Shape: {hist.shape}")
                            logger.debug(f"Columns: {hist.columns}")
                            logger.debug(f"Index type: {type(hist.index)}")
                            logger.debug(f"Close type: {hist['Close'].dtype}")
                            logger.debug(f"Volume type: {hist['Volume'].dtype}")

                            # Data validation
                            if hist is None or hist.empty:
                                logger.error(f"No historical data available for {symbol}")
                                st.error(f"No historical data available for {symbol}")
                                continue

                            if 'Close' not in hist.columns or 'Volume' not in hist.columns:
                                logger.error(f"Missing required columns for {symbol}")
                                st.error(f"Missing required data columns for {symbol}")
                                continue

                            # Convert index to datetime if needed
                            if not isinstance(hist.index, pd.DatetimeIndex):
                                hist.index = pd.to_datetime(hist.index)

                            # Ensure data is properly sorted
                            hist = hist.sort_index()

                            # Convert data to appropriate types
                            hist['Close'] = pd.to_numeric(hist['Close'], errors='coerce')
                            hist['Volume'] = pd.to_numeric(hist['Volume'], errors='coerce')

                            # Remove any NaN values
                            hist = hist.dropna(subset=['Close', 'Volume'])

                            # Historical Price Chart
                            fig = go.Figure()

                            # Add price line
                            fig.add_trace(go.Scatter(
                                x=hist.index,
                                y=hist['Close'],
                                name='Close Price',
                                line=dict(color='#FF4B4B', width=2)
                            ))

                            # Add volume bars with adjusted scale
                            max_price = hist['Close'].max()
                            volume_scale = max_price / hist['Volume'].max() if hist['Volume'].max() > 0 else 1
                            scaled_volume = hist['Volume'] * volume_scale

                            fig.add_trace(go.Bar(
                                x=hist.index,
                                y=scaled_volume,
                                name='Volume',
                                yaxis='y2',
                                opacity=0.3,
                                marker_color='#636363'
                            ))

                            # Update layout with better formatting
                            fig.update_layout(
                                title=dict(
                                    text=f"{JSE_TOP_50[symbol]['name']} - Historical Price and Volume",
                                    x=0.5,
                                    xanchor='center'
                                ),
                                yaxis=dict(
                                    title="Price (R)",
                                    titlefont=dict(color="#FF4B4B"),
                                    tickfont=dict(color="#FF4B4B"),
                                    gridcolor='rgba(255, 255, 255, 0.1)'
                                ),
                                yaxis2=dict(
                                    title="Volume",
                                    titlefont=dict(color="#636363"),
                                    tickfont=dict(color="#636363"),
                                    overlaying="y",
                                    side="right",
                                    showgrid=False
                                ),
                                hovermode='x unified',
                                template='plotly_dark',
                                height=500,
                                showlegend=True,
                                legend=dict(
                                    yanchor="top",
                                    y=0.99,
                                    xanchor="left",
                                    x=0.01
                                ),
                                margin=dict(l=50, r=50, t=50, b=50)
                            )

                            # Add range selector
                            fig.update_xaxes(
                                rangeslider_visible=True,
                                rangeselector=dict(
                                    buttons=list([
                                        dict(count=1, label="1m", step="month", stepmode="backward"),
                                        dict(count=6, label="6m", step="month", stepmode="backward"),
                                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                                        dict(count=1, label="1y", step="year", stepmode="backward"),
                                        dict(step="all")
                                    ])
                                )
                            )

                            st.plotly_chart(fig, use_container_width=True)
                            logger.info(f"Chart created successfully for {symbol}")
                        except Exception as e:
                            logger.error(f"Error creating chart for {symbol}: {str(e)}", exc_info=True)
                            st.error(f"Error creating chart for {symbol}")

                        # Show recent price history table
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
                    except Exception as e:
                        logger.error(f"Error displaying stock data for {symbol}: {str(e)}", exc_info=True)
                        continue
            else:
                st.warning("Please select at least 3 stocks with available data")
    else:
        st.info("Please select stocks to analyze")

except Exception as e:
    logger.error(f"Error in app execution: {str(e)}", exc_info=True)
    st.error("An unexpected error occurred. Please check the logs for details.")
    sys.exit(1)