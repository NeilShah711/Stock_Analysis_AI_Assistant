import yfinance as yf
import requests
import pandas as pd
import numpy as np
import ta
import json
import ollama
from datetime import datetime, timedelta

class StockAnalyzer:
    def __init__(self):
        self.ollama_model = "llama2" 
        
    def get_stock_data(self, symbol: str, period: str = "2y") -> pd.DataFrame:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, auto_adjust=True)
            print("Columns after history():", df.columns)
            if df.empty:
                raise ValueError(f"No data found for {symbol}")
            return df
        except Exception as e:
            print(f"[ERROR] Could not fetch data for {symbol}: {e}")
            return pd.DataFrame()

    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> dict:
        """Calculate various technical indicators."""
        if df.empty:
            return None
        # Moving Averages
        df['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20)
        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['SMA_200'] = ta.trend.sma_indicator(df['Close'], window=200)
        
        # RSI
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        
        # MACD
        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df['Close'])
        df['BB_Upper'] = bollinger.bollinger_hband()
        df['BB_Lower'] = bollinger.bollinger_lband()
        
        # Get the latest values
        latest = df.iloc[-1]
        
        return {
            'price': latest['Close'],
            'sma_20': latest['SMA_20'],
            'sma_50': latest['SMA_50'],
            'sma_200': latest['SMA_200'],
            'rsi': latest['RSI'],
            'macd': latest['MACD'],
            'macd_signal': latest['MACD_Signal'],
            'bb_upper': latest['BB_Upper'],
            'bb_lower': latest['BB_Lower']
        }
    
    def generate_ai_analysis(self, symbol: str, indicators: dict) -> dict:
        """Generate AI-powered analysis using Ollama."""
        prompt = f"""
        Analyze the following stock ({symbol}) with these technical indicators:
        - Current Price: ${indicators['price']:.2f}
        - RSI: {indicators['rsi']:.2f}
        - MACD: {indicators['macd']:.2f}
        - 20-day SMA: ${indicators['sma_20']:.2f}
        - 50-day SMA: ${indicators['sma_50']:.2f}
        - 200-day SMA: ${indicators['sma_200']:.2f}
        
        Provide:
        1. A brief summary about the stock
        2. A brief technical analysis
        3. A recommendation (Buy/Sell/Hold)
        4. Potential price targets in next 3-6 months
        5. Key risks and considerations
        6. Suggested portfolio allocation percentage
        """
        
        response = ollama.generate(model=self.ollama_model, prompt=prompt)
        
        analysis = {
            'technical_analysis': response['response'],
            'recommendation': self._extract_recommendation(response['response']),
            'portfolio_allocation': self._extract_allocation(response['response']),
            'risks': self._extract_risks(response['response'])
        }
        
        return analysis
    
    def _extract_recommendation(self, text: str) -> str:
        """Extract the recommendation from AI response."""
        if 'buy' in text.lower():
            return 'Buy'
        elif 'sell' in text.lower():
            return 'Sell'
        return 'Hold'
    
    def _extract_allocation(self, text: str) -> float:
        """Extract the suggested portfolio allocation from AI response."""
        # Default to 5% if no clear allocation is found
        try:
            # Look for percentage in the text
            import re
            percentages = re.findall(r'(\d+)%', text)
            if percentages:
                return min(float(percentages[0]) / 100, 1.0)
        except:
            pass
        return 0.05
    
    def _extract_risks(self, text: str) -> str:
        """Extract risk factors from AI response."""
        # This is a simple implementation - could be enhanced
        return "Please review the full analysis for detailed risk factors."
    
    def analyze_stock(self, symbol: str) -> dict:
        """Perform complete stock analysis."""
        df = self.get_stock_data(symbol)
        
        
        indicators = self.calculate_technical_indicators(df)
        
        ai_analysis = self.generate_ai_analysis(symbol, indicators)
        
        return {
            'symbol': symbol,
            'indicators': indicators,
            'analysis': ai_analysis,
            'timestamp': datetime.utcnow().isoformat()
        } 