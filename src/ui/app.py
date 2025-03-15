import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.models.black_scholes import black_scholes_price, black_scholes_greeks
from src.data.fetch_data import get_options_chain, get_stock_data, get_stock_info
from src.models.binomial_pricing import american_option_binomial
from src.ui.visualization_helpers import (
    create_option_visualizations, 
    create_combined_volatility_smile,
    display_stock_info,
    display_welcome_message,
    display_footer
)
from src.ui.options_helpers import display_options

#####################################################
# PAGE CONFIGURATION AND STYLING
#####################################################

# Set page configuration
st.set_page_config(
    page_title="Stock Options Analyzer",
    page_icon="📊",
    layout="wide"
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
    }
    .stock-info {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

#####################################################
# HEADER AND SIDEBAR CONTROLS
#####################################################

# Header
st.markdown("<h1 class='main-header'>Stock Options Analyzer</h1>", unsafe_allow_html=True)

# Sidebar for user inputs
st.sidebar.markdown("<h2 class='sub-header'>Settings</h2>", unsafe_allow_html=True)

# Stock ticker input
ticker = st.sidebar.text_input("Enter Stock Ticker", value="AAPL").upper()

# Load data button
load_data = st.sidebar.button("Load Options Data")

# Risk-free rate input (user configurable)
r = st.sidebar.number_input("Risk-Free Rate (%)", min_value=0.0, max_value=15.0, value=5.0, step=0.1) / 100

# Pricing model selection
pricing_model = st.sidebar.radio(
    "Pricing Model",
    ["Black-Scholes (European)", "Binomial Tree (American)"]
)

# If binomial model is selected, show number of steps slider
if pricing_model == "Binomial Tree (American)":
    n_steps = st.sidebar.slider("Number of Steps", min_value=20, max_value=200, value=50, step=10)
else:
    n_steps = 50  # Default value

#####################################################
# MAIN CONTENT AREA - DATA LOADING AND PROCESSING
#####################################################

# Main content area
if load_data or 'options_data' in st.session_state:
    try:
        # Show loading message
        with st.spinner(f"Fetching data for {ticker}..."):
            # Get stock data using the existing function
            stock_data = get_stock_data(ticker, period="1d")
            
            # Get stock info from our function
            info, stock_info = get_stock_info(ticker)
            current_price = info['current_price']
            
            # Get options data if not already in session state
            if 'options_data' not in st.session_state or st.session_state.get('current_ticker') != ticker:
                options_data = get_options_chain(ticker)
                st.session_state.options_data = options_data
                st.session_state.current_ticker = ticker
            else:
                options_data = st.session_state.options_data
            
            # Get list of expiration dates
            expirations = list(options_data.keys())
        
        #####################################################
        # STOCK INFORMATION DISPLAY
        #####################################################
        
        # Display stock information using helper function
        display_stock_info(ticker, info)
        
        #####################################################
        # EXPIRATION DATE SELECTION AND TIME CALCULATION
        #####################################################
        
        # Select expiration date
        selected_expiration = st.selectbox("Select Expiration Date", expirations)
        
        # Calculate time to expiration
        expiry_date = datetime.strptime(selected_expiration, '%Y-%m-%d')
        today = datetime.now()
        days_to_expiry = (expiry_date - today).days
        years_to_expiry = days_to_expiry / 365.0
        
        st.write(f"Days to Expiration: **{days_to_expiry}**")
        st.write(f"Years to Expiration: **{years_to_expiry}**")
        
        # Get options for selected expiration
        calls = options_data[selected_expiration]["calls"]
        puts = options_data[selected_expiration]["puts"]
        
        #####################################################
        # CALL AND PUT OPTIONS TABS
        #####################################################
        
        # Create tabs for calls and puts
        call_tab, put_tab = st.tabs(["Call Options", "Put Options"])
        
        # Display options in each tab
        with call_tab:
            st.markdown("<h3 class='sub-header'>Call Options Analysis</h3>", unsafe_allow_html=True)
            filtered_calls = display_options(
                calls, "Call", current_price, years_to_expiry, r, pricing_model, n_steps
            )
            
            # Create visualization for calls
            if not filtered_calls.empty and 'strike' in filtered_calls.columns:
                create_option_visualizations(filtered_calls, "Call", current_price)
        
        with put_tab:
            st.markdown("<h3 class='sub-header'>Put Options Analysis</h3>", unsafe_allow_html=True)
            filtered_puts = display_options(
                puts, "Put", current_price, years_to_expiry, r, pricing_model, n_steps
            )
            
            # Create visualization for puts
            if not filtered_puts.empty and 'strike' in filtered_puts.columns:
                create_option_visualizations(filtered_puts, "Put", current_price)
        
        #####################################################
        # COMBINED VOLATILITY SMILE
        #####################################################
        
        # Add a section for the combined volatility smile (put and call)
        if not filtered_calls.empty and not filtered_puts.empty:
            create_combined_volatility_smile(
                filtered_calls, filtered_puts, current_price, ticker, selected_expiration
            )
    
    #####################################################
    # ERROR HANDLING
    #####################################################
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.write("Please check the ticker symbol and try again.")

#####################################################
# WELCOME MESSAGE (DISPLAYED ON FIRST LOAD)
#####################################################

else:
    # Display welcome message using helper function
    display_welcome_message()

#####################################################
# FOOTER
#####################################################

# Add footer using helper function
display_footer()