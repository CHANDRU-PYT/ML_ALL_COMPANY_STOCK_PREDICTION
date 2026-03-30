# 📊 Stock ROCE Predictor v3.2

An ML-powered dashboard to predict the **Return on Capital Employed (ROCE)** for Indian listed companies using 8 key financial metrics.

## 🚀 Features

- **Live Tracker**: Fetch real-time financial metrics from Yahoo Finance via ticker symbols (e.g., `RELIANCE.NS`).
- **Manual Entry**: Input metrics manually to see predictions for any scenario.
- **MySQL Integration**: Automatically stores all predictions in a local/remote MySQL database with history tracking.
- **Analytics Dashboard**: Visualize ROCE distribution, top-performing companies, and trends over time.
- **Performance**: Powered by a highly optimized XGBoost model.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **Model**: XGBoost (Scikit-learn pipeline)
- **Database**: MySQL
- **Data Source**: yfinance

## ⚙️ Setup & Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/CHANDRU-PYT/project_sql.git
   cd project_sql
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DATABASE=stock_predictor
   MYSQL_USER=root
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   FASTAPI_URL=http://localhost:8000
   ```

4. **Run the Application**:
   Simply run the reliable launcher:
   ```bash
   python run.py
   ```
   - **FastAPI**: http://localhost:8000/docs
   - **Streamlit**: http://localhost:8501

## 📂 Project Structure

- `app.py`: Streamlit frontend dashboard.
- `main.py`: FastAPI backend and database logic.
- `run.py`: Multi-service launcher.
- `pipeline.pkl`: Trained ML model.
- `diagnose.py`: Automated diagnostic tool to fix common issues.

## ☁️ Deployment

This project is optimized for deployment on **Streamlit Cloud** (Frontend) and **Render/Railway** (Backend). See `deployment_guide.md` for full instructions.

---
*Created by [CHANDRU-PYT](https://github.com/CHANDRU-PYT)*
