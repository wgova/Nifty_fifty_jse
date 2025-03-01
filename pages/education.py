import streamlit as st

def render_education_page():
    st.title("🎓 Buffett Notes: Understanding Stock Metrics")
    st.markdown("""
    Let Warren guide you through the world of stock analysis with these nuggets of wisdom.
    Remember, the market is there to serve you, not to instruct you!
    """)

    # Price and Market Metrics
    st.header("📊 Price & Market Metrics")
    with st.expander("Market Capitalization"):
        st.markdown("""
        **What it is:** Total value of all shares = Share Price × Number of Shares

        **Buffett's Take:** "Size matters - but only when combined with quality. A big company selling at R1 might be worth less than a small one at R100."
        """)

    with st.expander("P/E Ratio (Price to Earnings)"):
        st.markdown("""
        **What it is:** Share Price ÷ Earnings Per Share

        **Buffett's Take:** "The higher the P/E, the more faith you need. And I'm a believer in numbers, not fairy tales."

        - Below 15: Might be undervalued
        - 15-25: Fairly valued
        - Above 25: Better have a good growth story!
        """)

    with st.expander("Price/Book Ratio"):
        st.markdown("""
        **What it is:** Share Price ÷ Book Value Per Share

        **Buffett's Take:** "Buy companies for less than they're worth. But remember, some assets are worth more than the books show, and some aren't worth the paper they're printed on."
        """)

    # Market Sentiment
    st.header("🎭 Market Sentiment")
    with st.expander("Bullish vs Bearish"):
        st.markdown("""
        **Bullish Indicators** 👍
        - Rising prices and increasing volume
        - Strong earnings growth
        - Positive industry trends
        - High institutional buying
        - Growing market share

        **What it means:** Investors expect prices to rise. Like a bull attacking upward with its horns!

        **Bearish Indicators** 👎
        - Falling prices with high volume
        - Declining earnings
        - Industry headwinds
        - Institutional selling
        - Loss of market share

        **What it means:** Investors expect prices to fall. Like a bear swiping downward with its paw!

        **Neutral Stance** 😐
        - Sideways price movement
        - Mixed signals
        - Unclear market direction

        **Buffett's Take:** "Be fearful when others are greedy, and greedy when others are fearful. But always do your homework before taking a stance!"
        """)

    # Dividend Metrics
    st.header("💰 Dividend Metrics")
    with st.expander("Dividend Yield"):
        st.markdown("""
        **What it is:** Annual Dividend ÷ Share Price × 100

        **Buffett's Take:** "If you need the dividend to live on, you probably shouldn't own stocks. But if a company can grow AND pay dividends, now that's interesting."

        - Below 2%: Growth focused
        - 2-6%: Balanced
        - Above 6%: High yield (but check if it's sustainable!)
        """)

    with st.expander("Dividend Growth"):
        st.markdown("""
        **What it is:** % Change in Dividend from Previous Period

        **Buffett's Take:** "A rising dividend is often a sign of a healthy business. But remember, dividends come from earnings, and earnings come from good business."
        """)

    # Risk Metrics
    st.header("⚖️ Risk Metrics")
    with st.expander("Beta"):
        st.markdown("""
        **What it is:** Stock's volatility compared to the market

        **Buffett's Take:** "If you understand the business, volatility is your friend. Beta is Wall Street's way of measuring risk, but they're looking at the wrong thing."

        - Below 1: Less volatile than market
        - 1: Moves with market
        - Above 1: More volatile than market
        """)

    with st.expander("ROE (Return on Equity)"):
        st.markdown("""
        **What it is:** Net Income ÷ Shareholder Equity × 100

        **Buffett's Take:** "Find businesses that can employ large amounts of capital at high rates of return. That's the golden ticket."

        - Below 10%: Might need improvement
        - 10-20%: Solid performance
        - Above 20%: Exceptional (but verify sustainability)
        """)

    # Final Words
    st.markdown("""
    ---
    Remember Buffett's Golden Rules:
    1. Never lose money
    2. Never forget rule #1
    3. Be fearful when others are greedy, and greedy when others are fearful

    *Disclaimer: These notes are for educational purposes only. Warren Buffett probably has more zeros in his bank account than you have fingers to count them.*
    """)

if __name__ == "__main__":
    render_education_page()