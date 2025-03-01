# JSE Top 50 Stock Analysis Tool 📈

A comprehensive Streamlit-based stock analysis application focused on JSE Top 50 stocks, providing advanced financial insights and portfolio simulation capabilities.

## Features

- Real-time stock data fetching from Yahoo Finance
- Interactive historical price trend visualization
- Portfolio value estimation and forecasting
- Advanced financial metrics and indicators analysis
- Responsive dark mode UI optimized for mobile use

## Technologies

- Python 3.11
- Streamlit framework
- Plotly for data visualization
- yfinance for stock data retrieval
- scikit-learn for predictive modeling

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Development vs Production

This project uses different configurations for development and production environments:

- Development (port 5000): Used for local development and testing
- Production (port 8501): Used for deployment on Streamlit Community Cloud

To switch between environments, use the provided script:

```bash
# Switch to development environment
python scripts/switch_env.py dev

# Switch to production environment
python scripts/switch_env.py prod
```

## Running the Application

```bash
streamlit run main.py
```

## Development Workflow

### Branch Strategy

1. `main` - Production branch
   - Protected branch
   - Requires pull request approval
   - Must pass all tests
   - Deployed to production after approval

2. `dev` - Development branch
   - Protected branch
   - Requires pull request approval
   - Must pass all tests
   - Used for ongoing development

3. `test` - Testing branch
   - Intermediate branch for testing
   - Automated tests run on every push
   - Used to verify changes before merging to dev/main

### Making Changes

1. Create a feature branch from `dev`
2. Make your changes and commit
3. Create a pull request to `test`
4. After tests pass, merge to `dev`
5. For releases, create a pull request from `dev` to `main`

## Usage

1. Select up to 15 stocks from the sidebar
2. View financial metrics and historical trends in the Overview tab
3. Analyze portfolio performance with custom monthly investment amounts
4. Explore price forecasts with confidence intervals

## Disclaimer

This tool is for educational purposes only. Historical performance does not guarantee future results.