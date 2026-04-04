-- ==================== Setup Database ====================
-- Script để tạo database user_db cho hệ thống

-- Tạo database
CREATE DATABASE
IF NOT EXISTS user_db
CHARACTER
SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Sử dụng database
USE user_db;

-- Kiểm tra xem tables đã tồn tại chưa (nếu rồi thì drop)
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;

-- Tạo bảng roles
CREATE TABLE
IF NOT EXISTS roles
(
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Role ID',
    name VARCHAR
(20) UNIQUE NOT NULL COMMENT 'Role name (admin, user, etc)',
    description VARCHAR
(255) COMMENT 'Role description',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    
    CHARSET utf8mb4,
    COLLATE utf8mb4_unicode_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert mặc định roles
INSERT INTO roles
    (name, description)
VALUES
    ('admin', 'Administrator - full access'),
    ('user', 'Regular user - limited access'),
    ('auditor', 'Can view masked data of all non-admin users');

-- Tạo bảng users
CREATE TABLE
IF NOT EXISTS users
(
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'User ID',
    username VARCHAR
(50) NOT NULL UNIQUE COMMENT 'Username',
    email VARBINARY
(255) NOT NULL COMMENT 'Encrypted email',
    phone VARBINARY
(255) NOT NULL COMMENT 'Encrypted phone number',
    password VARBINARY
(255) NOT NULL COMMENT 'Encrypted password',
    role_id INT NOT NULL DEFAULT 2 COMMENT 'Role ID (foreign key)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON
UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
    
    INDEX idx_username (username),
    CONSTRAINT fk_role
FOREIGN KEY
(role_id) REFERENCES roles
(id),
    
    CHARSET utf8mb4,
    COLLATE utf8mb4_unicode_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Verify table creation
SHOW TABLES;
DESCRIBE users;

-- ==================== Sample Queries ====================

-- SELECT all users
-- SELECT * FROM users;

-- Check table structure
-- SHOW CREATE TABLE users;

-- Delete all users (testing)
-- DELETE FROM users;

-- Drop table (if needed)
-- DROP TABLE users;

-- Drop database (if needed)
-- DROP DATABASE user_db;
