const router = require('express').Router();
const db     = require('../config/db');
const auth   = require('../middleware/auth');
const { matchingAgent } = require('../agents/aiAgents');

router.post('/', auth, async (req, res) => {
  try {
    const { listing_id, notes } = req.body;
    if (!listing_id) return res.status(400).json({ error: 'listing_id required' });
    const [[listing]] = await db.query("SELECT * FROM food_listings WHERE id=? AND status='available'", [listing_id]);
    if (!listing) return res.status(404).json({ error: 'Listing not available' });
    const [ex] = await db.query(
      "SELECT id FROM food_requests WHERE listing_id=? AND recipient_id=? AND status NOT IN ('rejected','cancelled')",
      [listing_id, req.user.id]
    );
    if (ex.length) return res.status(409).json({ error: 'Already requested' });
    const aiMatch = await matchingAgent(listing_id, req.user.id);
    const [r] = await db.query(
      'INSERT INTO food_requests (listing_id,recipient_id,notes,ai_match_score,ai_reasoning) VALUES (?,?,?,?,?)',
      [listing_id, req.user.id, notes||null, aiMatch.score, aiMatch.reasoning]
    );
    await db.query(
      'INSERT INTO notifications (user_id,title,message,type,related_listing_id,related_request_id) VALUES (?,?,?,?,?,?)',
      [listing.donor_id, '📦 New Food Request',
       `${req.user.full_name} requested "${listing.food_name}". AI Match: ${aiMatch.score}%`,
       'info', listing_id, r.insertId]
    );
    res.status(201).json({ id: r.insertId, ai_match: aiMatch, message: 'Request submitted' });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

router.get('/', auth, async (req, res) => {
  try {
    let rows;
    if (req.user.role === 'donor') {
      [rows] = await db.query(
        `SELECT fr.*, fl.food_name, fl.category, fl.quantity, fl.pickup_location,
                u.full_name as recipient_name, u.organization as recipient_org, u.phone as recipient_phone
         FROM food_requests fr JOIN food_listings fl ON fr.listing_id=fl.id JOIN users u ON fr.recipient_id=u.id
         WHERE fl.donor_id=? ORDER BY fr.created_at DESC`, [req.user.id]
      );
    } else {
      [rows] = await db.query(
        `SELECT fr.*, fl.food_name, fl.category, fl.quantity, fl.pickup_location, fl.expiry_date, fl.expiry_time,
                u.organization as donor_org
         FROM food_requests fr JOIN food_listings fl ON fr.listing_id=fl.id JOIN users u ON fl.donor_id=u.id
         WHERE fr.recipient_id=? ORDER BY fr.created_at DESC`, [req.user.id]
      );
    }
    res.json(rows);
  } catch (e) { res.status(500).json({ error: e.message }); }
});

router.put('/:id/status', auth, async (req, res) => {
  try {
    const { status } = req.body;
    if (!['approved','rejected','completed','cancelled'].includes(status))
      return res.status(400).json({ error: 'Invalid status' });
    const [[r]] = await db.query(
      `SELECT fr.*, fl.donor_id, fl.food_name, fl.id as lid
       FROM food_requests fr JOIN food_listings fl ON fr.listing_id=fl.id WHERE fr.id=?`, [req.params.id]
    );
    if (!r) return res.status(404).json({ error: 'Not found' });
    if (req.user.role === 'donor'     && r.donor_id     !== req.user.id) return res.status(403).json({ error: 'Unauthorized' });
    if (req.user.role === 'recipient' && r.recipient_id !== req.user.id) return res.status(403).json({ error: 'Unauthorized' });
    await db.query('UPDATE food_requests SET status=? WHERE id=?', [status, req.params.id]);
    if (status === 'approved')   await db.query("UPDATE food_listings SET status='requested'  WHERE id=?", [r.lid]);
    if (status === 'completed') {
      await db.query("UPDATE food_listings SET status='completed' WHERE id=?", [r.lid]);
      await db.query('UPDATE food_requests SET pickup_completed_at=NOW() WHERE id=?', [req.params.id]);
    }
    const msgs = { approved: '✅ Your request was approved! Ready for pickup.', rejected: '❌ Your request was not approved.', completed: '🎉 Pickup completed! Thank you.' };
    if (msgs[status]) await db.query(
      'INSERT INTO notifications (user_id,title,message,type) VALUES (?,?,?,?)',
      [r.recipient_id, `Request ${status}`, msgs[status], status==='completed'||status==='approved'?'success':'info']
    );
    res.json({ message: `Request ${status}` });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

module.exports = router;
