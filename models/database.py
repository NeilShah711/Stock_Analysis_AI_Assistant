from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

Base = declarative_base()

class UserRole(enum.Enum):
    ANALYST = "analyst"
    INVESTOR = "investor"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analyst_reports = relationship("StockAnalysis", back_populates="analyst")
    investor_portfolios = relationship("Portfolio", back_populates="investor")

class StockAnalysis(Base):
    __tablename__ = "stock_analyses"
    
    id = Column(Integer, primary_key=True)
    analyst_id = Column(Integer, ForeignKey("users.id"))
    stock_symbol = Column(String(10), nullable=False)
    analysis_date = Column(DateTime, default=datetime.utcnow)
    technical_indicators = Column(Text)  # JSON string of technical indicators
    recommendation = Column(String(50))  # Buy, Sell, Hold
    portfolio_allocation = Column(Float)  # Recommended portfolio percentage
    analysis_text = Column(Text)  # Detailed analysis
    price_at_analysis = Column(Float)
    
    # Relationships
    analyst = relationship("User", back_populates="analyst_reports")
    portfolio_entries = relationship("Portfolio", back_populates="analysis")

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True)
    investor_id = Column(Integer, ForeignKey("users.id"))
    analysis_id = Column(Integer, ForeignKey("stock_analyses.id"))
    stock_symbol = Column(String(10), nullable=False)
    allocation_percentage = Column(Float)
    entry_date = Column(DateTime, default=datetime.utcnow)
    exit_date = Column(DateTime, nullable=True)
    entry_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    
    # Relationships
    investor = relationship("User", back_populates="investor_portfolios")
    analysis = relationship("StockAnalysis", back_populates="portfolio_entries")

def init_db(database_url):
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine 