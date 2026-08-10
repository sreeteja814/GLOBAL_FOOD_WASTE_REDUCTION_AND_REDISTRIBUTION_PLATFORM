const router  = require('express').Router();
const bcrypt  = require('bcryptjs');
const jwt     = require('jsonwebtoken');
const db      = require('../config/db');
const auth    = require('../middleware/auth');

router.post('/register', async (req, res) => {
  try {
    const { full_name, email, password, phone, organization, address, role } = req.body;
    if (!full_name || !email || !password) return res.status(400).json({ error: 'Name, email and password required' });
    const [ex] = await db.query('SELECT id FROM users WHERE email=?', [email]);
    if (ex.length) return res.status(409).json({ error: 'Email already registered' });
    const hash = await bcrypt.hash(password, 10);
    const [r] = await db.query(
      'INSERT INTO users (full_name,email,password_hash,phone,organization,address,role) VALUES (?,?,?,?,?,?,?)',
      [full_name, email, hash, phone||null, organization||null, address||null, role||'donor']
    );
    const token = jwt.sign({ id: r.insertId }, process.env.JWT_SECRET, { expiresIn: process.env.JWT_EXPIRES_IN });
    res.status(201).json({ token, user: { id: r.insertId, full_name, email, role: role||'donor', organization } });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    if (!email || !password) return res.status(400).json({ error: 'Email and password required' });
    const [rows] = await db.query('SELECT * FROM users WHERE email=? AND is_active=1', [email]);
    if (!rows.length) return res.status(401).json({ error: 'Invalid credentials' });
    const user = rows[0];
    if (!await bcrypt.compare(password, user.password_hash)) return res.status(401).json({ error: 'Invalid credentials' });
    const token = jwt.sign({ id: user.id }, process.env.JWT_SECRET, { expiresIn: process.env.JWT_EXPIRES_IN });
    res.json({ token, user: { id: user.id, full_name: user.full_name, email: user.email, role: user.role, organization: user.organization, address: user.address, phone: user.phone, bio: user.bio } });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

router.get('/me', auth, async (req, res) => {
  const [r] = await db.query('SELECT id,full_name,email,phone,organization,address,bio,role,created_at FROM users WHERE id=?', [req.user.id]);
  res.json(r[0]);
});

router.put('/profile', auth, async (req, res) => {
  try {
    const { full_name, phone, organization, address, bio } = req.body;
    await db.query('UPDATE users SET full_name=?,phone=?,organization=?,address=?,bio=? WHERE id=?',
      [full_name, phone, organization, address, bio, req.user.id]);
    res.json({ message: 'Profile updated' });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

module.exports = router;
