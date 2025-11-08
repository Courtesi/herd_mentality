-- Initialize market_data table for FastAPI
-- This script runs automatically when MySQL container is first created

CREATE TABLE IF NOT EXISTS market_data (
    ticker VARCHAR(50) NOT NULL PRIMARY KEY,
    data JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
