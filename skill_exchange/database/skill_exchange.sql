CREATE DATABASE IF NOT EXISTS skill_exchange;

USE skill_exchange;


-- =========================================================
-- USERS TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS users (

    id INT AUTO_INCREMENT PRIMARY KEY,

    full_name VARCHAR(100) NOT NULL,

    username VARCHAR(50) NOT NULL UNIQUE,

    email VARCHAR(120) NOT NULL UNIQUE,

    password VARCHAR(255) NOT NULL,

    bio TEXT,

    location VARCHAR(100),

    education VARCHAR(150),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


-- =========================================================
-- SKILLS TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS skills (

    id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(100) NOT NULL UNIQUE,

    category VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


-- =========================================================
-- USER SKILLS TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS user_skills (

    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    skill_id INT NOT NULL,

    skill_type ENUM('teach', 'learn') NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (skill_id)
        REFERENCES skills(id)
        ON DELETE CASCADE,

    UNIQUE(user_id, skill_id, skill_type)

);


-- =========================================================
-- SKILL REQUESTS
-- =========================================================

CREATE TABLE IF NOT EXISTS skill_requests (

    id INT AUTO_INCREMENT PRIMARY KEY,

    sender_id INT NOT NULL,

    receiver_id INT NOT NULL,

    skill_id INT,

    message TEXT,

    status ENUM(
        'pending',
        'accepted',
        'rejected'
    ) DEFAULT 'pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (sender_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (receiver_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (skill_id)
        REFERENCES skills(id)
        ON DELETE SET NULL

);


-- =========================================================
-- CONNECTIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS connections (

    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    connected_user_id INT NOT NULL,

    status ENUM(
        'pending',
        'accepted',
        'rejected'
    ) DEFAULT 'pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (connected_user_id)
        REFERENCES users(id)
        ON DELETE CASCADE

);


-- =========================================================
-- NOTIFICATIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS notifications (

    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    title VARCHAR(150),

    message TEXT,

    notification_type VARCHAR(50),

    is_read BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE

);


-- =========================================================
-- CHAT MESSAGES
-- =========================================================

CREATE TABLE IF NOT EXISTS messages (

    id INT AUTO_INCREMENT PRIMARY KEY,

    sender_id INT NOT NULL,

    receiver_id INT NOT NULL,

    message TEXT NOT NULL,

    is_read BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (sender_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (receiver_id)
        REFERENCES users(id)
        ON DELETE CASCADE

);


-- =========================================================
-- REVIEWS
-- =========================================================

CREATE TABLE IF NOT EXISTS reviews (

    id INT AUTO_INCREMENT PRIMARY KEY,

    reviewer_id INT NOT NULL,

    reviewed_user_id INT NOT NULL,

    rating INT NOT NULL,

    review TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (reviewer_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (reviewed_user_id)
        REFERENCES users(id)
        ON DELETE CASCADE

);


-- =========================================================
-- BADGES
-- =========================================================

CREATE TABLE IF NOT EXISTS badges (

    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    name VARCHAR(100) NOT NULL,

    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE

);


-- =========================================================
-- DEFAULT SKILLS
-- =========================================================

INSERT IGNORE INTO skills
(name, category)
VALUES

('Python', 'Programming'),

('Java', 'Programming'),

('JavaScript', 'Programming'),

('C', 'Programming'),

('C++', 'Programming'),

('HTML', 'Web Development'),

('CSS', 'Web Development'),

('React', 'Web Development'),

('Node.js', 'Web Development'),

('Flask', 'Web Development'),

('Django', 'Web Development'),

('MySQL', 'Database'),

('MongoDB', 'Database'),

('Git', 'Tools'),

('GitHub', 'Tools'),

('Machine Learning', 'AI & ML'),

('Artificial Intelligence', 'AI & ML'),

('Deep Learning', 'AI & ML'),

('Data Science', 'Data'),

('Communication', 'Soft Skills'),

('Public Speaking', 'Soft Skills'),

('English', 'Languages'),

('Telugu', 'Languages');


-- =========================================================
-- SAMPLE BADGES
-- =========================================================

-- Badges actual users ki later activity base chesi
-- automatically assign cheyyachu.