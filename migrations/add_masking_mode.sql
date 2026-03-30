-- Migration: Add masking_mode column to users table
-- Date: 2026-03-29
-- Description: Add data masking mode preference per user (mask, shuffle, fake, noise)

ALTER TABLE users ADD COLUMN masking_mode VARCHAR(20) DEFAULT 'mask' COMMENT 'Data masking mode (mask, shuffle, fake, noise)';

-- Create index for performance
CREATE INDEX idx_masking_mode ON users(masking_mode);
