import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.stock_data import (
    JSE_TOP_50, get_stock_data, get_financial_metrics,
    get_available_sectors, get_stocks_by_sector
)
from utils.analysis import prepare_chart_data

def render_comparison_page():
    st.title("📊 Stock Comparison Lab")
    st.markdown("""
    Compare key metrics and performance across multiple JSE stocks.
    Select up to 4 stocks to analyze their relative performance.
    """)

    # Stock selection
    selected_stocks = st.multiselect(
        "Select stocks to compare (max 4)",
        options=list(JSE_TOP_50.keys()),
        max_selections=4,
        format_func=lambda x: f"{x} - {JSE_TOP_50[x]['name']} ({JSE_TOP_50[x]['sector']})"
    )

    if len(selected_stocks) > 1:
        # Create comparison table
        comparison_data = []
        for symbol in selected_stocks:
            try:
                hist, info = get_stock_data(symbol)
                metrics = get_financial_metrics(symbol)
                
                stock_data = {
                    'Symbol': symbol,
                    'Name': JSE_TOP_50[symbol]['name'],
                    'Sector': JSE_TOP_50[symbol]['sector'],
                    'Current Price': f"R{hist['Close'].iloc[-1]:.2f}",
                    'Market Cap': f"R{metrics['Market Cap']/1e9:.2f}B" if isinstance(metrics['Market Cap'], (int, float)) else "N/A",
                    'P/E Ratio': f"{metrics['P/E Ratio']:.2f}" if isinstance(metrics['P/E Ratio'], (int, float)) else "N/A",
                    'Dividend Yield': f"{metrics['Dividend Yield']*100:.2f}%" if isinstance(metrics['Dividend Yield'], (int, float)) else "N/A",
                    'Beta': f"{metrics['Beta']:.2f}" if isinstance(metrics['Beta'], (int, float)) else "N/A"
                }
                comparison_data.append(stock_data)
            except Exception as e:
                st.error(f"Error loading data for {symbol}: {str(e)}")
                continue

        if comparison_data:
            # Display comparison table
            df = pd.DataFrame(comparison_data)
            st.dataframe(
                df.set_index('Symbol'),
                use_container_width=True,
                height=400
            )

            # Create price performance comparison chart
            st.subheader("📈 Price Performance Comparison")
            fig, ax = plt.subplots(figsize=(12, 6))
            
            for symbol in selected_stocks:
                hist, _ = get_stock_data(symbol)
                if hist is not None and not hist.empty:
                    # Normalize prices to 100 for comparison
                    normalized_price = hist['Close'] / hist['Close'].iloc[0] * 100
                    ax.plot(hist.index, normalized_price, label=f"{JSE_TOP_50[symbol]['name']}")

            ax.set_xlabel('Date')
            ax.set_ylabel('Normalized Price (Base 100)')
            ax.grid(True, alpha=0.2)
            ax.legend()
            plt.title("Relative Price Performance")
            st.pyplot(fig)
            plt.close()

    else:
        st.info("Please select at least 2 stocks to compare")

if __name__ == "__main__":
    render_comparison_page()
