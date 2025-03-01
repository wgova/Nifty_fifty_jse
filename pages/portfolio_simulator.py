import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import plotly.graph_objects as go
from utils.stock_data import JSE_TOP_50, get_stock_data, get_financial_metrics
from utils.ml_models import generate_ml_forecast
from utils.analysis import calculate_portfolio_value

def create_forecast_chart(hist, forecast, lower_bound, upper_bound, stock_name, ml_forecast=None, ml_lower=None, ml_upper=None):
    """Create forecast chart using plotly"""
    fig = go.Figure()

    # Historical prices
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist['Close'],
        name='Historical',
        line=dict(color='blue')
    ))

    # Statistical forecast
    fig.add_trace(go.Scatter(
        x=forecast.index,
        y=forecast,
        name='Statistical Forecast',
        line=dict(color='red', dash='dash')
    ))

    # Statistical confidence interval
    fig.add_trace(go.Scatter(
        x=upper_bound.index,
        y=upper_bound,
        name='Statistical Upper Bound',
        line=dict(color='rgba(255,0,0,0.2)'),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=lower_bound.index,
        y=lower_bound,
        name='Statistical Lower Bound',
        line=dict(color='rgba(255,0,0,0.2)'),
        fill='tonexty',
        showlegend=False
    ))

    # ML forecast if available
    if ml_forecast is not None:
        fig.add_trace(go.Scatter(
            x=ml_forecast.index,
            y=ml_forecast,
            name='ML Forecast',
            line=dict(color='green', dash='dash')
        ))

        # ML confidence interval
        fig.add_trace(go.Scatter(
            x=ml_upper.index,
            y=ml_upper,
            name='ML Upper Bound',
            line=dict(color='rgba(0,255,0,0.2)'),
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x=ml_lower.index,
            y=ml_lower,
            name='ML Lower Bound',
            line=dict(color='rgba(0,255,0,0.2)'),
            fill='tonexty',
            showlegend=False
        ))

    fig.update_layout(
        title=f"{stock_name} - Price Forecast",
        xaxis_title="Date",
        yaxis_title="Price (R)",
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    return fig

def render_portfolio_simulator():
    st.title("💼 Portfolio Opportunity Explorer")
    st.markdown("""
    Compare your current portfolio against potential investments.
    See how different investment choices could have performed.
    """)

    # Portfolio Input Section
    st.header("📊 Your Current Portfolio")

    # Initialize session state for portfolio
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []

    # Add stock to portfolio using columns
    st.subheader("➕ Add Stock to Portfolio")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        stock = st.selectbox(
            "Select Stock",
            options=list(JSE_TOP_50.keys()),
            format_func=lambda x: f"{x} - {JSE_TOP_50[x]['name']}"
        )

    with col2:
        years_ago = st.number_input(
            "Years Held",
            min_value=1,
            max_value=10,
            value=1,
            help="How many years ago did you buy this stock?"
        )

    with col3:
        shares = st.number_input(
            "Number of Shares",
            min_value=1,
            value=100,
            help="How many shares do you own?"
        )

    with col4:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("Add to Portfolio", use_container_width=True):
            purchase_date = datetime.now(pytz.UTC) - timedelta(days=365 * years_ago)

            # Get stock data and calculate returns
            hist, info = get_stock_data(stock)
            if hist is not None and not hist.empty:
                purchase_price = hist['Close'].iloc[0]  # First available price
                current_price = hist['Close'].iloc[-1]  # Latest price
                total_return = ((current_price - purchase_price) / purchase_price) * 100

                portfolio_item = {
                    'symbol': stock,
                    'name': JSE_TOP_50[stock]['name'],
                    'shares': shares,
                    'purchase_date': purchase_date.strftime('%Y-%m-%d'),
                    'purchase_price': purchase_price,
                    'current_price': current_price,
                    'total_return': total_return,
                    'current_value': current_price * shares
                }

                st.session_state.portfolio.append(portfolio_item)
                st.success(f"Added {JSE_TOP_50[stock]['name']} to portfolio")

    # Display Current Portfolio
    if st.session_state.portfolio:
        portfolio_df = pd.DataFrame(st.session_state.portfolio)
        total_value = portfolio_df['current_value'].sum()

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Total Portfolio Value: R{total_value:,.2f}**")
        with col2:
            if st.button("Clear Portfolio", use_container_width=True):
                st.session_state.portfolio = []
                st.rerun()

        st.dataframe(
            portfolio_df[['symbol', 'name', 'shares', 'purchase_date', 'purchase_price', 
                         'current_price', 'total_return', 'current_value']],
            hide_index=True
        )

        # Portfolio Forecast Section
        st.header("📈 Portfolio Forecast")
        forecast_months = st.slider(
            "Forecast Horizon (months)",
            min_value=1,
            max_value=12,
            value=6,
            help="How many months ahead to forecast?"
        )

        use_ml = st.checkbox(
            "Use Machine Learning Forecast",
            value=True,
            help="Enable advanced ML-based predictions alongside statistical forecasts"
        )

        # Create forecasts for portfolio stocks
        for idx, stock_data in portfolio_df.iterrows():
            st.subheader(f"🎯 {stock_data['name']} ({stock_data['symbol']})")

            hist, info = get_stock_data(stock_data['symbol'])
            if hist is not None and not hist.empty:
                # Statistical forecast
                forecast, lower_bound, upper_bound = create_forecast(hist, months_ahead=forecast_months)
                _, forecast_return, return_percentage = calculate_forecast_returns(forecast)

                # ML forecast
                ml_forecast, ml_lower, ml_upper = generate_ml_forecast(hist, months_ahead=forecast_months) if use_ml else (None, None, None)

                # Calculate projected values
                current_value = stock_data['current_value']
                stat_projected_value = current_value * (1 + return_percentage/100)

                ml_return_percentage = None
                if ml_forecast is not None and not ml_forecast.empty:
                    ml_return = ((ml_forecast.iloc[-1] - hist['Close'].iloc[-1]) / hist['Close'].iloc[-1]) * 100
                    ml_projected_value = current_value * (1 + ml_return/100)

                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Current Position",
                        f"R{current_value:,.2f}",
                        f"{stock_data['total_return']:,.1f}%"
                    )
                with col2:
                    st.metric(
                        f"Statistical Forecast ({forecast_months} months)",
                        f"R{stat_projected_value:,.2f}",
                        f"{return_percentage:,.1f}%"
                    )
                if use_ml and ml_forecast is not None:
                    with col3:
                        st.metric(
                            f"ML Forecast ({forecast_months} months)",
                            f"R{ml_projected_value:,.2f}",
                            f"{ml_return:,.1f}%"
                        )

                # Display forecast chart
                fig = create_forecast_chart(
                    hist, forecast, lower_bound, upper_bound, 
                    stock_data['name'],
                    ml_forecast if use_ml else None,
                    ml_lower if use_ml else None,
                    ml_upper if use_ml else None
                )
                st.plotly_chart(fig, use_container_width=True)

    # Opportunity Analysis Section
    st.header("🎯 New Investment Opportunities")

    col1, col2, col3 = st.columns(3)

    with col1:
        potential_stock = st.selectbox(
            "Select Stock to Analyze",
            options=[s for s in JSE_TOP_50.keys() if s not in [p['symbol'] for p in st.session_state.portfolio]],
            format_func=lambda x: f"{x} - {JSE_TOP_50[x]['name']}"
        )

    with col2:
        potential_investment = st.number_input(
            "Investment Amount (R)",
            min_value=1000,
            value=10000,
            step=1000,
            help="How much would you like to invest?"
        )

    with col3:
        new_forecast_months = st.slider(
            "Forecast Horizon (months)",
            min_value=1,
            max_value=12,
            value=forecast_months if 'forecast_months' in locals() else 6,
            help="How many months ahead to forecast?",
            key="new_forecast_months"
        )

    if potential_stock:
        hist, info = get_stock_data(potential_stock)
        if hist is not None and not hist.empty:
            # Calculate historical returns
            start_price = hist['Close'].iloc[0]
            current_price = hist['Close'].iloc[-1]
            shares_possible = potential_investment / current_price
            potential_value = shares_possible * current_price

            # Generate forecasts
            forecast, lower_bound, upper_bound = create_forecast(hist, months_ahead=new_forecast_months)
            _, forecast_return, return_percentage = calculate_forecast_returns(forecast)

            # Generate ML forecast if enabled
            if use_ml:
                ml_forecast, ml_lower, ml_upper = generate_ml_forecast(hist, months_ahead=new_forecast_months)
                if not ml_forecast.empty:
                    ml_return = ((ml_forecast.iloc[-1] - current_price) / current_price) * 100
                    ml_projected_value = potential_value * (1 + ml_return/100)

            # Display Results in Columns
            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader("Historical Performance")
                st.metric(
                    "Shares You Could Buy",
                    f"{shares_possible:.0f}",
                    help="Number of shares possible with your investment"
                )
                st.metric(
                    "Initial Investment",
                    f"R{potential_investment:,.2f}"
                )

            with col2:
                st.subheader("Statistical Forecast")
                stat_projected_value = potential_value * (1 + return_percentage/100)
                st.metric(
                    f"Projected Value ({new_forecast_months} months)",
                    f"R{stat_projected_value:,.2f}",
                    f"{return_percentage:,.1f}%"
                )

            if use_ml and 'ml_forecast' in locals() and not ml_forecast.empty:
                with col3:
                    st.subheader("ML Forecast")
                    st.metric(
                        f"ML Projected Value ({new_forecast_months} months)",
                        f"R{ml_projected_value:,.2f}",
                        f"{ml_return:,.1f}%"
                    )

            # Display forecast chart
            fig = create_forecast_chart(
                hist, forecast, lower_bound, upper_bound,
                JSE_TOP_50[potential_stock]['name'],
                ml_forecast if use_ml else None,
                ml_lower if use_ml else None,
                ml_upper if use_ml else None
            )
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    render_portfolio_simulator()