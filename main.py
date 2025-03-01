import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.stock_data import (
    JSE_TOP_50, get_stock_data, get_financial_metrics, calculate_portfolio_metrics,
    get_available_sectors, get_stocks_by_sector, calculate_sector_metrics
)
from utils.analysis import calculate_portfolio_value, calculate_returns, get_summary_statistics
from utils.forecasting import (
    create_forecast,
    calculate_forecast_returns, generate_stock_recommendation
)

# Page config
st.set_page_config(
    page_title="JSE Stock Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('.streamlit/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Title
st.title("📈 JSE Stock Analysis Tool")
st.markdown("---")

# Sidebar
st.sidebar.header("Portfolio Selection")

# Sector selection
selected_sector = st.sidebar.selectbox(
    "Select Sector",
    ["All Sectors"] + get_available_sectors(),
    help="Select a specific sector to analyze or 'All Sectors' for custom selection"
)

# Stock selection based on sector
if selected_sector == "All Sectors":
    selected_stocks = st.sidebar.multiselect(
        "Select up to 5 stocks",
        options=list(JSE_TOP_50.keys()),
        default=[list(JSE_TOP_50.keys())[0]],
        max_selections=5,
        format_func=lambda x: f"{x} - {JSE_TOP_50[x]['name']} ({JSE_TOP_50[x]['sector']})"
    )
else:
    sector_stocks = get_stocks_by_sector(selected_sector)
    selected_stocks = st.sidebar.multiselect(
        f"Select {selected_sector} stocks",
        options=list(sector_stocks.keys()),
        default=list(sector_stocks.keys()),
        format_func=lambda x: f"{x} - {JSE_TOP_50[x]['name']}"
    )

# Main content
if not selected_stocks:
    st.warning("Please select at least one stock to analyze.")
else:
    # Calculate portfolio and sector metrics
    portfolio_metrics = calculate_portfolio_metrics(selected_stocks)
    if selected_sector != "All Sectors":
        sector_metrics = calculate_sector_metrics(selected_sector)

        # Display sector overview
        st.subheader(f"{selected_sector} Sector Overview")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Sector Market Cap",
                f"R{sector_metrics['Total Market Cap']:,.0f}"
            )
        with col2:
            st.metric(
                "Sector P/E",
                f"{sector_metrics['Weighted P/E']:.2f}"
            )
        with col3:
            st.metric(
                "Sector Dividend Yield",
                f"{sector_metrics['Weighted Dividend Yield']:.2%}"
            )
        with col4:
            st.metric(
                "Number of Companies",
                f"{sector_metrics['Number of Companies']}"
            )

    # Display portfolio overview
    st.subheader("Portfolio Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Total Market Cap",
            f"R{portfolio_metrics['Total Market Cap']:,.0f}"
        )
    with col2:
        st.metric(
            "Portfolio P/E",
            f"{portfolio_metrics['Weighted P/E']:.2f}"
        )
    with col3:
        st.metric(
            "Portfolio Dividend Yield",
            f"{portfolio_metrics['Weighted Dividend Yield']:.2%}"
        )

    # Create tabs
    tabs = st.tabs(["📊 Overview", "💰 Portfolio Analysis", "🔮 Forecasting"])

    with tabs[0]:
        # Financial metrics table
        st.subheader("Financial Metrics")
        metrics_data = {}
        for symbol in selected_stocks:
            metrics = get_financial_metrics(symbol)
            formatted_metrics = {}
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    if key == 'Market Cap':
                        formatted_metrics[key] = f"R{value:,.0f}" if value != 'N/A' else 'N/A'
                    elif key == 'Dividend Yield':
                        formatted_metrics[key] = f"{value:.2%}" if value != 'N/A' else 'N/A'
                    else:
                        formatted_metrics[key] = f"{value:,.2f}" if value != 'N/A' else 'N/A'
                else:
                    formatted_metrics[key] = value
            metrics_data[f"{symbol} ({JSE_TOP_50[symbol]['name']})"] = formatted_metrics

        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(
            metrics_df,
            use_container_width=True,
            height=250
        )

        # Historical price chart
        st.subheader("Historical Price Trends")
        fig = go.Figure()
        for symbol in selected_stocks:
            hist, _ = get_stock_data(symbol)
            if hist is not None:
                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=hist['Close'],
                    name=f"{symbol} - {JSE_TOP_50[symbol]['name']}",
                    mode='lines'
                ))

        fig.update_layout(
            template="plotly_dark",
            height=600,
            xaxis_title="Date",
            yaxis_title="Price (ZAR)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        st.subheader("Portfolio Analysis")
        monthly_investment = st.number_input(
            "Monthly Investment per Stock (ZAR)",
            min_value=100,
            value=100,
            step=100
        )

        # Calculate total portfolio value and returns
        total_portfolio_value = 0
        total_investment = 0

        # Individual stock analysis
        for symbol in selected_stocks:
            st.write(f"### {JSE_TOP_50[symbol]['name']} ({symbol})")
            hist, _ = get_stock_data(symbol)
            if hist is not None:
                portfolio_value = calculate_portfolio_value(hist, monthly_investment)
                returns = calculate_returns(portfolio_value)

                # Add to portfolio totals
                total_portfolio_value += portfolio_value.iloc[-1]
                total_investment += len(portfolio_value) * monthly_investment

                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "Investment Value",
                        f"R{portfolio_value.iloc[-1]:,.2f}",
                        f"{returns:.1f}%"
                    )
                with col2:
                    st.metric(
                        "Total Returns",
                        f"R{(portfolio_value.iloc[-1] - len(portfolio_value)*monthly_investment):,.2f}"
                    )

        # Display portfolio totals
        st.write("### Total Portfolio Performance")
        total_returns = total_portfolio_value - total_investment
        total_return_percentage = (total_returns / total_investment * 100) if total_investment > 0 else 0

        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Total Portfolio Value",
                f"R{total_portfolio_value:,.2f}",
                f"{total_return_percentage:.1f}%"
            )
        with col2:
            st.metric(
                "Total Returns",
                f"R{total_returns:,.2f}"
            )

    with tabs[2]:
        st.subheader("Stock Price Forecasting")
        forecast_months = st.slider("Forecast Months", 3, 18, 6, 
            help="Select forecast horizon between 3 and 18 months")

        monthly_investment = st.number_input(
            "Monthly Investment Amount (ZAR)",
            min_value=100,
            value=100,
            step=100,
            help="Amount to invest monthly during the forecast period"
        )

        # Track total forecasted portfolio metrics
        total_forecast_investment = 0
        total_forecast_return = 0
        total_forecast_value = 0

        for symbol in selected_stocks:
            st.write(f"### {JSE_TOP_50[symbol]['name']} ({symbol})")
            hist, info = get_stock_data(symbol)
            if hist is not None:
                with st.spinner(f'Generating {forecast_months}-month forecast for {symbol}...'):
                    # Generate forecast with confidence intervals
                    median_forecast, lower_bound, upper_bound = create_forecast(hist, forecast_months)

                    # Calculate forecast returns using median forecast
                    investment, returns, return_percentage = calculate_forecast_returns(
                        median_forecast, monthly_investment
                    )

                    # Update portfolio totals
                    total_forecast_investment += investment
                    total_forecast_return += returns
                    total_forecast_value += (investment + returns)

                    # Generate recommendation
                    recommendation, reasons = generate_stock_recommendation(
                        info, return_percentage
                    )

                    # Display metrics in columns
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Median Forecast Price",
                            f"R{median_forecast.iloc[-1]:.2f}",
                            f"{((median_forecast.iloc[-1] - hist['Close'].iloc[-1]) / hist['Close'].iloc[-1] * 100):+.1f}%"
                        )

                    with col2:
                        st.metric(
                            "Potential Return",
                            f"R{returns:,.2f}",
                            f"{return_percentage:+.1f}%"
                        )

                    with col3:
                        forecast_range = f"R{lower_bound.iloc[-1]:.2f} - R{upper_bound.iloc[-1]:.2f}"
                        st.metric(
                            "95% Confidence Range",
                            forecast_range
                        )

                    # Display recommendation
                    st.subheader("Investment Recommendation")
                    st.write(f"**{recommendation}**")
                    if reasons:
                        st.write("Based on:")
                        for reason in reasons:
                            st.write(f"• {reason}")

                    # Forecast chart
                    fig = go.Figure()

                    # Historical data
                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=hist['Close'],
                        name='Historical',
                        mode='lines'
                    ))

                    # Median forecast
                    fig.add_trace(go.Scatter(
                        x=median_forecast.index,
                        y=median_forecast,
                        name='Median Forecast',
                        mode='lines',
                        line=dict(dash='dash', color='yellow')
                    ))

                    # Confidence intervals
                    fig.add_trace(go.Scatter(
                        x=upper_bound.index,
                        y=upper_bound,
                        name='Upper Bound (97.5%)',
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False
                    ))
                    fig.add_trace(go.Scatter(
                        x=lower_bound.index,
                        y=lower_bound,
                        name='Lower Bound (2.5%)',
                        mode='lines',
                        line=dict(width=0),
                        fill='tonexty',
                        fillcolor='rgba(255,255,255,0.1)',
                        showlegend=False
                    ))

                    fig.update_layout(
                        template="plotly_dark",
                        height=400,
                        xaxis_title="Date",
                        yaxis_title="Price (ZAR)",
                        hovermode='x unified',
                        showlegend=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"Unable to fetch data for {symbol}")

        # Display total portfolio forecast metrics
        st.write("### Total Portfolio Forecast")
        total_forecast_return_percentage = (total_forecast_return / total_forecast_investment * 100) if total_forecast_investment > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Total Forecasted Value",
                f"R{total_forecast_value:,.2f}",
                f"{total_forecast_return_percentage:+.1f}%"
            )
        with col2:
            st.metric(
                "Total Potential Return",
                f"R{total_forecast_return:,.2f}"
            )
        with col3:
            st.metric(
                "Total Investment Required",
                f"R{total_forecast_investment:,.2f}"
            )

# Footer
st.markdown("---")
st.markdown("*Disclaimer: This tool is for educational purposes only. Historical performance does not guarantee future results.*")