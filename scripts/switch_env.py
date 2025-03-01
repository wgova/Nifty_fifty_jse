#!/usr/bin/env python3
import os
import shutil
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def switch_environment(env):
    """Switch between development and production configurations"""
    streamlit_dir = ".streamlit"
    config_prod = os.path.join(streamlit_dir, "config.prod.toml")
    config_dev = os.path.join(streamlit_dir, "config.toml")
    
    try:
        if env == "prod":
            if os.path.exists(config_prod):
                shutil.copy2(config_prod, config_dev)
                logger.info("Switched to production configuration (port 8501)")
            else:
                logger.error("Production config file not found")
                return False
        elif env == "dev":
            # Ensure development config exists with port 5000
            dev_content = """[server]
headless = true
address = "0.0.0.0"
port = 5000
enableCORS = false
enableXsrfProtection = false

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FFFFFF"
font = "sans serif"
"""
            with open(config_dev, 'w') as f:
                f.write(dev_content)
            logger.info("Switched to development configuration (port 5000)")
        return True
    except Exception as e:
        logger.error(f"Error switching environment: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Switch between development and production environments")
    parser.add_argument("environment", choices=["dev", "prod"], help="Target environment")
    args = parser.parse_args()
    
    if switch_environment(args.environment):
        print(f"Successfully switched to {args.environment} environment")
    else:
        print("Failed to switch environment")
        exit(1)
