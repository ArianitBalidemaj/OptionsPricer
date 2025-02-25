import numpy as np
import scipy.stats as stats

def black_scholes_price(S, K, T, r, sigma, option_type="call"):
    """
    Computes the Black-Scholes option price.

    Args:
        S (float): Current stock price.
        K (float): Strike price.
        T (float): Time to expiration (in years).
        r (float): Risk-free interest rate (as decimal).
        sigma (float): Implied volatility (as decimal).
        option_type (str): "call" or "put".

    Returns:
        float: Theoretical option price.
    """
    if T <= 0:
        return max(0, S - K) if option_type == "call" else max(0, K - S)

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == "call":
        price = S * stats.norm.cdf(d1) - K * np.exp(-r * T) * stats.norm.cdf(d2)
    elif option_type == "put":
        price = K * np.exp(-r * T) * stats.norm.cdf(-d2) - S * stats.norm.cdf(-d1)
    else:
        raise ValueError("Invalid option_type. Choose 'call' or 'put'.")

    return price

def black_scholes_greeks(S, K, T, r, sigma, option_type="call"):
    """
    Computes the Greeks (Delta, Gamma, Vega, Theta, Rho) using the Black-Scholes model.

    Args:
        S (float): Current stock price.
        K (float): Strike price.
        T (float): Time to expiration (in years).
        r (float): Risk-free interest rate (as decimal).
        sigma (float): Implied volatility (as decimal).
        option_type (str): "call" or "put".

    Returns:
        dict: A dictionary with Delta, Gamma, Vega, Theta, and Rho.
    """
    if T <= 0:
        return {"Delta": 0, "Gamma": 0, "Vega": 0, "Theta": 0, "Rho": 0}

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    delta = stats.norm.cdf(d1) if option_type == "call" else stats.norm.cdf(d1) - 1
    gamma = stats.norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = S * stats.norm.pdf(d1) * np.sqrt(T)
    theta = (-S * stats.norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
            - r * K * np.exp(-r * T) * stats.norm.cdf(d2 if option_type == "call" else -d2))
    rho = K * T * np.exp(-r * T) * stats.norm.cdf(d2 if option_type == "call" else -d2)

    return {"Delta": delta, "Gamma": gamma, "Vega": vega, "Theta": theta, "Rho": rho}

if __name__ == "__main__":
    # Example usage
    S = 150    # Stock price
    K = 160    # Strike price
    T = 0.5    # Time to expiration (6 months)
    r = 0.02   # Risk-free rate (2%)
    sigma = 0.25  # Volatility (25%)

    option_type = "call"

    price = black_scholes_price(S, K, T, r, sigma, option_type)
    greeks = black_scholes_greeks(S, K, T, r, sigma, option_type)

    print(f"{option_type.capitalize()} Option Price: {price:.2f}")
    print("Greeks:", greeks)
