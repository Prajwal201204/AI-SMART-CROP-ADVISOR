-- Smart Crop Advisory System - Database Schema
-- Run this file to set up the MySQL database

CREATE DATABASE IF NOT EXISTS smart_crop_db;
USE smart_crop_db;

-- Table to store crop recommendation history
CREATE TABLE IF NOT EXISTS recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nitrogen FLOAT NOT NULL,
    phosphorus FLOAT NOT NULL,
    potassium FLOAT NOT NULL,
    ph FLOAT NOT NULL,
    temperature FLOAT NOT NULL,
    rainfall FLOAT NOT NULL,
    result VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Optional: Insert some sample data
INSERT INTO recommendations (nitrogen, phosphorus, potassium, ph, temperature, rainfall, result)
VALUES
    (90, 42, 43, 6.5, 20.8, 82.0, 'Rice'),
    (85, 58, 41, 7.0, 21.8, 80.5, 'Rice'),
    (60, 55, 44, 6.8, 23.0, 65.0, 'Wheat'),
    (40, 67, 23, 8.0, 25.5, 50.0, 'Maize');
