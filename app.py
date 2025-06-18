import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import json
import os
from dotenv import load_dotenv

from models.database import init_db, User, StockAnalysis, Portfolio, UserRole
from utils.auth import hash_password, verify_password, create_access_token, verify_token
from services.stock_analysis import StockAnalyzer

# Load environment variables
load_dotenv()

# Initialize database
engine = init_db(os.getenv("DATABASE_URL", "sqlite:///stock_analysis.db"))

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'token' not in st.session_state:
    st.session_state.token = None

def login_page():
    st.title("Stock Analysis AI Assistant")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            # Verify credentials
            with engine.connect() as conn:
                user = conn.execute(User.__table__.select().where(User.username == username)).first()
                if user and verify_password(password, user.password_hash):
                    st.session_state.user = {
                        'id': user.id,
                        'username': user.username,
                        'role': user.role.value
                    }
                    st.session_state.token = create_access_token({'sub': user.username})
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with tab2:
        st.subheader("Register")
        new_username = st.text_input("Username", key="reg_username")
        new_email = st.text_input("Email", key="reg_email")
        new_password = st.text_input("Password", type="password", key="reg_password")
        role = st.selectbox("Role", ["analyst", "investor"])
        
        if st.button("Register"):
            with engine.connect() as conn:
                # Check if username exists
                if conn.execute(User.__table__.select().where(User.username == new_username)).first():
                    st.error("Username already exists")
                else:
                    # Create new user
                    new_user = User(
                        username=new_username,
                        email=new_email,
                        password_hash=hash_password(new_password),
                        role=UserRole(role)
                    )
                    conn.execute(User.__table__.insert(), new_user.__dict__)
                    conn.commit()
                    st.success("Registration successful! Please login.")

def main_page():
    st.title("Stock Analysis AI Assistant")
    
    # Sidebar
    st.sidebar.title(f"Welcome, {st.session_state.user['username']}")
    st.sidebar.write(f"Role: {st.session_state.user['role'].capitalize()}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.token = None
        st.rerun()
    
    # Main content
    tab1, tab2 = st.tabs(["Stock Analysis", "Portfolio"])
    
    with tab1:
        st.subheader("Stock Analysis")
        symbol = st.text_input("Enter Stock Symbol (e.g., AAPL)").strip().upper()
        st.write(f"Symbol entered: '{symbol}'")  # Debug: Show the symbol
        
        if symbol:
            analyzer = StockAnalyzer()
            try:
                stock_data = analyzer.get_stock_data(symbol)
                if stock_data.empty:
                    st.error("No data found for this symbol and period. Please check the symbol or try a different one.")
                    return
                st.write(stock_data)  # Debug: Show the raw DataFrame
                analysis = analyzer.analyze_stock(symbol)
                
                # Display stock price chart
                fig = go.Figure(data=[go.Candlestick(
                    x=stock_data.index,
                    open=stock_data['Open'],
                    high=stock_data['High'],
                    low=stock_data['Low'],
                    close=stock_data['Close']
                )])
                fig.update_layout(title=f"{symbol} Stock Price")
                st.plotly_chart(fig)
                
                # Display technical indicators
                st.subheader("Technical Indicators")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Current Price", f"${analysis['indicators']['price']:.2f}")
                    st.metric("RSI", f"{analysis['indicators']['rsi']:.2f}")
                with col2:
                    st.metric("MACD", f"{analysis['indicators']['macd']:.2f}")
                    st.metric("20-day SMA", f"${analysis['indicators']['sma_20']:.2f}")
                
                # Display AI Analysis
                st.subheader("AI Analysis")
                st.write(analysis['analysis']['technical_analysis'])
                
                # Display recommendation
                st.subheader("Recommendation")
                st.write(f"Action: {analysis['analysis']['recommendation']}")
                st.write(f"Suggested Portfolio Allocation: {analysis['analysis']['portfolio_allocation']*100:.1f}%")
                
                # Save analysis if user is an analyst
                if st.session_state.user['role'] == 'analyst':
                    if st.button("Save Analysis"):
                        with engine.connect() as conn:
                            new_analysis = StockAnalysis(
                                analyst_id=st.session_state.user['id'],
                                stock_symbol=symbol,
                                technical_indicators=json.dumps(analysis['indicators']),
                                recommendation=analysis['analysis']['recommendation'],
                                portfolio_allocation=analysis['analysis']['portfolio_allocation'],
                                analysis_text=analysis['analysis']['technical_analysis'],
                                price_at_analysis=analysis['indicators']['price']
                            )
                            conn.execute(StockAnalysis.__table__.insert(), new_analysis.__dict__)
                            conn.commit()
                            st.success("Analysis saved successfully!")
                
            except Exception as e:
                import traceback
                st.error(f"Error analyzing stock: {str(e)}")
                st.text(traceback.format_exc())
    
    with tab2:
        st.subheader("Portfolio")
        if st.session_state.user['role'] == 'investor':
            # Display investor's portfolio
            with engine.connect() as conn:
                portfolio = conn.execute(
                    Portfolio.__table__.select().where(
                        Portfolio.investor_id == st.session_state.user['id']
                    )
                ).fetchall()
                
                if portfolio:
                    for entry in portfolio:
                        st.write(f"Symbol: {entry.stock_symbol}")
                        st.write(f"Allocation: {entry.allocation_percentage*100:.1f}%")
                        st.write(f"Entry Date: {entry.entry_date}")
                        st.write("---")
                else:
                    st.write("No portfolio entries found.")

            # Add report to portfolio
            st.subheader("Add Latest Report to Portfolio")
            # Fetch all analysts
            with engine.connect() as conn:
                analysts = conn.execute(User.__table__.select().where(User.role == UserRole.ANALYST)).fetchall()
            analyst_options = {f"{a.username} (ID: {a.id})": a.id for a in analysts}
            selected_analyst = st.selectbox("Select Analyst", list(analyst_options.keys()))
            selected_analyst_id = analyst_options[selected_analyst] if selected_analyst else None
            # Fetch latest analysis
            with engine.connect() as conn:
                latest_analysis = conn.execute(
                    StockAnalysis.__table__.select().order_by(StockAnalysis.analysis_date.desc())
                ).first()
            if latest_analysis:
                if st.button("Add Latest Report to Portfolio"):
                    with engine.connect() as conn:
                        new_portfolio = Portfolio(
                            investor_id=st.session_state.user['id'],
                            analysis_id=latest_analysis.id,
                            stock_symbol=latest_analysis.stock_symbol,
                            allocation_percentage=latest_analysis.portfolio_allocation,
                            entry_price=latest_analysis.price_at_analysis
                        )
                        conn.execute(Portfolio.__table__.insert(), new_portfolio.__dict__)
                        conn.commit()
                        st.success("Report added to your portfolio!")
            else:
                st.info("No analysis report available to add.")
        else:
            # Analyst view: show assigned investors and their reports
            st.write("Analyst View - Assigned Investors")
            with engine.connect() as conn:
                # Find all portfolios where this analyst's analysis was used
                portfolios = conn.execute(
                    Portfolio.__table__.join(StockAnalysis, Portfolio.analysis_id == StockAnalysis.id)
                    .select()
                    .where(StockAnalysis.analyst_id == st.session_state.user['id'])
                ).fetchall()
                if portfolios:
                    for entry in portfolios:
                        st.write(f"Investor ID: {entry.investor_id}")
                        st.write(f"Symbol: {entry.stock_symbol}")
                        st.write(f"Allocation: {entry.allocation_percentage*100:.1f}%")
                        st.write(f"Entry Date: {entry.entry_date}")
                        st.write("---")
                else:
                    st.write("No assigned investor reports found.")

if __name__ == "__main__":
    if st.session_state.user is None:
        login_page()
    else:
        main_page() 