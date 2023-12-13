import streamlit as st
import yfinance as yf
import requests

# Function definitions
def pv(fv, requiredRateOfReturn, years):
    return fv / ((1 + requiredRateOfReturn / 100) ** years)

def fv(pv, growth, years):
    return pv * (1 + growth) ** years

# Initial UI
ticker = st.text_input('Ticker', "AAPL").upper()
buttonClicked = st.button('Set')

# Callbacks
if buttonClicked:
    try:
        # Get the data using yfinance
        stock = yf.Ticker(ticker)
        info = stock.info
        if 'currentPrice' not in info or info['currentPrice'] is None:
            st.error(f"Current price data is not available for {ticker}. Please try a different ticker.")
        else:
            st.session_state.data = info
    except requests.exceptions.ConnectionError:
        st.error("Failed to connect to the data source. Please check your internet connection.")
    except Exception as e:
        st.error(f"An error occurred while fetching data for {ticker}: {e}")

if 'data' in st.session_state:
    data = st.session_state.data

    # Print company profile
    st.header("Company Profile")
    st.metric("Sector", data.get("sector", "N/A"))
    st.metric("Industry", data.get("industry", "N/A"))
    st.metric("Website", data.get("website", "N/A"))
    st.metric("Market Cap", f"{data.get('marketCap', 'N/A'):,}")

    with st.expander("About Company"):
        st.write(data.get("longBusinessSummary", "N/A"))

    # Valuation
    st.header("Valuation")
    currentPrice = data.get("currentPrice", 0)
    growth = 10  # Placeholder, adjust as needed
    peFWD = data.get("forwardPE", 0)
    epsFWD = data.get("trailingEps", 0)
    requiredRateOfReturn = 10.0
    yearsToProject = 5

    # Print the metrics
    st.metric("Current Price", f"{currentPrice:.2f}")
    st.metric("Estimated Growth", f"{growth:.2f}%")
    st.metric("Forward P/E", f"{peFWD:.2f}")
    st.metric("Forward EPS", f"{epsFWD:.2f}")
    st.metric("Required Rate Of Return", f"{requiredRateOfReturn}%")
    st.metric("Years to Project", yearsToProject)

    # Get user inputs for future projections
    growth = st.number_input("Annual Growth Rate (%)", min_value=0.0, max_value=100.0, step=0.5, value=10.0)
    peFWD = st.number_input("Future P/E Ratio", min_value=0.0, step=0.1, value=data.get("forwardPE", 15))
    requiredRateOfReturn = st.number_input("Required Rate of Return (%)", min_value=0.0, max_value=100.0, step=0.5, value=10.0)
    yearsToProject = st.number_input("Years to Project", min_value=1, max_value=30, step=1, value=5)

    # Validate user inputs
    if growth < 0 or growth > 100:
        st.warning("Please enter a growth rate between 0 and 100.")
    elif peFWD < 0:
        st.warning("Please enter a positive Future P/E Ratio.")
    elif requiredRateOfReturn < 0 or requiredRateOfReturn > 100:
        st.warning("Please enter a Required Rate of Return between 0 and 100.")
    elif yearsToProject < 1:
        st.warning("Please enter a positive number of Years to Project.")
    else:
        # Fair value calculation
        futureEPS = fv(epsFWD, growth / 100, yearsToProject)
        futurePrice = futureEPS * peFWD
        stickerPrice = pv(futurePrice, requiredRateOfReturn / 100, yearsToProject)
        upside = (stickerPrice - currentPrice) / currentPrice * 100

        # Show result
        st.metric("Future EPS", f"{futureEPS:.2f}")
        st.metric("Future Price", f"{futurePrice:.2f}")
        st.metric("Sticker Price", f"{stickerPrice:.2f}")
        st.metric("Current Price", f"{currentPrice:.2f}")
        st.metric("Upside", f"{upside:.2f}%")
