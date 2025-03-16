import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from .surface_helpers import create_mesh_grid, get_expiration_days, get_strike_range, create_3d_layout

def interpolate_volatility_surface(options_data, current_price, strike_range=None):
    """
    Interpolates implied volatility across strikes and expirations
    
    Args:
        options_data (dict): Dictionary with expiration dates as keys
        current_price (float): Current stock price
        strike_range (tuple): Optional (min_strike, max_strike) to limit range
        
    Returns:
        tuple: (strikes, days, volatility_surface)
    """
    # Get all expiration days
    expirations = list(options_data.keys())
    today = datetime.now()
    
    # Prepare data structures
    all_strikes = set()
    all_days = []
    iv_data = {}
    
    # Extract all strikes and days to expiration
    for exp_date in expirations:
        expiry = datetime.strptime(exp_date, '%Y-%m-%d')
        days = (expiry - today).days
        if days <= 0:  # Skip past expirations
            continue
            
        all_days.append(days)
        
        # Get both calls and puts for this expiration
        calls = options_data[exp_date]["calls"]
        puts = options_data[exp_date]["puts"]
        
        # Extract strikes and IVs
        for options in [calls, puts]:
            for _, row in options.iterrows():
                strike = row['strike']
                iv = row['impliedVolatility']
                
                # Skip if outside strike range
                if strike_range and (strike < strike_range[0] or strike > strike_range[1]):
                    continue
                    
                if not np.isnan(iv) and iv > 0:
                    all_strikes.add(strike)
                    iv_data[(days, strike)] = iv
    
    # Sort days and strikes
    all_days = sorted(all_days)
    all_strikes = sorted(all_strikes)
    
    # Create mesh grid for interpolation
    if not strike_range:
        strike_range = (min(all_strikes), max(all_strikes))
    
    strike_points = 50
    day_points = min(50, len(all_days) * 5)  # Ensure enough points but not too many
    
    strikes = np.linspace(strike_range[0], strike_range[1], strike_points)
    days = np.linspace(min(all_days), max(all_days), day_points)
    
    # Create empty volatility surface
    volatility_surface = np.zeros((len(days), len(strikes)))
    
    # Simple interpolation - for each point, find nearest data point
    for i, d in enumerate(days):
        for j, s in enumerate(strikes):
            # Find closest day and strike with data
            closest_day = min(all_days, key=lambda x: abs(x - d))
            closest_strike = min(all_strikes, key=lambda x: abs(x - s))
            
            # Get IV if available, otherwise use ATM IV
            if (closest_day, closest_strike) in iv_data:
                volatility_surface[i, j] = iv_data[(closest_day, closest_strike)]
            else:
                # Find ATM IV for this day
                atm_strike = min(all_strikes, key=lambda x: abs(x - current_price))
                if (closest_day, atm_strike) in iv_data:
                    volatility_surface[i, j] = iv_data[(closest_day, atm_strike)]
                else:
                    # Default to average IV if no ATM available
                    volatility_surface[i, j] = np.mean([v for k, v in iv_data.items() if k[0] == closest_day])
    
    # Convert days and strikes to meshgrid for plotting
    D, S = np.meshgrid(days, strikes)
    
    return D, S, volatility_surface.T  # Transpose to match meshgrid dimensions

def create_volatility_surface(options_data, current_price, width_pct=0.5, colorscale='Viridis'):
    """
    Creates a 3D volatility surface visualization
    
    Args:
        options_data (dict): Dictionary with expiration dates as keys
        current_price (float): Current stock price
        width_pct (float): Width of strike range as percentage of current price
        colorscale (str): Colorscale for the surface
        
    Returns:
        plotly.graph_objects.Figure: 3D surface plot
    """
    # Get strike range
    strike_range = (current_price * (1 - width_pct), current_price * (1 + width_pct))
    
    # Interpolate volatility surface
    days, strikes, vol_surface = interpolate_volatility_surface(options_data, current_price, strike_range)
    
    # Create 3D surface plot
    fig = go.Figure()
    
    fig.add_trace(go.Surface(
        x=days,
        y=strikes,
        z=vol_surface,
        colorscale=colorscale,
        colorbar=dict(title='Implied Volatility'),
        lighting=dict(ambient=0.6, diffuse=0.8, roughness=0.5, specular=0.2, fresnel=0.8),
    ))
    
    # Add a plane at current price
    x_range = [np.min(days), np.max(days)]
    z_range = [np.min(vol_surface), np.max(vol_surface)]
    
    fig.add_trace(go.Surface(
        x=[x_range[0], x_range[1], x_range[1], x_range[0]],
        y=[current_price, current_price, current_price, current_price],
        z=[[z_range[0], z_range[0]], [z_range[1], z_range[1]]],
        colorscale=[[0, 'rgba(0,255,0,0.3)'], [1, 'rgba(0,255,0,0.3)']],
        showscale=False,
    ))
    
    # Set layout
    fig.update_layout(
        **create_3d_layout(
            title='Implied Volatility Surface',
            x_title='Days to Expiration',
            y_title='Strike Price ($)',
            z_title='Implied Volatility',
            colorscale=colorscale
        )
    )
    
    return fig

def volatility_surface_tab():
    """
    Creates the volatility surface tab content
    """
    st.markdown("### Implied Volatility Surface")
    
    st.markdown("""
    This 3D visualization shows how implied volatility varies across both strike prices and time to expiration.
    The surface reveals both the volatility smile (across strikes) and term structure (across time).
    """)
    
    # Controls
    col1, col2 = st.columns(2)
    
    with col1:
        width_pct = st.slider(
            "Strike Range (% of current price)", 
            min_value=0.1, 
            max_value=1.0, 
            value=0.5, 
            step=0.1,
            key="vol_surface_width"
        )
    
    with col2:
        colorscale = st.selectbox(
            "Color Scale",
            options=["Viridis", "Plasma", "Inferno", "Magma", "Cividis", "Turbo"],
            index=0,
            key="vol_surface_colorscale"
        )
    
    # Get data from session state
    if 'options_data' in st.session_state and 'current_price' in st.session_state:
        options_data = st.session_state.options_data
        current_price = st.session_state.current_price
        
        # Create and display the surface plot
        fig = create_volatility_surface(options_data, current_price, width_pct, colorscale)
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation
        with st.expander("Understanding the Volatility Surface"):
            st.markdown("""
            ### Interpreting the Volatility Surface
            
            The volatility surface is a 3D representation of implied volatility across different strike prices and expiration dates.
            
            **Key Features to Look For:**
            
            1. **Volatility Smile/Skew (Along Strike Axis):**
               - A "smile" shape indicates higher IV for both high and low strikes
               - A "skew" (higher IV for lower strikes) suggests market concern about downside risk
            
            2. **Term Structure (Along Time Axis):**
               - Upward slope: Long-term uncertainty exceeds short-term (normal condition)
               - Downward slope: Short-term uncertainty exceeds long-term (often during market stress)
               - Humps: May indicate expected volatility around specific events (earnings, etc.)
            
            3. **Surface Curvature:**
               - Steep areas indicate high sensitivity to changes in strike or time
               - Flat areas suggest more consistent volatility expectations
            
            4. **Current Price Plane:**
               - The green plane shows the current stock price
               - Observe how volatility changes as you move away from this plane
            
            This visualization helps option traders identify relative value across the entire options chain and develop strategies that exploit the volatility structure.
            """)
    else:
        st.warning("Please load options data first using the 'Load Options Data' button in the sidebar.")