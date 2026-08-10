-- Global Food Waste Reduction and Redistribution Platform
CREATE DATABASE IF NOT EXISTS foodshare;
USE foodshare;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  phone VARCHAR(50),
  organization VARCHAR(255),
  address TEXT,
  bio TEXT,
  role ENUM('donor','recipient','admin') DEFAULT 'donor',
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS food_listings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  donor_id INT NOT NULL,
  food_name VARCHAR(255) NOT NULL,
  category ENUM('Prepared Food','Vegetables','Fruits','Bakery','Dairy','Grains','Beverages','Other') NOT NULL,
  quantity VARCHAR(255) NOT NULL,
  expiry_date DATE NOT NULL,
  expiry_time TIME NOT NULL,
  pickup_location TEXT NOT NULL,
  pickup_lat DECIMAL(10,8),
  pickup_lng DECIMAL(11,8),
  additional_details TEXT,
  status ENUM('available','requested','completed','expired','cancelled') DEFAULT 'available',
  is_urgent BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (donor_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS food_requests (
  id INT AUTO_INCREMENT PRIMARY KEY,
  listing_id INT NOT NULL,
  recipient_id INT NOT NULL,
  status ENUM('pending','approved','rejected','completed','cancelled') DEFAULT 'pending',
  pickup_scheduled_at TIMESTAMP NULL,
  pickup_completed_at TIMESTAMP NULL,
  notes TEXT,
  ai_match_score DECIMAL(5,2),
  ai_reasoning TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (listing_id) REFERENCES food_listings(id) ON DELETE CASCADE,
  FOREIGN KEY (recipient_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notifications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  title VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  type ENUM('info','success','warning','urgent') DEFAULT 'info',
  is_read BOOLEAN DEFAULT FALSE,
  related_listing_id INT,
  related_request_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ai_agent_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  agent_type ENUM('matching','expiry_monitor','impact_analyzer','chat','recommender') NOT NULL,
  action TEXT NOT NULL,
  result TEXT,
  affected_listing_id INT,
  affected_request_id INT,
  metadata JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS impact_metrics (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  metric_date DATE NOT NULL,
  meals_donated INT DEFAULT 0,
  weight_kg DECIMAL(10,2) DEFAULT 0,
  co2_saved_kg DECIMAL(10,2) DEFAULT 0,
  listings_count INT DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- password = demo1234
INSERT IGNORE INTO users (full_name, email, password_hash, phone, organization, address, bio, role) VALUES
('Demo User',   'demo@foodshare.com',  '$2a$10$/6Lwrh8c6.zl5XoIjZn5/e6wHwhCOW.Yc59SPwimUZIizv44Y.E.u', '+1 234 567 8900', 'Green Hotel',            '123 Green Street, Downtown', 'Contributing to reduce food waste and help the community.', 'donor'),
('Alice Chen',  'alice@freshmart.com', '$2a$10$/6Lwrh8c6.zl5XoIjZn5/e6wHwhCOW.Yc59SPwimUZIizv44Y.E.u', '+1 234 567 8901', 'Fresh Mart Supermarket',  '456 Market Avenue',          'Fresh produce donor committed to zero waste.',              'donor'),
('Bob Kitchen', 'bob@citykitchen.com', '$2a$10$/6Lwrh8c6.zl5XoIjZn5/e6wHwhCOW.Yc59SPwimUZIizv44Y.E.u', '+1 234 567 8902', 'City Kitchen Restaurant', '789 Chef Road',              'Restaurant committed to community impact.',                 'donor'),
('Sarah Hope',  'sarah@shelter.org',   '$2a$10$/6Lwrh8c6.zl5XoIjZn5/e6wHwhCOW.Yc59SPwimUZIizv44Y.E.u', '+1 234 567 8903', 'Community Shelter',       '321 Hope Street',            'Helping families in need every day.',                       'recipient');

INSERT IGNORE INTO food_listings (donor_id, food_name, category, quantity, expiry_date, expiry_time, pickup_location, pickup_lat, pickup_lng, additional_details, status, is_urgent) VALUES
(1, 'Rice & Curry',     'Prepared Food', '20 meals',  CURDATE(), ADDTIME(CURTIME(),'02:00:00'), 'Green Hotel, Downtown',       40.7128, -74.0060, 'Freshly prepared, vegetarian friendly',  'available', FALSE),
(2, 'Fresh Vegetables', 'Vegetables',    '30 kg',     DATE_ADD(CURDATE(),INTERVAL 1 DAY), '18:00:00', 'Fresh Mart Supermarket', 40.7580, -73.9855, 'Assorted seasonal vegetables',           'available', FALSE),
(3, 'Vegetable Stew',   'Prepared Food', '15 meals',  CURDATE(), ADDTIME(CURTIME(),'01:00:00'), 'City Kitchen Restaurant',     40.7484, -73.9967, 'Hot stew, needs immediate pickup',        'available', TRUE),
(1, 'Sourdough Bread',  'Bakery',        '25 loaves', CURDATE(), '20:00:00',                    'Green Hotel, Downtown',       40.7128, -74.0060, 'Freshly baked this morning',              'available', FALSE),
(2, 'Mixed Fruits',     'Fruits',        '40 kg',     DATE_ADD(CURDATE(),INTERVAL 2 DAY), '17:00:00', 'Fresh Mart Supermarket', 40.7580, -73.9855, 'Seasonal mix, excellent condition',       'available', FALSE),
(3, 'Pasta Meals',      'Prepared Food', '30 meals',  DATE_ADD(CURDATE(),INTERVAL 1 DAY), '19:00:00', 'City Kitchen Restaurant',  40.7484, -73.9967, 'Italian pasta with tomato sauce',         'available', FALSE);

INSERT IGNORE INTO impact_metrics (user_id, metric_date, meals_donated, weight_kg, co2_saved_kg, listings_count) VALUES
(1, DATE_SUB(CURDATE(),INTERVAL 5 MONTH),  95,  48,  96,  8),
(1, DATE_SUB(CURDATE(),INTERVAL 4 MONTH), 110,  55, 110, 10),
(1, DATE_SUB(CURDATE(),INTERVAL 3 MONTH), 285, 142, 284, 18),
(1, DATE_SUB(CURDATE(),INTERVAL 2 MONTH), 290, 145, 290, 19),
(1, DATE_SUB(CURDATE(),INTERVAL 1 MONTH), 280, 140, 280, 17),
(1, CURDATE(),                             380, 190, 380, 22);

INSERT IGNORE INTO notifications (user_id, title, message, type, is_read) VALUES
(1, 'New Request',       'Sarah Hope requested your Rice & Curry listing.',          'info',    FALSE),
(1, 'Listing Expiring',  'Your Sourdough Bread listing expires in 2 hours!',         'urgent',  FALSE),
(1, 'Request Approved',  'Your food request has been approved. Ready for pickup.',   'success', TRUE),
(1, 'AI Match Found',    'Our AI agent found a 95% match for your surplus food.',    'info',    FALSE);