import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from .surface_helpers import create_mesh_grid, create_3d_layout
from src.models.black_scholes import black_scholes_greeks

def create_greeks_surface(current_price, days_range, strike_range, volatility, risk_free_rate, greek, option_type='call'):
    """
    Creates a 3D surface of a selected Greek across stock prices and days to expiration
    
    Args:
        current_price (float): Current stock price
        days_range (tuple): (min_days, max_days) range for days to expiration
        strike_range (tuple): (min_strike, max_strike) range for strike prices
        volatility (float): Implied volatility (as decimal)
        risk_free_rate (float): Risk-free interest rate (as decimal)
        greek (str): Greek to visualize ('Delta', 'Gamma', 'Theta', 'Vega', 'Rho')
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
    
    # Calculate Greek values for each point on the grid
    Z = np.zeros_like(S)
    
    for i in range(S.shape[0]):
        for j in range(S.shape[1]):
            stock_price = S[i, j]
            days_to_expiry = D[i, j]
            years_to_expiry = days_to_expiry / 365.0
            
            # Use the strike price from input
            strike_price = strike_range[0] + (strike_range[1] - strike_range[0]) / 2
            
            # Calculate Greeks
            greeks = black_scholes_greeks(
                stock_price, 
                strike_price, 
                years_to_expiry, 
                risk_free_rate, 
                volatility, 
                option_type
            )
            
            Z[i, j] = greeks[greek]
    
    # Create 3D surface plot
    fig = go.Figure()
    
    # Choose colorscale based on Greek
    colorscales = {
        'Delta': 'RdBu',
        'Gamma': 'Viridis',
        'Theta': 'Plasma',
        'Vega': 'Cividis',
        'Rho': 'Inferno'
    }
    
    colorscale = colorscales.get(greek, 'Viridis')
    
    fig.add_trace(go.Surface(
        x=S,
        y=D,
        z=Z,
        colorscale=colorscale,
        colorbar=dict(title=f'{greek} Value'),
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
            title=f'{option_type_title} Option {greek} Surface (Strike: ${strike_price:.2f})',
            x_title='Stock Price ($)',
            y_title='Days to Expiration',
            z_title=f'{greek} Value',
            colorscale=colorscale
        )
    )
    
    return fig

def greeks_surface_tab():
    """
    Creates the Greeks surface tab content
    """
    st.markdown("### Option Greeks Surface")
    
    st.markdown("""
    This 3D visualization shows how option Greeks (Delta, Gamma, Theta, Vega, Rho) change with both the underlying stock price and time to expiration.
    It provides a comprehensive view of option sensitivity across different market conditions and time horizons.
    """)
    
    # Controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        option_type = st.radio(
            "Option Type",
            options=["Call", "Put"],
            index=0,
            key="greeks_surface_option_type"
        ).lower()
        
        greek = st.selectbox(
            "Greek to Visualize",
            options=["Delta", "Gamma", "Theta", "Vega", "Rho"],
            index=0,
            key="greeks_surface_greek"
        )
    
    with col2:
        volatility = st.slider(
            "Implied Volatility (%)", 
            min_value=10, 
            max_value=100, 
            value=30, 
            step=5,
            key="greeks_surface_volatility"
        ) / 100
        
        risk_free_rate = st.slider(
            "Risk-Free Rate (%)", 
            min_value=0.0, 
            max_value=10.0, 
            value=5.0, 
            step=0.5,
            key="greeks_surface_rate"
        ) / 100
    
    with col3:
        max_days = st.slider(
            "Maximum Days to Expiration", 
            min_value=10, 
            max_value=365, 
            value=90, 
            step=5,
            key="greeks_surface_max_days"
        )
    
    # Get data from session state
    if 'options_data' in st.session_state and 'current_price' in st.session_state:
        options_data = st.session_state.options_data
        current_price = st.session_state.current_price
        
        # Get strike range
        strike_min = current_price * 0.8
        strike_max = current_price * 1.2
        
        # Create and display the surface plot
        fig = create_greeks_surface(
            current_price, 
            (1, max_days), 
            (strike_min, strike_max), 
            volatility, 
            risk_free_rate, 
            greek,
            option_type
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation
        with st.expander(f"Understanding the {greek} Surface"):
            if greek == "Delta":
                st.markdown(f"""
                ### Interpreting the Delta Surface
                
                Delta measures the rate of change of the option price with respect to changes in the underlying stock price.
                
                **Key Features to Look For:**
                
                1. **Delta Range:**
                   - For {option_type} options, delta ranges from {0 if option_type == 'put' else -1} to {1 if option_type == 'call' else 0}
                   - At-the-money options have deltas near {0.5 if option_type == 'call' else -0.5}
                
                2. **Delta Behavior Across Stock Prices:**
                   - Deep in-the-money options approach a delta of {1 if option_type == 'call' else -1}
                   - Deep out-of-the-money options approach a delta of 0
                   - The steepest change in delta occurs near the strike price
                
                3. **Time Effect on Delta:**
                   - As expiration approaches, delta becomes more binary (closer to 0 or {1 if option_type == 'call' else -1})
                   - This creates the "cliff" effect visible in the surface near expiration
                
                4. **Practical Applications:**
                   - Delta is often interpreted as the approximate probability of finishing in-the-money
                   - Delta also represents the equivalent stock position (e.g., a call with 0.5 delta behaves like owning 50 shares)
                   - Delta hedging involves offsetting this exposure to create position-neutral strategies
                """)
            elif greek == "Gamma":
                st.markdown(f"""
                ### Interpreting the Gamma Surface
                
                Gamma measures the rate of change of Delta with respect to changes in the underlying stock price.
                
                **Key Features to Look For:**
                
                1. **Gamma Distribution:**
                   - Gamma is always positive for both calls and puts
                   - Gamma is highest for at-the-money options
                   - Gamma decreases as you move away from the strike price in either direction
                
                2. **Time Effect on Gamma:**
                   - Gamma increases as expiration approaches for at-the-money options
                   - This creates the "ridge" effect visible in the surface near expiration
                   - Long-dated options have lower gamma (more gradual delta changes)
                
                3. **Volatility Effect:**
                   - Lower volatility increases the peak gamma value
                   - Higher volatility spreads gamma out across a wider range of stock prices
                
                4. **Practical Applications:**
                   - High gamma positions can experience rapid changes in delta (and thus P&L)
                   - Gamma risk increases as expiration approaches
                   - Option sellers are typically short gamma (negative gamma exposure)
                   - Option buyers are typically long gamma (positive gamma exposure)
                """)
            elif greek == "Theta":
                st.markdown(f"""
                ### Interpreting the Theta Surface
                
                Theta measures the rate of change of the option price with respect to the passage of time (time decay).
                
                **Key Features to Look For:**
                
                1. **Theta Distribution:**
                   - Theta is typically negative for both calls and puts (options lose value over time)
                   - Theta is most negative for at-the-money options
                   - Theta becomes less negative for deep in-the-money or out-of-the-money options
                
                2. **Time Effect on Theta:**
                   - Theta accelerates as expiration approaches (time decay is not linear)
                   - This creates the "valley" effect visible in the surface near expiration
                   - Long-dated options have less theta (slower time decay)
                
                3. **Volatility Effect:**
                   - Higher volatility generally leads to more negative theta
                   - This is because higher-priced options have more time value to lose
                
                4. **Practical Applications:**
                   - Option sellers benefit from theta (positive theta exposure)
                   - Option buyers are hurt by theta (negative theta exposure)
                   - Calendar spreads aim to profit from the differential time decay between options
                   - Weekends and holidays can be advantageous for option sellers (time passes but markets are closed)
                """)
            elif greek == "Vega":
                st.markdown(f"""
                ### Interpreting the Vega Surface
                
                Vega measures the rate of change of the option price with respect to changes in implied volatility.
                
                **Key Features to Look For:**
                
                1. **Vega Distribution:**
                   - Vega is always positive for both calls and puts (higher volatility increases option prices)
                   - Vega is highest for at-the-money options
                   - Vega decreases as you move away from the strike price in either direction
                
                2. **Time Effect on Vega:**
                   - Vega decreases as expiration approaches
                   - Long-dated options have higher vega (more sensitive to volatility changes)
                   - This creates the gradual slope visible in the surface along the time axis
                
                3. **Practical Applications:**
                   - Vega risk is important during earnings announcements, economic releases, or other events that might affect volatility
                   - Option buyers are typically long vega (benefit from volatility increases)
                   - Option sellers are typically short vega (benefit from volatility decreases)
                   - Volatility strategies like straddles and strangles have high vega exposure
                """)
            elif greek == "Rho":
                st.markdown(f"""
                ### Interpreting the Rho Surface
                
                Rho measures the rate of change of the option price with respect to changes in the risk-free interest rate.
                
                **Key Features to Look For:**
                
                1. **Rho Distribution:**
                   - For calls, rho is positive (higher rates increase call prices)
                   - For puts, rho is negative (higher rates decrease put prices)
                   - Rho's magnitude increases as options become more in-the-money
                
                2. **Time Effect on Rho:**
                   - Rho increases with time to expiration
                   - Long-dated options have higher rho (more sensitive to interest rate changes)
                   - This creates the gradual slope visible in the surface along the time axis
                
                3. **Practical Applications:**
                   - Rho is often the least monitored Greek because interest rates typically change slowly
                   - However, rho becomes important during periods of changing monetary policy
                   - Long-dated options and LEAPS have significant rho exposure
                   - Interest rate changes can affect put-call parity relationships
                """)
    else:
        st.warning("Please load options data first using the 'Load Options Data' button in the sidebar.")