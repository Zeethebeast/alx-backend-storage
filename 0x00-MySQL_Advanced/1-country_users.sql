-- Alters an existing table
-- Write a SQL script that creates a table users following these requirements:

CREATE TABLE IF NOT EXISTS users(
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) NOT NULL UNIQUE,
        name VARCHAR(255) NOT NULL
);

ALTER TABLE users
ADD COLUMN country ENUM('US', 'CO', 'TN') NOT NULL DEFAULT 'US';