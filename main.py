import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.stock_data import JSE_TOP_50, get_stock_data, get_financial_metrics
from utils.analysis import calculate_portfolio_value, calculate_returns, get_summary_statistics
from utils.forecasting import (
    create_forecast, calculate_confidence_intervals,
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
st.sidebar.header("Stock Selection")
selected_stocks = st.sidebar.multiselect(
    "Select up to 3 stocks",
    options=list(JSE_TOP_50.keys()),
    default=[list(JSE_TOP_50.keys())[0]],
    max_selections=3,
    format_func=lambda x: f"{x} - {JSE_TOP_50[x]}"
)

# Main content
if not selected_stocks:
    st.warning("Please select at least one stock to analyze.")
else:
    # Create tabs
    tabs = st.tabs(["📊 Overview", "💰 Portfolio Analysis", "🔮 Forecasting"])

    with tabs[0]:
        # Financial metrics table
        st.subheader("Financial Metrics")
        metrics_data = {}
        for symbol in selected_stocks:
            metrics = get_financial_metrics(symbol)
            # Format numeric values
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
            metrics_data[symbol] = formatted_metrics

        # Display metrics without background gradient
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
                    name=f"{symbol} - {JSE_TOP_50[symbol]}",
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

        for symbol in selected_stocks:
            st.write(f"### {JSE_TOP_50[symbol]} ({symbol})")
            hist, _ = get_stock_data(symbol)
            if hist is not None:
                portfolio_value = calculate_portfolio_value(hist, monthly_investment)
                returns = calculate_returns(portfolio_value)

                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "Total Investment",
                        f"R{portfolio_value.iloc[-1]:,.2f}",
                        f"{returns:.1f}%"
                    )
                with col2:
                    st.metric(
                        "Total Returns",
                        f"R{(portfolio_value.iloc[-1] - len(portfolio_value)*monthly_investment):,.2f}"
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

        for symbol in selected_stocks:
            st.write(f"### {JSE_TOP_50[symbol]} ({symbol})")
            hist, info = get_stock_data(symbol)
            if hist is not None:
                with st.spinner(f'Generating {forecast_months}-month forecast for {symbol}...'):
                    # Generate forecast
                    forecast = create_forecast(hist, forecast_months)
                    upper, lower = calculate_confidence_intervals(forecast)

                    # Calculate forecast returns
                    total_investment, total_return, return_percentage = calculate_forecast_returns(
                        forecast, monthly_investment
                    )

                    # Generate recommendation
                    recommendation, reasons = generate_stock_recommendation(
                        info, return_percentage
                    )

                    # Display metrics in columns
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Forecasted End Price",
                            f"R{forecast.iloc[-1]:.2f}",
                            f"{((forecast.iloc[-1] - hist['Close'].iloc[-1]) / hist['Close'].iloc[-1] * 100):+.1f}%"
                        )

                    with col2:
                        st.metric(
                            "Potential Return",
                            f"R{total_return:,.2f}",
                            f"{return_percentage:+.1f}%"
                        )

                    with col3:
                        st.metric(
                            "Total Investment",
                            f"R{total_investment:,.2f}"
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

                    # Forecast
                    fig.add_trace(go.Scatter(
                        x=forecast.index,
                        y=forecast,
                        name='Forecast',
                        mode='lines',
                        line=dict(dash='dash')
                    ))

                    # Confidence intervals
                    fig.add_trace(go.Scatter(
                        x=forecast.index.tolist() + forecast.index.tolist()[::-1],
                        y=upper.tolist() + lower.tolist()[::-1],
                        fill='toself',
                        fillcolor='rgba(255,255,255,0.1)',
                        line=dict(color='rgba(255,255,255,0)'),
                        name='Confidence Interval'
                    ))

                    fig.update_layout(
                        template="plotly_dark",
                        height=400,
                        xaxis_title="Date",
                        yaxis_title="Price (ZAR)",
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"Unable to fetch data for {symbol}")

# Footer
st.markdown("---")
st.markdown("*Disclaimer: This tool is for educational purposes only. Historical performance does not guarantee future results.*")