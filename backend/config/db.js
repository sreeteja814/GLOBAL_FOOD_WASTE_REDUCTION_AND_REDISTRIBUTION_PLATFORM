const mysql = require('mysql2/promise');
require('dotenv').config();

const pool = mysql.createPool({
  host:     process.env.DB_HOST     || 'localhost',
  port:     process.env.DB_PORT     || 3306,
  database: process.env.DB_NAME     || 'foodshare',
  user:     process.env.DB_USER     || 'foodshare_user',
  password: process.env.DB_PASSWORD || 'foodshare_pass_2024',
  waitForConnections: true,
  connectionLimit: 20,
  queueLimit: 0,
  timezone: '+00:00'
});

(async () => {
  try {
    const c = await pool.getConnection();
    console.log('✅ MySQL connected');
    c.release();
  } catch (e) {
    console.error('❌ MySQL error:', e.message);
  }
})();

module.exports = pool;
