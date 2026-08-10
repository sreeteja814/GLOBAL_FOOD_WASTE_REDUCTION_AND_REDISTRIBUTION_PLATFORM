const jwt = require('jsonwebtoken');
const db  = require('../config/db');

module.exports = async (req, res, next) => {
  try {
    const h = req.headers.authorization;
    if (!h?.startsWith('Bearer ')) return res.status(401).json({ error: 'No token' });
    const decoded = jwt.verify(h.split(' ')[1], process.env.JWT_SECRET);
    const [[user]] = await db.query(
      'SELECT id,full_name,email,role,organization,address,phone FROM users WHERE id=? AND is_active=1',
      [decoded.id]
    );
    if (!user) return res.status(401).json({ error: 'User not found' });
    req.user = user;
    next();
  } catch {
    res.status(401).json({ error: 'Invalid token' });
  }
};
