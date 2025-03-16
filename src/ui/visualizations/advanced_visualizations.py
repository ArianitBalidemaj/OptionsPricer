import streamlit as st
from src.ui.visualizations.volatility_surface import volatility_surface_tab
from src.ui.visualizations.option_price_surface import option_price_surface_tab
from src.ui.visualizations.greeks_surface import greeks_surface_tab

def show_advanced_visualizations():
    """
    Shows the advanced 3D visualizations section
    """
    st.markdown("<h2 class='main-header'>Advanced 3D Visualizations</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    This section provides interactive 3D visualizations to help you understand the complex relationships 
    between option prices, Greeks, volatility, stock price, and time to expiration.
    
    Use the tabs below to explore different 3D surfaces.
    """)
    
    # Create tabs for different 3D visualizations
    vol_surface_tab, price_surface_tab, greeks_surface_tab_ui = st.tabs([
        "Volatility Surface", 
        "Option Price Surface", 
        "Greeks Surface"
    ])
    
    # Populate each tab
    with vol_surface_tab:
        volatility_surface_tab()
        
    with price_surface_tab:
        option_price_surface_tab()
        
    with greeks_surface_tab_ui:
        greeks_surface_tab()