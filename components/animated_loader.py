import streamlit as st
import time

def show_stock_loader(message="Loading data..."):
    """
    Display an animated loader with a stock market theme.
    
    Args:
        message (str): Custom message to display with the loader
        
    Returns:
        st.empty: Placeholder container that can be cleared when loading is complete
    """
    # Create a placeholder for the loader
    placeholder = st.empty()
    
    # CSS for the animated loader
    loader_css = """
    <style>
    .stock-loader {
        text-align: center;
        padding: 20px;
        background: #1E1E1E;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .loader-title {
        color: #00FF00;
        font-size: 1.2em;
        margin-bottom: 10px;
        font-family: monospace;
    }
    
    .candlestick {
        display: inline-block;
        width: 10px;
        height: 40px;
        background: #00FF00;
        margin: 0 5px;
        animation: candlestick-animation 1.2s infinite;
    }
    
    .candlestick:nth-child(2) { animation-delay: 0.2s; }
    .candlestick:nth-child(3) { animation-delay: 0.4s; }
    .candlestick:nth-child(4) { animation-delay: 0.6s; }
    
    @keyframes candlestick-animation {
        0% {
            transform: scaleY(0.5);
            background: #FF4444;
        }
        50% {
            transform: scaleY(1.2);
            background: #00FF00;
        }
        100% {
            transform: scaleY(0.5);
            background: #FF4444;
        }
    }
    </style>
    """
    
    # HTML for the loader
    loader_html = f"""
    <div class="stock-loader">
        <div class="loader-title">{message}</div>
        <div class="candlestick"></div>
        <div class="candlestick"></div>
        <div class="candlestick"></div>
        <div class="candlestick"></div>
    </div>
    """
    
    # Display the loader
    placeholder.markdown(loader_css + loader_html, unsafe_allow_html=True)
    
    return placeholder

def demo_loader():
    """
    Demonstrate the animated loader functionality.
    """
    st.title("Stock Market Loader Demo")
    
    if st.button("Show Loading Animation"):
        loader = show_stock_loader("Fetching market data...")
        time.sleep(3)  # Simulate loading
        loader.empty()
        st.success("Data loaded successfully!")

if __name__ == "__main__":
    demo_loader()
