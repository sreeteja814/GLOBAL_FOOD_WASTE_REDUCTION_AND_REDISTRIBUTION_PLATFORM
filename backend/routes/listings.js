const router = require('express').Router();
const db     = require('../config/db');
const auth   = require('../middleware/auth');

router.get('/', auth, async (req, res) => {
  try {
    const { category, search, status } = req.query;
    let sql = `SELECT fl.*, u.full_name as donor_name, u.organization as donor_org,
                TIMESTAMPDIFF(MINUTE, NOW(), TIMESTAMP(fl.expiry_date, fl.expiry_time)) as minutes_left
               FROM food_listings fl JOIN users u ON fl.donor_id=u.id WHERE 1=1`;
    const p = [];
    if (status) { sql += ' AND fl.status=?'; p.push(status); }
    else { sql += " AND fl.status='available'"; }
    if (category) { sql += ' AND fl.category=?'; p.push(category); }
    if (search)   { sql += ' AND fl.food_name LIKE ?'; p.push(`%${search}%`); }
    sql += ' ORDER BY fl.is_urgent DESC, fl.created_at DESC';
    const [rows] = await db.query(sql, p);
    res.json(rows);
  } catch (e) { res.status(500).json({ error: e.message }); }
});

router.get('/my/all', auth, async (req, res) => {
  try {
    const [rows] = await db.query(
      `SELECT fl.*, COUNT(fr.id) as request_count,
              TIMESTAMPDIFF(MINUTE, NOW(), TIMESTAMP(fl.expiry_date, fl.expiry_time)) as minutes_left
       FROM food_listings fl LEFT JOIN food_requests fr ON fr.listing_id=fl.id
       WHERE fl.donor_id=? GROUP BY fl.id ORDER BY fl.created_at DESC`, [req.user.id]
    );
    res.json(rows);
  } catch (e) { res.status(500).json({ error: e.message }); }
});

router.get('/:id', auth, async (req, res) => {
  try {
    const [rows] = await db.query(
      `SELECT fl.*, u.full_name as donor_name, u.organization as donor_org, u.phone as donor_phone,
              TIMESTAMPDIFF(MINUTE, NOW(), TIMESTAMP(fl.expiry_date, fl.expiry_time)) as minutes_left
       FROM food_listings fl JOIN users u ON fl.donor_id=u.id WHERE fl.id=?`, [req.params.id]
    );
    if (!rows.length) return res.status(404).json({ error: 'Not found' });
    res.json(rows[0]);
  } catch (e) { res.status(500).json({ error: e.message }); }
});

router.post('/', auth, async (req, res) => {
  try {
    const { food_name, category, quantity, expiry_date, expiry_time, pickup_location, pickup_lat, pickup_lng, additional_details } = req.body;
    if (!food_name || !category || !quantity || !expiry_date || !expiry_time || !pickup_location)
      return res.status(400).json({ error: 'All required fields must be filled' });
    const [r] = await db.query(
      `INSERT INTO food_listings (donor_id,food_name,category,quantity,expiry_date,expiry_time,pickup_location,pickup_lat,pickup_lng,additional_details)
       VALUES (?,?,?,?,?,?,?,?,?,?)`,
      [req.user.id, food_name, category, quantity, expiry_date, expiry_time, pickup_location, pickup_lat||null, pickup_lng||null, additional_details||null]
    );
    res.status(201).json({ id: r.insertId, message: 'Listing created' });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

router.put('/:id', auth, async (req, res) => {
  try {
    const [[row]] = await db.query('SELECT donor_id FROM food_listings WHERE id=?', [req.params.id]);
    if (!row) return res.status(404).json({ error: 'Not found' });
    if (row.donor_id !== req.user.id) return res.status(403).json({ error: 'Unauthorized' });
    const { food_name, category, quantity, expiry_date, expiry_time, pickup_location, additional_details, status } = req.body;
    await db.query(
      `UPDATE food_listings SET food_name=?,category=?,quantity=?,expiry_date=?,expiry_time=?,pickup_location=?,additional_details=?,status=? WHERE id=?`,
      [food_name, category, quantity, expiry_date, expiry_time, pickup_location, additional_details, status, req.params.id]
    );
    res.json({ message: 'Updated' });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

router.delete('/:id', auth, async (req, res) => {
  try {
    const [[row]] = await db.query('SELECT donor_id FROM food_listings WHERE id=?', [req.params.id]);
    if (!row) return res.status(404).json({ error: 'Not found' });
    if (row.donor_id !== req.user.id) return res.status(403).json({ error: 'Unauthorized' });
    await db.query("UPDATE food_listings SET status='cancelled' WHERE id=?", [req.params.id]);
    res.json({ message: 'Cancelled' });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

module.exports = router;
