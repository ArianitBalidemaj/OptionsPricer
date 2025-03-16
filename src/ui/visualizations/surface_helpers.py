import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

def create_mesh_grid(x_range, y_range, x_points=50, y_points=50):
    """
    Creates a mesh grid for 3D surface plots
    
    Args:
        x_range (tuple): (min, max) for x-axis
        y_range (tuple): (min, max) for y-axis
        x_points (int): Number of points along x-axis
        y_points (int): Number of points along y-axis
        
    Returns:
        tuple: (X, Y) mesh grid arrays
    """
    x = np.linspace(x_range[0], x_range[1], x_points)
    y = np.linspace(y_range[0], y_range[1], y_points)
    return np.meshgrid(x, y)

def get_expiration_days(options_data):
    """
    Extracts days to expiration from options data
    
    Args:
        options_data (dict): Dictionary with expiration dates as keys
        
    Returns:
        list: List of days to expiration for each date
    """
    today = datetime.now()
    days_list = []
    
    for exp_date in options_data.keys():
        expiry = datetime.strptime(exp_date, '%Y-%m-%d')
        days = (expiry - today).days
        if days > 0:  # Only include future expirations
            days_list.append(days)
    
    return sorted(days_list)

def get_strike_range(options_data, current_price, width=0.5):
    """
    Determines a reasonable strike price range based on current price
    
    Args:
        options_data (dict): Dictionary with expiration dates as keys
        current_price (float): Current stock price
        width (float): Width multiplier for range (0.5 = ±50%)
        
    Returns:
        tuple: (min_strike, max_strike)
    """
    min_strike = current_price * (1 - width)
    max_strike = current_price * (1 + width)
    
    return min_strike, max_strike

def create_3d_layout(title, x_title, y_title, z_title, colorscale='Viridis'):
    """
    Creates a standard layout for 3D surface plots
    
    Args:
        title (str): Plot title
        x_title (str): X-axis title
        y_title (str): Y-axis title
        z_title (str): Z-axis title
        colorscale (str): Colorscale name
        
    Returns:
        dict: Layout configuration
    """
    return {
        'title': title,
        'scene': {
            'xaxis_title': x_title,
            'yaxis_title': y_title,
            'zaxis_title': z_title,
            'camera': {
                'eye': {'x': 1.5, 'y': 1.5, 'z': 1}
            }
        },
        'coloraxis': {'colorscale': colorscale},
        'height': 700,
        'margin': {'l': 65, 'r': 50, 'b': 65, 't': 90}
    }