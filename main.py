import sys
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    import streamlit as st
    logger.info("Streamlit import successful")

    # Basic page config
    st.set_page_config(
        page_title="JSE Stock Analysis",
        page_icon="📈",
        layout="wide"
    )
    logger.info("Page config set")

    # Simple title
    st.title("📈 JSE Stock Analysis Tool")
    st.markdown("Test version - Basic functionality check")

except Exception as e:
    logger.error(f"Error in app execution: {str(e)}", exc_info=True)
    sys.exit(1)