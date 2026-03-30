-- Migration: Create masking_modes table for global per-role masking
-- Date: 2026-03-30
-- Description: Adds masking_modes table and drops deprecated users.masking_mode if present

START TRANSACTION;

-- Drop deprecated column if present (compatible with MySQL < 8)
SET @col_exists := (
        SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'users'
            AND COLUMN_NAME = 'masking_mode'
);
SET @drop_sql := IF(@col_exists > 0, 'ALTER TABLE users DROP COLUMN masking_mode;', 'SELECT "skip drop masking_mode";');
PREPARE stmt FROM @drop_sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Create masking_modes table
CREATE TABLE IF NOT EXISTS masking_modes (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    role VARCHAR(50) NOT NULL COMMENT 'Role name (admin, user)',
    mode VARCHAR(20) NOT NULL DEFAULT 'mask' COMMENT 'mask|shuffle|fake|noise',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_masking_modes_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ensure defaults exist even if table already existed without them
ALTER TABLE masking_modes
    MODIFY created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    MODIFY updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- Seed defaults
INSERT INTO masking_modes (role, mode, created_at, updated_at)
VALUES ('admin', 'mask', NOW(), NOW()), ('user', 'mask', NOW(), NOW())
ON DUPLICATE KEY UPDATE mode = VALUES(mode), updated_at = NOW();

COMMIT;
