-- ============================================================
--  MySQL Workbench Setup Script
--  Stock ROCE Predictor — Database & Table
--  v1.1 — Run this ONCE before starting the app
-- ============================================================

-- Step 1: Create the database
CREATE DATABASE IF NOT EXISTS stock_predictor
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE stock_predictor;

-- Step 2: Create predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    company_name            VARCHAR(255)    DEFAULT 'Manual Entry',
    ticker                  VARCHAR(50)     DEFAULT NULL,

    -- Input features
    current_market_price    FLOAT           NOT NULL,
    price_to_earning        FLOAT           NOT NULL,
    market_cap              FLOAT           NOT NULL,
    dividend_yield          FLOAT           NOT NULL,
    net_profit_quarter      FLOAT           NOT NULL,
    yoy_profit_growth       FLOAT           NOT NULL,
    sales_latest_quarter    FLOAT           NOT NULL,
    yoy_sales_growth        FLOAT           NOT NULL,

    -- Prediction output
    predicted_roce          FLOAT           NOT NULL,
    interpretation          VARCHAR(100)    NOT NULL,
    color                   VARCHAR(20)     NOT NULL,

    -- Metadata
    source                  VARCHAR(50)     DEFAULT 'manual',
    created_at              DATETIME        DEFAULT CURRENT_TIMESTAMP,

    -- Indexes for fast dashboard queries
    INDEX idx_created_at    (created_at),
    INDEX idx_color         (color),
    INDEX idx_company       (company_name),
    INDEX idx_ticker        (ticker)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Step 3: Verify setup
SHOW TABLES;
DESCRIBE predictions;

SELECT 'Setup complete! stock_predictor database and predictions table are ready.' AS status;

-- ── Optional: create a dedicated app user (recommended for production) ────────
-- CREATE USER IF NOT EXISTS 'roce_app'@'localhost' IDENTIFIED BY 'StrongPass123!';
-- GRANT SELECT, INSERT, DELETE ON stock_predictor.* TO 'roce_app'@'localhost';
-- FLUSH PRIVILEGES;

-- ── Useful monitoring queries ─────────────────────────────────────────────────

-- All recent predictions
-- SELECT * FROM predictions ORDER BY created_at DESC LIMIT 50;

-- Category summary
-- SELECT color, COUNT(*) AS count, ROUND(AVG(predicted_roce), 2) AS avg_roce
-- FROM predictions GROUP BY color ORDER BY avg_roce DESC;

-- Daily summary
-- SELECT DATE(created_at) AS date, COUNT(*) AS predictions, ROUND(AVG(predicted_roce), 2) AS avg_roce
-- FROM predictions GROUP BY DATE(created_at) ORDER BY date DESC;

-- Top 10 companies by predicted ROCE
-- SELECT company_name, ticker, ROUND(predicted_roce, 2) AS roce, interpretation, created_at
-- FROM predictions ORDER BY predicted_roce DESC LIMIT 10;

-- Delete all records (reset dashboard)
-- TRUNCATE TABLE predictions;
