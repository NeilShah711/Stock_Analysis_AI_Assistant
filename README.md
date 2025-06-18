# Stock Analysis Application

An AI-powered stock analysis platform that leverages the Llama 3 model through Ollama to provide automated stock analysis and portfolio management capabilities. The application serves both analysts and investors with role-specific features.

## Features

### For Analysts
- Real-time stock data analysis using Yahoo Finance API
- AI-powered report generation using Llama 3
- Technical indicator computation
- Report management and assignment system
- Track report history and assignments

### For Investors
- Portfolio management
- Access to assigned reports
- Analysis history tracking
- Stock performance monitoring

## Technical Stack
- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: SQLite (via SQLAlchemy ORM)
- **AI Model**: Llama 3 (via Ollama)
- **Stock Data**: Yahoo Finance API (yfinance)
- **Authentication**: Custom JWT-based system

## Prerequisites
- Python 3.8 or higher
- Ollama with Llama 3 model installed
- Internet connection for stock data fetching

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd stock-analysis-app
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
SECRET_KEY=your_secret_key_here
```

5. Initialize the database:
```bash
python init_db.py
```

## Running the Application

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Access the application at `http://localhost:8501`

## Usage

### Analyst Role
1. Log in with analyst credentials
2. Enter a stock symbol to analyze
3. View real-time stock data and technical indicators
4. Generate AI-powered analysis reports
5. Save reports and assign them to investors

### Investor Role
1. Log in with investor credentials
2. Access assigned reports
3. Add reports to portfolio
4. Track analysis history
5. Monitor stock performance

## Project Structure
```
stock-analysis-app/
├── app.py                 # Main Streamlit application
├── models.py             # Database models
├── auth.py              # Authentication utilities
├── stock_analysis.py    # Stock analysis functions
├── database.py          # Database connection and utilities
├── requirements.txt     # Project dependencies
├── .env                # Environment variables

```

## Security Features
- JWT-based authentication
- Role-based access control
- Secure password hashing
- Input validation
- SQL injection prevention

## Future Improvements
1. Advanced Analysis Features
   - Additional technical indicators
   - Custom analysis templates
   - Batch report generation

2. User Experience
   - Enhanced visualization capabilities
   - Mobile responsiveness
   - Real-time notifications

3. Performance Optimization
   - Caching mechanisms
   - Asynchronous data fetching
   - Database optimization

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

*Last updated: [Current Date]*
