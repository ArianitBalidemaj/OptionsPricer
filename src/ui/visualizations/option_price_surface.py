import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from .surface_helpers import create_mesh_grid, create_3d_layout
from src.models.black_scholes import black_scholes_price

def create_option_price_surface(current_price, days_range, strike_range, volatility, risk_free_rate, option_type='call'):
    """
    Creates a 3D surface of option prices across stock prices and days to expiration
    
    Args:
        current_price (float): Current stock price
        days_range (tuple): (min_days, max_days) range for days to expiration
        strike_range (tuple): (min_strike, max_strike) range for strike prices
        volatility (float): Implied volatility (as decimal)
        risk_free_rate (float): Risk-free interest rate (as decimal)
        option_type (str): 'call' or 'put'
        
    Returns:
        plotly.graph_objects.Figure: 3D surface plot
    """
    # Create price range centered around current price
    price_min = current_price * 0.7
    price_max = current_price * 1.3
    
    # Create mesh grid
    stock_prices = np.linspace(price_min, price_max, 50)
    days = np.linspace(days_range[0], days_range[1], 50)
    
    S, D = np.meshgrid(stock_prices, days)
    
    # Calculate option prices for each point on the grid
    Z = np.zeros_like(S)
    
    for i in range(S.shape[0]):
        for j in range(S.shape[1]):
            stock_price = S[i, j]
            days_to_expiry = D[i, j]
            years_to_expiry = days_to_expiry / 365.0
            
            # Use the strike price from input
            strike_price = strike_range[0] + (strike_range[1] - strike_range[0]) / 2
            
            # Calculate option price
            Z[i, j] = black_scholes_price(
                stock_price, 
                strike_price, 
                years_to_expiry, 
                risk_free_rate, 
                volatility, 
                option_type
            )
    
    # Create 3D surface plot
    fig = go.Figure()
    
    fig.add_trace(go.Surface(
        x=S,
        y=D,
        z=Z,
        colorscale='Viridis',
        colorbar=dict(title='Option Price ($)'),
        lighting=dict(ambient=0.6, diffuse=0.8, roughness=0.5, specular=0.2, fresnel=0.8),
    ))
    
    # Add a vertical plane at current stock price
    y_range = [np.min(D), np.max(D)]
    z_range = [np.min(Z), np.max(Z)]
    
    fig.add_trace(go.Surface(
        x=[current_price, current_price, current_price, current_price],
        y=[y_range[0], y_range[0], y_range[1], y_range[1]],
        z=[[z_range[0], z_range[1]], [z_range[0], z_range[1]]],
        colorscale=[[0, 'rgba(0,255,0,0.3)'], [1, 'rgba(0,255,0,0.3)']],
        showscale=False,
    ))
    
    # Set layout
    option_type_title = "Call" if option_type == "call" else "Put"
    strike_price = strike_range[0] + (strike_range[1] - strike_range[0]) / 2
    
    fig.update_layout(
        **create_3d_layout(
            title=f'{option_type_title} Option Price Surface (Strike: ${strike_price:.2f})',
            x_title='Stock Price ($)',
            y_title='Days to Expiration',
            z_title='Option Price ($)'
        )
    )
    
    return fig

def option_price_surface_tab():
    """
    Creates the option price surface tab content
    """
    st.markdown("### Option Price Surface")
    
    st.markdown("""
    This 3D visualization shows how option prices change with both the underlying stock price and time to expiration.
    It helps visualize the relationship between option price, stock price, and time decay simultaneously.
    """)
    
    # Controls
    col1, col2 = st.columns(2)
    
    with col1:
        option_type = st.radio(
            "Option Type",
            options=["Call", "Put"],
            index=0,
            key="price_surface_option_type"
        ).lower()
        
        volatility = st.slider(
            "Implied Volatility (%)", 
            min_value=10, 
            max_value=100, 
            value=30, 
            step=5,
            key="price_surface_volatility"
        ) / 100
    
    with col2:
        risk_free_rate = st.slider(
            "Risk-Free Rate (%)", 
            min_value=0.0, 
            max_value=10.0, 
            value=5.0, 
            step=0.5,
            key="price_surface_rate"
        ) / 100
        
        max_days = st.slider(
            "Maximum Days to Expiration", 
            min_value=10, 
            max_value=365, 
            value=90, 
            step=5,
            key="price_surface_max_days"
        )
    
    # Get data from session state
    if 'options_data' in st.session_state and 'current_price' in st.session_state:
        options_data = st.session_state.options_data
        current_price = st.session_state.current_price
        
        # Get strike range
        strike_min = current_price * 0.8
        strike_max = current_price * 1.2
        
        # Create and display the surface plot
        fig = create_option_price_surface(
            current_price, 
            (1, max_days), 
            (strike_min, strike_max), 
            volatility, 
            risk_free_rate, 
            option_type
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation
        with st.expander("Understanding the Option Price Surface"):
            st.markdown(f"""
            ### Interpreting the Option Price Surface
            
            This 3D surface shows how {option_type} option prices change with both the underlying stock price and time to expiration.
            
            **Key Features to Look For:**
            
            1. **Price Sensitivity to Stock Price (Delta):**
               - Observe how the surface slopes along the stock price axis
               - Steeper slope indicates higher delta (greater sensitivity to stock price changes)
               - For {option_type}s, the slope is {'positive' if option_type == 'call' else 'negative'}
            
            2. **Time Decay (Theta):**
               - Notice how option prices decrease as you move toward expiration (lower days)
               - This decay accelerates as expiration approaches, especially for at-the-money options
               - The "waterfall" effect shows how time erodes option value
            
            3. **Current Price Plane:**
               - The green vertical plane shows the current stock price
               - Options to the {'right' if option_type == 'call' else 'left'} of this plane are out-of-the-money
               - Options to the {'left' if option_type == 'call' else 'right'} of this plane are in-the-money
            
            4. **Curvature (Gamma):**
               - The curvature of the surface along the price axis indicates gamma
               - Higher curvature means the option's delta changes more rapidly with stock price movements
            
            5. **Impact of Volatility:**
               - Try adjusting the volatility slider to see how it affects the overall height of the surface
               - Higher volatility raises the entire surface, especially for out-of-the-money options
            
            This visualization helps traders understand the complex interplay between stock price movements, time decay, and option pricing.
            """)
    else:
        st.warning("Please load options data first using the 'Load Options Data' button in the sidebar.")