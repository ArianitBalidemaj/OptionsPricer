import streamlit as st
from src.models.black_scholes import black_scholes_price, black_scholes_greeks
from src.models.binomial_pricing import american_option_binomial

def display_options(options_df, option_type, current_price, years_to_expiry, r, pricing_model, n_steps=50):
    """
    Displays options data and calculates theoretical prices
    
    Args:
        options_df (DataFrame): DataFrame containing options data
        option_type (str): "Call" or "Put"
        current_price (float): Current stock price
        years_to_expiry (float): Time to expiration in years
        r (float): Risk-free interest rate
        pricing_model (str): "Black-Scholes (European)" or "Binomial Tree (American)"
        n_steps (int): Number of steps for binomial tree model
        
    Returns:
        DataFrame: Filtered options data with theoretical prices
    """
    # Filter options to show only those near the current price
    filtered_options = options_df[
        (options_df['strike'] >= current_price * 0.8) & 
        (options_df['strike'] <= current_price * 1.2)
    ].copy()
    
    # Calculate theoretical prices based on selected model
    if pricing_model == "Black-Scholes (European)":
        filtered_options['theoreticalPrice'] = filtered_options.apply(
            lambda row: black_scholes_price(
                current_price, 
                row['strike'], 
                years_to_expiry, 
                r, 
                row['impliedVolatility'], 
                option_type.lower()
            ), 
            axis=1
        )
        
        # Calculate Greeks
        greeks_list = []
        for _, row in filtered_options.iterrows():
            greeks = black_scholes_greeks(
                current_price, 
                row['strike'], 
                years_to_expiry, 
                r, 
                row['impliedVolatility'], 
                option_type.lower()
            )
            greeks_list.append(greeks)
        
        # Add Greeks to DataFrame
        for greek in ['Delta', 'Gamma', 'Vega', 'Theta', 'Rho']:
            filtered_options[greek.lower()] = [g[greek] for g in greeks_list]
        
    else:  # Binomial Tree (American)
        filtered_options['theoreticalPrice'] = filtered_options.apply(
            lambda row: american_option_binomial(
                current_price, 
                row['strike'], 
                r, 
                years_to_expiry, 
                row['impliedVolatility'], 
                n_steps, 
                option_type.lower()
            ), 
            axis=1
        )
    
    # Calculate price difference
    if 'lastPrice' in filtered_options.columns:
        filtered_options['priceDiff'] = filtered_options['theoreticalPrice'] - filtered_options['lastPrice']
        filtered_options['priceDiffPct'] = (filtered_options['priceDiff'] / filtered_options['lastPrice']) * 100
    
    # Display the options data
    st.dataframe(
        filtered_options[[
            'strike', 'lastPrice', 'theoreticalPrice', 
            'priceDiff', 'priceDiffPct', 'impliedVolatility', 
            'volume', 'openInterest', 'delta', 'gamma', 'theta'
        ]].style.format({
            'lastPrice': '${:.2f}',
            'theoreticalPrice': '${:.2f}',
            'priceDiff': '${:.2f}',
            'priceDiffPct': '{:.2f}%',
            'impliedVolatility': '{:.2%}',
            'delta': '{:.4f}',
            'gamma': '{:.4f}',
            'theta': '{:.4f}'
        }),
        use_container_width=True
    )
    
    return filtered_options