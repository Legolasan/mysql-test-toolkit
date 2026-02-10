-- Create test database and initial schema
CREATE DATABASE IF NOT EXISTS testdb;
USE testdb;

-- Users table for testing
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    status ENUM('active', 'inactive', 'pending') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Seed with initial records
INSERT INTO users (name, email, status) VALUES
    ('Alice Johnson', 'alice@example.com', 'active'),
    ('Bob Smith', 'bob@example.com', 'active'),
    ('Charlie Brown', 'charlie@example.com', 'pending'),
    ('Diana Prince', 'diana@example.com', 'active'),
    ('Eve Wilson', 'eve@example.com', 'inactive');

-- Create backup directory marker
CREATE TABLE _toolkit_meta (
    key_name VARCHAR(50) PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO _toolkit_meta (key_name, value) VALUES ('version', '1.0.0');

-- Create ETL/CDC user with replication permissions
CREATE USER IF NOT EXISTS 'hevo'@'%' IDENTIFIED WITH mysql_native_password BY 'hevopassword';
GRANT ALL PRIVILEGES ON testdb.* TO 'hevo'@'%';
GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'hevo'@'%';
FLUSH PRIVILEGES;
