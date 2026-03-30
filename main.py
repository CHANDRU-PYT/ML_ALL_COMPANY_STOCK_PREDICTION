"""
================================================
  FastAPI Backend — Stock Return Predictor
  v3.2 — Bug fixed: model key mismatch resolved
================================================
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import pandas as pd
import pickle, os, datetime

# ══════════════════════════════════════════════════════════════
#  STEP 1 ► SET YOUR MYSQL PASSWORD HERE (only line you change)
# ══════════════════════════════════════════════════════════════
MYSQL_PASSWORD = "Chandru@1234"         # ← PUT YOUR MySQL Workbench PASSWORD HERE
#                                  (leave as "" if you have no password)
# ══════════════════════════════════════════════════════════════

# ── Optional: override via .env file ──────────────────────────────────────────
_env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_file):
    for _line in open(_env_file):
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

# ── MySQL config (reads .env / environment first, then falls back to above) ───
DB_CONFIG = {
    "host":     os.getenv("MYSQL_HOST",     "localhost"),
    "port":     int(os.getenv("MYSQL_PORT", "3306")),
    "user":     os.getenv("MYSQL_USER",     "root"),
    "password": os.getenv("MYSQL_PASSWORD", MYSQL_PASSWORD),
    "database": os.getenv("MYSQL_DATABASE", "stock_predictor"),
    "connection_timeout": 5,
}

# ── Model path ────────────────────────────────────────────────────────────────
def _find_model(filename="pipeline.pkl"):
    search_dirs = [
        os.path.dirname(os.path.abspath(__file__)),
        os.getcwd(),
        os.path.expanduser("~"),
        os.path.join(os.path.expanduser("~"), "Downloads"),
        os.path.join(os.path.expanduser("~"), "Desktop"),
    ]
    for d in search_dirs:
        p = os.path.join(d, filename)
        if os.path.exists(p):
            return p
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

MODEL_PATH  = os.getenv("MODEL_PATH", _find_model("pipeline.pkl"))

# ── Single consistent key used everywhere ─────────────────────────────────────
MODEL_KEY = "pipeline.pkl"
model_store: dict = {}

# ── DB helpers ────────────────────────────────────────────────────────────────
def get_connection():
    try:
        import mysql.connector
        return mysql.connector.connect(**DB_CONFIG)
    except ImportError:
        raise RuntimeError("mysql-connector-python not installed. Run: pip install mysql-connector-python")

def init_db() -> bool:
    """Create database + table. Returns True on success, False on failure."""
    try:
        import mysql.connector
        from mysql.connector import Error

        # ── Test connection without specifying database ────────────────────────
        cfg_no_db = {k: v for k, v in DB_CONFIG.items() if k != "database"}
        conn = mysql.connector.connect(**cfg_no_db)
        cursor = conn.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`")
        cursor.execute(f"USE `{DB_CONFIG['database']}`")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id                   INT AUTO_INCREMENT PRIMARY KEY,
                company_name         VARCHAR(255) DEFAULT 'Manual Entry',
                ticker               VARCHAR(50)  DEFAULT NULL,
                current_market_price FLOAT,
                price_to_earning     FLOAT,
                market_cap           FLOAT,
                dividend_yield       FLOAT,
                net_profit_quarter   FLOAT,
                yoy_profit_growth    FLOAT,
                sales_latest_quarter FLOAT,
                yoy_sales_growth     FLOAT,
                predicted_roce       FLOAT,
                interpretation       VARCHAR(100),
                color                VARCHAR(20),
                source               VARCHAR(50)  DEFAULT 'manual',
                created_at           DATETIME     DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_created  (created_at),
                INDEX idx_color    (color),
                INDEX idx_company  (company_name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[OK] MySQL connected — host={DB_CONFIG['host']} db={DB_CONFIG['database']}")
        return True

    except ImportError:
        print("[ERROR] mysql-connector-python not installed.")
        print("        Fix: pip install mysql-connector-python")
        return False
    except Exception as e:
        _err = str(e)
        print(f"\n{'='*55}")
        print(f"[MYSQL ERROR] {_err}")
        print(f"{'='*55}")
        # ── Give a specific hint per error type ───────────────────────────────
        if "Access denied" in _err:
            print("► WRONG PASSWORD")
            print(f"  Open main.py and set MYSQL_PASSWORD to your MySQL Workbench password.")
            print(f"  Current password tried: '{DB_CONFIG['password']}'")
            print(f"  Example fix in main.py line ~14:")
            print(f"    MYSQL_PASSWORD = \"YourActualPassword\"")
        elif "Can't connect" in _err or "Connection refused" in _err or "10061" in _err:
            print("► MYSQL SERVER NOT RUNNING")
            print("  Fix: Open MySQL Workbench → Start the local MySQL instance")
            print("  Or open Services (Win+R → services.msc) → Start 'MySQL80'")
        elif "Unknown database" in _err:
            print("► DATABASE DOES NOT EXIST (will be auto-created on next connect)")
        elif "timed out" in _err.lower():
            print("► CONNECTION TIMED OUT — MySQL is unreachable on localhost:3306")
        print(f"{'='*55}\n")
        return False

def save_prediction(row: dict) -> Optional[int]:
    try:
        conn = get_connection()
        conn.database = DB_CONFIG["database"]
        cursor = conn.cursor()
        sql = """
            INSERT INTO predictions (
                company_name, ticker,
                current_market_price, price_to_earning, market_cap,
                dividend_yield, net_profit_quarter, yoy_profit_growth,
                sales_latest_quarter, yoy_sales_growth,
                predicted_roce, interpretation, color, source
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        vals = (
            row.get("company_name", "Manual Entry"), row.get("ticker"),
            row["current_market_price"], row["price_to_earning"],
            row["market_cap"], row["dividend_yield"],
            row["net_profit_quarter"], row["yoy_profit_growth"],
            row["sales_latest_quarter"], row["yoy_sales_growth"],
            row["predicted_roce"], row["interpretation"],
            row["color"], row.get("source", "manual"),
        )
        cursor.execute(sql, vals)
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return new_id
    except Exception as e:
        print(f"[DB SAVE ERROR] {e}")
        return None

# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Load ML model ─────────────────────────────────────────────────────────
    print(f"\n[STARTUP] Looking for model at: {MODEL_PATH}")
    if os.path.exists(MODEL_PATH):
        import joblib
        # FIX: use MODEL_KEY consistently — was "pipeline", now "pipeline.pkl"
        model_store[MODEL_KEY] = joblib.load(MODEL_PATH)
        print(f"[OK] Model loaded — {os.path.getsize(MODEL_PATH):,} bytes")
    else:
        print(f"[ERROR] pipeline.pkl NOT FOUND at {MODEL_PATH}")
        print(f"        Copy pipeline.pkl into: {os.path.dirname(MODEL_PATH)}")

    # ── Connect MySQL ──────────────────────────────────────────────────────────
    print(f"[STARTUP] Connecting to MySQL at {DB_CONFIG['host']}:{DB_CONFIG['port']} "
          f"user={DB_CONFIG['user']} ...")
    model_store["db_ready"] = init_db()
    yield
    model_store.clear()
    print("[SHUTDOWN] Cleared model store.")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Stock Return Predictor API",
    description="Predicts ROCE using ML. Stores results in MySQL.",
    version="3.2.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

PIPELINE_COLS = [
    "Current Market price(Rs)", "Price to Earning",
    "Market Capitilization", "Dividend yield", "Net Profit latest quarter",
    "YOY Quarterly profit Growth", "Sales latest quarter",
    "YOY Quarter sales growth",
]

# ── Schemas ───────────────────────────────────────────────────────────────────
class StockInput(BaseModel):
    company_name         : str            = Field("Manual Entry")
    ticker               : Optional[str] = None
    source               : str            = Field("manual")
    current_market_price : float          = Field(..., alias="Current Market price(Rs)")
    price_to_earning     : float          = Field(..., alias="Price to Earning")
    market_cap           : float          = Field(..., alias="Market Capitilization")
    dividend_yield       : float          = Field(..., alias="Dividend yield")
    net_profit_quarter   : float          = Field(..., alias="Net Profit latest quarter")
    yoy_profit_growth    : float          = Field(..., alias="YOY Quarterly profit Growth")
    sales_latest_quarter : float          = Field(..., alias="Sales latest quarter")
    yoy_sales_growth     : float          = Field(..., alias="YOY Quarter sales growth")
    class Config:
        populate_by_name = True

class PredictRequest(BaseModel):
    inputs: List[StockInput]

# ── Helpers ───────────────────────────────────────────────────────────────────
def interpret(val: float) -> dict:
    if   val > 20: return {"label": "Excellent",     "color": "green"}
    elif val > 10: return {"label": "Good",          "color": "blue"}
    elif val > 5:  return {"label": "Average",       "color": "yellow"}
    else:          return {"label": "Below Average", "color": "red"}

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status":               "ok",
        "model_ready":          MODEL_KEY in model_store,
        "db_ready":             model_store.get("db_ready", True),
        "model_path":           MODEL_PATH,
        "model_exists_on_disk": os.path.exists(MODEL_PATH),
        "db_host":              DB_CONFIG["host"],
        "db_user":              DB_CONFIG["user"],
        "db_name":              DB_CONFIG["database"],
    }

@app.post("/predict")
def predict(req: PredictRequest):
    # FIX: check and access model using the same MODEL_KEY constant
    if MODEL_KEY not in model_store:
        raise HTTPException(503,
            f"Model not loaded. Copy pipeline.pkl to: {os.path.dirname(MODEL_PATH)}")
    rows = []
    for inp in req.inputs:
        rows.append({
            "Current Market price(Rs)":    inp.current_market_price,
            "Price to Earning":            inp.price_to_earning,
            "Market Capitilization":       inp.market_cap,
            "Dividend yield":              inp.dividend_yield,
            "Net Profit latest quarter":   inp.net_profit_quarter,
            "YOY Quarterly profit Growth": inp.yoy_profit_growth,
            "Sales latest quarter":        inp.sales_latest_quarter,
            "YOY Quarter sales growth":    inp.yoy_sales_growth,
        })
    df    = pd.DataFrame(rows, columns=PIPELINE_COLS)
    # FIX: use MODEL_KEY instead of hardcoded "pipeline.pkl"
    preds = model_store[MODEL_KEY].predict(df).tolist()
    results = []
    for i, (val, inp) in enumerate(zip(preds, req.inputs)):
        info = interpret(val)
        db_row = {
            "company_name":         inp.company_name,
            "ticker":               inp.ticker,
            "current_market_price": inp.current_market_price,
            "price_to_earning":     inp.price_to_earning,
            "market_cap":           inp.market_cap,
            "dividend_yield":       inp.dividend_yield,
            "net_profit_quarter":   inp.net_profit_quarter,
            "yoy_profit_growth":    inp.yoy_profit_growth,
            "sales_latest_quarter": inp.sales_latest_quarter,
            "yoy_sales_growth":     inp.yoy_sales_growth,
            "predicted_roce":       round(val, 4),
            "interpretation":       f"{info['label']} ({val:.2f}%)",
            "color":                info["color"],
            "source":               inp.source,
        }
        record_id = save_prediction(db_row) if model_store.get("db_ready") else None
        results.append({
            "index":          i,
            "record_id":      record_id,
            "predicted_ROCE": round(val, 4),
            "interpretation": f"{info['label']} ({val:.2f}%)",
            "color":          info["color"],
        })
    return {"predictions": results, "count": len(results)}

@app.get("/history")
def get_history(limit: int = 100):
    if not model_store.get("db_ready"):
        raise HTTPException(503, "Database not connected.")
    try:
        conn = get_connection()
        conn.database = DB_CONFIG["database"]
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM predictions ORDER BY created_at DESC LIMIT %s", (limit,))
        rows = cursor.fetchall()
        for r in rows:
            if isinstance(r.get("created_at"), datetime.datetime):
                r["created_at"] = r["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        cursor.close()
        conn.close()
        return {"history": rows, "count": len(rows)}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/stats")
def get_stats():
    if not model_store.get("db_ready"):
        raise HTTPException(503, "Database not connected.")
    try:
        conn = get_connection()
        conn.database = DB_CONFIG["database"]
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                COUNT(*)  as total_predictions,
                ROUND(AVG(predicted_roce), 2) as avg_roce,
                ROUND(MAX(predicted_roce), 2) as max_roce,
                ROUND(MIN(predicted_roce), 2) as min_roce,
                SUM(CASE WHEN color='green'  THEN 1 ELSE 0 END) as excellent_count,
                SUM(CASE WHEN color='blue'   THEN 1 ELSE 0 END) as good_count,
                SUM(CASE WHEN color='yellow' THEN 1 ELSE 0 END) as average_count,
                SUM(CASE WHEN color='red'    THEN 1 ELSE 0 END) as below_avg_count
            FROM predictions
        """)
        stats = cursor.fetchone()
        cursor.close()
        conn.close()
        return stats
    except Exception as e:
        raise HTTPException(500, str(e))

@app.delete("/history/{record_id}")
def delete_record(record_id: int):
    if not model_store.get("db_ready"):
        raise HTTPException(503, "Database not connected.")
    try:
        conn = get_connection()
        conn.database = DB_CONFIG["database"]
        cursor = conn.cursor()
        cursor.execute("DELETE FROM predictions WHERE id = %s", (record_id,))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        if affected == 0:
            raise HTTPException(404, "Record not found.")
        return {"deleted": True, "id": record_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))
