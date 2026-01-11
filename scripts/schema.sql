-- ============================================================
-- Signals System - SQLite Database Schema
-- ============================================================
-- This file creates all tables for the signals system database
-- Execute this file to set up a fresh database
--
-- Usage:
--   sqlite3 signals_data/sqlite_db/signals.db < scripts/schema.sql
--   OR in DB Browser: File -> Open SQL -> Execute SQL
-- ============================================================

-- ============================================================
-- Table: tickers
-- Purpose: Store stock ticker symbols and their names
-- ============================================================
CREATE TABLE IF NOT EXISTS tickers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL UNIQUE,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups by ticker symbol
CREATE INDEX IF NOT EXISTS idx_tickers_ticker ON tickers(ticker);

-- ============================================================
-- Table: configuration
-- Purpose: Store system configuration key-value pairs
-- ============================================================
CREATE TABLE IF NOT EXISTS configuration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT,
    config_key TEXT NOT NULL UNIQUE,
    config_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups by config key
CREATE INDEX IF NOT EXISTS idx_configuration_key ON configuration(config_key);

-- ============================================================
-- Verification Queries (commented out - uncomment to run)
-- ============================================================

-- Check if tables were created successfully
-- SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;

-- View tickers table structure
-- PRAGMA table_info(tickers);

-- View configuration table structure
-- PRAGMA table_info(configuration);

-- ============================================================
-- Sample Data (commented out - uncomment to insert)
-- ============================================================

-- Sample tickers
INSERT OR IGNORE INTO tickers (ticker, name) VALUES 
    ('RELIANCE', 'Reliance Industries Limited'),
    ('TCS', 'Tata Consultancy Services Limited'),
    ('HDFCBANK', 'HDFC Bank Limited'),
    ('INFY', 'Infosys Limited'),
    ('ICICIBANK', 'ICICI Bank Limited');

-- Sample configuration
-- INSERT OR IGNORE INTO configuration (description, config_key, config_value) VALUES 
--     ('Starting capital for backtesting', 'capital.start', '100000'),
--     ('Maximum capital limit', 'capital.max', '200000'),
--     ('Risk per trade percentage', 'risk.per_trade_pct', '1.0'),
--     ('Data source client type', 'data.client_type', 'nse'),
--     ('Path to raw OHLCV data', 'data.raw_path', '../signals_data/raw/ohlc_1d');

-- ============================================================
-- End of Schema
-- ============================================================
