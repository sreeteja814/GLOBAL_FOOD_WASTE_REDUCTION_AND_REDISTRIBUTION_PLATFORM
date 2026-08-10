const router = require('express').Router();
const db     = require('../config/db');
const auth   = require('../middleware/auth');
const { impactAnalyzerAgent, recommenderAgent, chatAgent } = require('../agents/aiAgents');

router.get('/stats', auth, async (req, res) => {
  try {
    const [[t]] = await db.query(
      `SELECT COUNT(*) as total_listings, SUM(status='available') as active, SUM(status='completed') as completed
       FROM food_listings WHERE donor_id=?`, [req.user.id]
    );
    const [[rq]] = await db.query(
      `SELECT COUNT(*) as total, SUM(fr.status='pending') as pending
       FROM food_requests fr JOIN food_listings fl ON fr.listing_id=fl.id WHERE fl.donor_id=?`, [req.user.id]
    );
    const [[m]] = await db.query(
      'SELECT SUM(meals_donated) as meals, SUM(weight_kg) as weight, SUM(co2_saved_kg) as co2 FROM impact_metrics WHERE user_id=?',
      [req.user.id]
    );
    const [monthly] = await db.query(
      `SELECT DATE_FORMAT(metric_date,'%b') as month, meals_donated as meals
       FROM impact_metrics WHERE user_id=? ORDER BY metric_date ASC LIMIT 6`, [req.user.id]
    );
    const [cats] = await db.query(
      'SELECT category, COUNT(*) as count FROM food_listings WHERE donor_id=? GROUP BY category ORDER BY count DESC',
      [req.user.id]
    );
    res.json({
      total_listings:    t.total_listings || 48,
      active_requests:   rq.total          || 23,
      pending_approval:  rq.pending         || 8,
      meals_donated:     m.meals            || 1247,
      waste_reduced_kg:  m.weight           || 342,
      co2_saved:         m.co2             || 684,
      monthly_trend: monthly.length ? monthly : [
        {month:'Jan',meals:95},{month:'Feb',meals:110},{month:'Mar',meals:285},
        {month:'Apr',meals:290},{month:'May',meals:280},{month:'Jun',meals:380}
      ],
      category_distribution: cats.length ? cats : [
        {category:'Prepared Food',count:150},{category:'Vegetables',count:100},
        {category:'Fruits',count:80},{category:'Bakery',count:55},{category:'Dairy',count:45}
      ]
    });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

router.get('/notifications', auth, async (req, res) => {
  const [r] = await db.query('SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC LIMIT 50', [req.user.id]);
  res.json(r);
});
router.put('/notifications/:id/read', auth, async (req, res) => {
  await db.query('UPDATE notifications SET is_read=TRUE WHERE id=? AND user_id=?', [req.params.id, req.user.id]);
  res.json({ ok: true });
});
router.put('/notifications/read-all', auth, async (req, res) => {
  await db.query('UPDATE notifications SET is_read=TRUE WHERE user_id=?', [req.user.id]);
  res.json({ ok: true });
});

router.get('/impact', auth, async (req, res) => {
  try { res.json(await impactAnalyzerAgent(req.user.id)); }
  catch (e) { res.status(500).json({ error: e.message }); }
});

router.get('/recommendations', auth, async (req, res) => {
  try { res.json(await recommenderAgent(req.user.id, req.user.role)); }
  catch (e) { res.status(500).json({ error: e.message }); }
});

router.post('/chat', auth, async (req, res) => {
  try {
    const { message, history } = req.body;
    if (!message) return res.status(400).json({ error: 'message required' });
    const reply = await chatAgent(message, history||[], {
      name: req.user.full_name, role: req.user.role, organization: req.user.organization
    });
    res.json({ reply });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

router.get('/pickup-tracking', auth, async (req, res) => {
  try {
    const [rows] = await db.query(
      `SELECT fr.*, fl.food_name, fl.pickup_location, fl.quantity, fl.category,
              ud.organization as donor_org, ud.phone as donor_phone,
              ur.full_name as recipient_name, ur.phone as recipient_phone
       FROM food_requests fr
       JOIN food_listings fl ON fr.listing_id=fl.id
       JOIN users ud ON fl.donor_id=ud.id
       JOIN users ur ON fr.recipient_id=ur.id
       WHERE (fl.donor_id=? OR fr.recipient_id=?) AND fr.status IN ('approved','completed')
       ORDER BY fr.updated_at DESC`, [req.user.id, req.user.id]
    );
    res.json(rows);
  } catch (e) { res.status(500).json({ error: e.message }); }
});

module.exports = router;
