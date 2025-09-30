-- Create Database
CREATE DATABASE smartlocker;
USE smartlocker;

-- ========================
-- 1) User Table
-- ========================
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================
-- 2) Admin Table
-- ========================
CREATE TABLE admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE
);

-- ========================
-- 3) Lock Log Table
-- ========================
CREATE TABLE lock_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    access_type ENUM('SUCCESS', 'FAIL') NOT NULL,
    access_date DATE NOT NULL,
    access_time TIME NOT NULL
);
