import sys
import logging
import os

# Configure logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Starting Streamlit App...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")

try:
    logger.info("Importing streamlit...")
    import streamlit as st
    logger.info("Streamlit import successful")

    logger.info("Setting up Streamlit page config...")
    st.set_page_config(
        page_title="JSE Stock Analysis",
        page_icon="📈",
        layout="wide"
    )
    logger.info("Page config set")

    # Basic content
    st.title("📈 JSE Stock Analysis Tool")
    st.write("Basic test version")
    st.write("If you can see this message, the Streamlit server is working correctly.")

except Exception as e:
    logger.error(f"Error in app execution: {str(e)}", exc_info=True)
    sys.exit(1)