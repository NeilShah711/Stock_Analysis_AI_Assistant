import yfinance as yf
print(yf.Ticker("AAPL").history(period="1y"))