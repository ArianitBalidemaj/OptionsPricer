# 📈 Options Pricing Playground

🚀 *An interactive dashboard for exploring options pricing models, volatility surfaces, and trading strategies.*

---

## 📌 Project Status: In Development 🚧  
This project is currently a **work in progress**. The goal is to build an interactive Python-based application that allows users to explore option pricing, implied volatility, and strategy simulations dynamically.

---

## 💡 Overview  
Options Pricing Playground is a **hands-on tool** for understanding and experimenting with options pricing. Users can:  
- Select different **stock tickers** and retrieve real-time options chain data.  
- Use **Black-Scholes, Binomial Tree, and Monte Carlo** models to price options.  
- Adjust key parameters like **strike price, volatility, expiration, and interest rates**.  
- Visualize **volatility smiles, Greeks, and strategy P&L charts**.  
- Simulate **options trading strategies** like straddles, butterflies, and iron condors.  
- Perform **risk management** with Value at Risk (VaR) and stress tests.  

---

## 🛠️ Tech Stack  
- **Backend:** Python (Flask/FastAPI)  
- **Frontend:** Streamlit / Dash  
- **Data Retrieval:** `yfinance`, `pandas`, `numpy`  
- **Options Pricing Models:** `scipy`, `mibian`  
- **Volatility Modeling:** `arch` (GARCH)  
- **Visualization:** `plotly`, `matplotlib`  
- **Deployment:** Docker, AWS/GCP (Planned)  

---

## 📌 Features (Planned)  
✔️ **Real-time options chain data retrieval**  
✔️ **Black-Scholes, Binomial Tree, Monte Carlo pricing models**  
✔️ **Interactive options pricing dashboard**  
✔️ **Volatility smile and surface visualization**  
✔️ **Strategy simulator for Iron Condors, Straddles, etc.**  
✔️ **Risk analysis (VaR, stress testing, scenario modeling)**  

---

## 📂 Project Structure  
```
options-pricing-playground/
│── src/
│   │── models/        # Pricing models (Black-Scholes, Binomial, Monte Carlo)
│   │── data/          # Stock & options chain data retrieval
│   │── ui/            # Interactive dashboard (Streamlit/Dash)
│   │── strategies/    # Options trading strategy simulations
│   │── risk/          # Risk management tools (VaR, stress tests)
│── tests/             # Unit tests for pricing and calculations
│── notebooks/         # Jupyter notebooks for research & prototyping
│── README.md          # Project overview and setup instructions
│── requirements.txt   # Python dependencies
│── Dockerfile         # Deployment configuration

## Installation
# Clone the repository
git clone https://github.com/yourusername/options-pricing-playground.git
cd options-pricing-playground

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

## 📌 Running App
# Run the interactive dashboard (when implemented)
streamlit run src/ui/app.py

