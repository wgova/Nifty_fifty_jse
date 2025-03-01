import streamlit as st

def render_insights_page():
    st.title("🎯 Advanced Investment Insights")
    st.markdown("""
    Beyond the numbers, successful investing requires understanding the qualitative aspects 
    of a business. Here's your guide to deeper analysis.
    """)

    # Management Assessment
    st.header("👥 Management Assessment Framework")
    with st.expander("How to Evaluate Management"):
        st.markdown("""
        **1. Track Record**
        - ✅ Consistent delivery on promises
        - ✅ History of capital allocation decisions
        - ❌ Watch out for frequent strategy changes

        **2. Communication Style**
        - ✅ Clear and transparent communication
        - ✅ Willingness to admit mistakes
        - ❌ Beware of overly promotional language

        **3. Alignment with Shareholders**
        - 👀 Review insider ownership trends
        - 💰 Executive compensation structure
        - 🎯 Long-term incentive metrics
        """)

    # Investment Checklist
    st.header("✅ The Smart Investor's Checklist")
    with st.expander("Pre-Investment Checklist"):
        st.markdown("""
        **Before You Invest:**

        1. **Business Understanding**
           - Can you explain the business model to a 10-year-old?
           - What's their competitive advantage?
           - How do they make money?

        2. **Industry Position**
           - Market share trends
           - Barriers to entry
           - Regulatory environment

        3. **Financial Health**
           - Debt levels vs. industry average
           - Working capital trends
           - Cash flow quality

        4. **Growth Prospects**
           - Organic growth opportunities
           - Market expansion potential
           - Innovation pipeline

        Remember Warren's Words: *"Risk comes from not knowing what you're doing"*
        """)

    # Warning Note
    st.markdown("""
    ---
    *Disclaimer: This guide is for educational purposes only. Always do your own research 
    and consider consulting with a financial advisor before making investment decisions.*
    """)

if __name__ == "__main__":
    render_insights_page()