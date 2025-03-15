import streamlit as st
import plotly.graph_objects as go

def create_option_visualizations(filtered_options, option_type, current_price):
    """
    Creates and displays visualizations for option data
    
    Args:
        filtered_options (DataFrame): DataFrame containing filtered option data
        option_type (str): "Call" or "Put"
        current_price (float): Current stock price
    """
    st.markdown(f"<h3 class='sub-header'>{option_type} Options Visualization</h3>", unsafe_allow_html=True)
    
    # Create tabs for different visualizations
    price_tab, greeks_tab, vol_tab = st.tabs(["Price Comparison", "Greeks", "Implied Volatility"])
    
    with price_tab:
        # Create price comparison chart
        fig = go.Figure()
        
        if 'lastPrice' in filtered_options.columns:
            fig.add_trace(go.Scatter(
                x=filtered_options['strike'],
                y=filtered_options['lastPrice'],
                mode='markers+lines',
                name='Market Price',
                marker=dict(size=8, color='blue')
            ))
        
        fig.add_trace(go.Scatter(
            x=filtered_options['strike'],
            y=filtered_options['theoreticalPrice'],
            mode='markers+lines',
            name='Theoretical Price',
            marker=dict(size=8, color='red')
        ))
        
        # Add vertical line at current stock price
        fig.add_vline(x=current_price, line_width=2, line_dash="dash", line_color="green")
        fig.add_annotation(x=current_price, y=filtered_options['theoreticalPrice'].max()/2, 
                          text=f"Current Price: ${current_price:.2f}", showarrow=True, arrowhead=1)
        
        fig.update_layout(
            title=f"{option_type} Option Prices vs. Strike",
            xaxis_title="Strike Price ($)",
            yaxis_title="Option Price ($)",
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation in an expander
        with st.expander("Understanding the Price Comparison Chart"):
            st.markdown(f"""
            ### Price Comparison Chart Explanation
            
            This chart compares the **market prices** (blue line) of {option_type.lower()} options with their **theoretical prices** (red line) calculated using the selected pricing model.
            
            **Key insights from this chart:**
            
            - **Price Discrepancies**: Differences between market and theoretical prices may indicate potential mispricing or market inefficiencies
            - **Price Curve**: The shape of the price curve shows how option prices change with different strike prices
            - **At-the-Money (ATM)**: Options with strike prices near the current stock price (green dashed line)
            - **In-the-Money (ITM)**: For {option_type.lower()}s, these are {'to the left' if option_type == 'Call' else 'to the right'} of the current price
            - **Out-of-the-Money (OTM)**: For {option_type.lower()}s, these are {'to the right' if option_type == 'Call' else 'to the left'} of the current price
            
            When market prices are higher than theoretical prices, it may suggest that the market expects more volatility than what's implied by the model. Conversely, when market prices are lower, it could indicate that the market expects less volatility.
            """)
    
    with greeks_tab:
        # Create Greeks visualization
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=filtered_options['strike'],
            y=filtered_options['delta'],
            mode='lines',
            name='Delta',
            line=dict(color='blue', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=filtered_options['strike'],
            y=filtered_options['gamma'],
            mode='lines',
            name='Gamma',
            line=dict(color='red', width=2)
        ))
        
        # Add vertical line at current stock price
        fig.add_vline(x=current_price, line_width=2, line_dash="dash", line_color="green")
        
        fig.update_layout(
            title=f"{option_type} Option Greeks vs. Strike",
            xaxis_title="Strike Price ($)",
            yaxis_title="Greek Value",
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation in an expander
        with st.expander("Understanding the Greeks Chart"):
            st.markdown(f"""
            ### Option Greeks Explanation
            
            This chart shows how the key "Greeks" (sensitivity measures) change across different strike prices for {option_type.lower()} options.
            
            **Delta (Blue Line):**
            - Measures how much the option price changes when the underlying stock price changes by $1
            - For {option_type.lower()}s, Delta ranges from {0 if option_type == 'Call' else -1} to {1 if option_type == 'Call' else 0}
            - Delta is steepest near the current stock price (green dashed line)
            - Delta can also be interpreted as the approximate probability that the option will expire in-the-money
            
            **Gamma (Red Line):**
            - Measures how much Delta changes when the underlying stock price changes by $1
            - Gamma is highest near the current stock price, indicating that at-the-money options experience the largest changes in Delta
            - High Gamma means the option's Delta (and therefore its price) is very sensitive to small changes in the stock price
            
            **Other important Greeks (not shown):**
            - **Theta**: Measures time decay - how much the option loses value each day
            - **Vega**: Measures sensitivity to volatility changes
            - **Rho**: Measures sensitivity to interest rate changes
            
            Traders use Greeks to manage risk and understand how their options positions will behave under different market conditions.
            """)
    
    with vol_tab:
        # Create implied volatility smile visualization
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=filtered_options['strike'],
            y=filtered_options['impliedVolatility'],
            mode='markers+lines',
            name='Implied Volatility',
            marker=dict(size=8, color='purple')
        ))
        
        # Add vertical line at current stock price
        fig.add_vline(x=current_price, line_width=2, line_dash="dash", line_color="green")
        
        fig.update_layout(
            title=f"{option_type} Option Implied Volatility Smile",
            xaxis_title="Strike Price ($)",
            yaxis_title="Implied Volatility",
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation in an expander
        with st.expander("Understanding the Implied Volatility Smile"):
            st.markdown(f"""
            ### Implied Volatility Smile Explanation
            
            This chart shows the "volatility smile" - how implied volatility changes across different strike prices for {option_type.lower()} options.
            
            **What is Implied Volatility?**
            - Implied volatility (IV) is the market's forecast of how much the stock price will move
            - It's "implied" because it's derived from the market price of options
            - Higher IV means the market expects larger price movements (in either direction)
            
            **The Volatility Smile Pattern:**
            - In theory, under the Black-Scholes model, IV should be constant across all strike prices
            - In reality, we often see a "smile" or "smirk" pattern where:
              - Options with strikes far from the current price have higher IV
              - Options with strikes near the current price have lower IV
            
            **What This Tells Us:**
            - The market prices in a higher probability of extreme moves than what a normal distribution would predict
            - This pattern emerged strongly after the 1987 market crash, as traders began pricing in the risk of rare but extreme events
            - For {option_type.lower()} options, a skew toward {'lower' if option_type == 'Put' else 'higher'} strikes may indicate market concern about {'downside' if option_type == 'Put' else 'upside'} risk
            
            Traders can use this information to identify potentially overpriced or underpriced options, or to understand market sentiment about potential price movements.
            """)

def create_combined_volatility_smile(filtered_calls, filtered_puts, current_price, ticker, selected_expiration):
    """
    Creates and displays a combined volatility smile visualization for both call and put options
    
    Args:
        filtered_calls (DataFrame): DataFrame containing filtered call options data
        filtered_puts (DataFrame): DataFrame containing filtered put options data
        current_price (float): Current stock price
        ticker (str): Stock ticker symbol
        selected_expiration (str): Selected expiration date
    """
    st.markdown("<h3 class='sub-header'>Volatility Smile (Combined)</h3>", unsafe_allow_html=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=filtered_calls['strike'],
        y=filtered_calls['impliedVolatility'],
        mode='markers+lines',
        name='Call IV',
        marker=dict(size=8, color='blue')
    ))
    
    fig.add_trace(go.Scatter(
        x=filtered_puts['strike'],
        y=filtered_puts['impliedVolatility'],
        mode='markers+lines',
        name='Put IV',
        marker=dict(size=8, color='red')
    ))
    
    # Add vertical line at current stock price
    fig.add_vline(x=current_price, line_width=2, line_dash="dash", line_color="green")
    fig.add_annotation(x=current_price, y=max(filtered_calls['impliedVolatility'].max(), 
                                            filtered_puts['impliedVolatility'].max())/2, 
                      text=f"Current Price: ${current_price:.2f}", showarrow=True, arrowhead=1)
    
    fig.update_layout(
        title=f"Volatility Smile for {ticker} (Expiry: {selected_expiration})",
        xaxis_title="Strike Price ($)",
        yaxis_title="Implied Volatility",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add explanation of volatility smile
    with st.expander("What is a Volatility Smile?"):
        st.markdown("""
        A **volatility smile** is a common pattern where options with strike prices that are further away from the current stock price (both higher and lower) have higher implied volatilities than options with strike prices near the current stock price.
        
        This pattern contradicts the Black-Scholes model's assumption of constant volatility across all strike prices. The smile shape reflects market expectations about potential large price movements (tail risk) and the supply/demand dynamics of options at different strike prices.
        
        **Key insights from the volatility smile:**
        - **Skew**: If one side of the smile is higher than the other, it indicates market bias toward upside or downside risk
        - **Steepness**: A steeper smile suggests the market expects larger price movements or "fat tails" in the distribution
        - **Level**: The overall height of the smile reflects the general level of expected volatility
        """)

def display_stock_info(ticker, info):
    """
    Displays stock information in a formatted box
    
    Args:
        ticker (str): Stock ticker symbol
        info (dict): Dictionary containing stock information
    """
    st.markdown("<div class='stock-info'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label=f"{ticker} - {info['name']}",
            value=f"${info['current_price']:.2f}",
            delta=f"{info['change_percent']:.2f}%"
        )
    
    with col2:
        st.metric(
            label="Day Range",
            value=f"${info['day_low']:.2f} - ${info['day_high']:.2f}"
        )
    
    with col3:
        st.metric(
            label="Volume",
            value=f"{info['volume']:,}"
        )
    
    st.markdown("</div>", unsafe_allow_html=True)

def display_welcome_message():
    """
    Displays welcome message and instructions when the app is first loaded
    """
    st.markdown("""
    ## Welcome to the Stock Options Analyzer
    
    This tool helps you analyze options data for any publicly traded stock. To get started:
    
    1. Enter a stock ticker symbol in the sidebar (e.g., AAPL, MSFT, TSLA)
    2. Click "Load Options Data" to fetch the latest information
    3. Explore the options chain data, theoretical prices, and visualizations
    
    The analyzer will show you:
    - Current stock information
    - Available options expiration dates
    - Call and put options data
    - Theoretical prices based on the Black-Scholes model
    - Price comparisons between market and theoretical values
    - Greeks (Delta, Gamma, etc.) for risk analysis
    - Volatility smile visualization
    
    **Note:** This tool uses real-time data from Yahoo Finance and theoretical calculations based on the Black-Scholes model.
    """)

def display_footer():
    """
    Displays footer with disclaimer
    """
    st.markdown("""
    ---
    **Disclaimer:** This tool is for educational purposes only. Options trading involves significant risk. 
    The theoretical prices shown are based on the Black-Scholes model and may differ from actual market prices due to various factors.
    """)