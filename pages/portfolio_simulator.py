import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
from utils.stock_data import JSE_TOP_50, get_stock_data, get_financial_metrics
from utils.forecasting import create_forecast, calculate_forecast_returns
from utils.analysis import calculate_portfolio_value

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

    # Add stock to portfolio
    with st.expander("➕ Add Stock to Portfolio"):
        col1, col2, col3 = st.columns(3)
        
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
            
        if st.button("Add to Portfolio"):
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
        
        st.markdown(f"**Total Portfolio Value: R{total_value:,.2f}**")
        st.dataframe(
            portfolio_df[['symbol', 'name', 'shares', 'purchase_date', 'purchase_price', 
                         'current_price', 'total_return', 'current_value']],
            hide_index=True
        )
        
        if st.button("Clear Portfolio"):
            st.session_state.portfolio = []
            st.rerun()

    # Opportunity Analysis Section
    st.header("🎯 Opportunity Analysis")
    
    potential_stock = st.selectbox(
        "Select Stock to Analyze",
        options=[s for s in JSE_TOP_50.keys() if s not in [p['symbol'] for p in st.session_state.portfolio]],
        format_func=lambda x: f"{x} - {JSE_TOP_50[x]['name']}"
    )
    
    potential_investment = st.number_input(
        "Investment Amount (R)",
        min_value=1000,
        value=10000,
        step=1000,
        help="How much would you like to invest?"
    )

    if potential_stock:
        hist, info = get_stock_data(potential_stock)
        if hist is not None and not hist.empty:
            # Calculate historical returns
            start_price = hist['Close'].iloc[0]
            current_price = hist['Close'].iloc[-1]
            shares_possible = potential_investment / start_price
            potential_value = shares_possible * current_price
            opportunity_cost = potential_value - potential_investment
            
            # Generate forecast
            forecast, lower_bound, upper_bound = create_forecast(hist)
            _, forecast_return, return_percentage = calculate_forecast_returns(forecast)
            
            # Display Results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Historical Performance")
                st.metric(
                    "Potential Value Today",
                    f"R{potential_value:,.2f}",
                    f"R{opportunity_cost:,.2f}",
                    help="How much your investment would be worth today"
                )
                st.metric(
                    "Return on Investment",
                    f"{((potential_value - potential_investment) / potential_investment * 100):,.1f}%"
                )
                
            with col2:
                st.subheader("Forecasted Returns")
                st.metric(
                    "Projected Value (6 months)",
                    f"R{(potential_value + forecast_return):,.2f}",
                    f"{return_percentage:,.1f}%"
                )
                st.markdown(f"""
                    **Forecast Range:**
                    - Optimistic: R{(potential_value * (1 + upper_bound.iloc[-1]/100)):,.2f}
                    - Conservative: R{(potential_value * (1 + lower_bound.iloc[-1]/100)):,.2f}
                """)

if __name__ == "__main__":
    render_portfolio_simulator()
