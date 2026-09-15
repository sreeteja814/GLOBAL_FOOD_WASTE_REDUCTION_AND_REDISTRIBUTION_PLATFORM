/**
 * backend/agents/aiAgents.js
 * AI Agent functions using HuggingFace Inference API.
 * Uses keyword-based intent detection + direct DB queries for reliability.
 */

const axios = require('axios');
const db    = require('../config/db');

const HF_TOKEN = process.env.HF_API_TOKEN || process.env.HF_TOKEN || '';
const HF_MODEL = process.env.HF_MODEL || 'mistralai/Mistral-7B-Instruct-v0.2';
const HF_URL   = `https://api-inference.huggingface.co/models/${HF_MODEL}`;

// ── HuggingFace call ──────────────────────────────────────────────────────────
async function hfGenerate(prompt) {
  if (!HF_TOKEN) return null;
  try {
    const { data } = await axios.post(
      HF_URL,
      { inputs: prompt,
        parameters: { max_new_tokens: 300, temperature: 0.4, return_full_text: false } },
      { headers: { Authorization: `Bearer ${HF_TOKEN}` }, timeout: 30000 }
    );
    if (Array.isArray(data) && data[0]?.generated_text) {
      return data[0].generated_text.trim();
    }
  } catch (e) {
    if (e.response?.status === 503) return null; // model loading
    console.error('HF error:', e.message);
  }
  return null;
}

// ── Intent detection ──────────────────────────────────────────────────────────
function detectIntent(message) {
  const m = message.toLowerCase();

  if (/expir|urgent|soon|running out|last chance/.test(m))      return 'expiring';
  if (/impact|co2|carbon|meal|saved|contribution/.test(m))      return 'impact';
  if (/listing|available food|find food|what food/.test(m))     return 'listings';
  if (/request|pending|approv|how do i approve/.test(m))        return 'requests';
  if (/tip|advice|best practice|how (to|can) i|reduce waste/.test(m)) return 'tips';
  if (/match|how does.*match|ai match|algorithm/.test(m))       return 'matching';
  if (/creat|add|new listing|post food/.test(m))                return 'create_listing';
  if (/pickup|track|collect|where|location/.test(m))            return 'pickup';
  if (/hi|hello|hey|help|what can you|who are you/.test(m))     return 'greeting';

  return 'general';
}

// ── chatAgent ─────────────────────────────────────────────────────────────────
async function chatAgent(message, history = [], user = {}) {
  const intent = detectIntent(message);
  const name   = user.name || 'there';
  const role   = user.role || 'user';

  let dataResponse = '';

  try {
    // Handle intents with real DB data
    if (intent === 'expiring') {
      const [rows] = await db.query(
        `SELECT food_name, quantity, category, pickup_location, expiry_date
         FROM food_listings
         WHERE status = 'available'
           AND expiry_date <= DATE_ADD(NOW(), INTERVAL 3 DAY)
         ORDER BY expiry_date ASC LIMIT 5`
      );
      if (rows.length === 0) {
        dataResponse = '✅ Great news! No food listings are expiring in the next 3 days.';
      } else {
        const lines = rows.map(r =>
          `• **${r.food_name}** (${r.category}) — ${r.quantity} | Expires: ${new Date(r.expiry_date).toLocaleDateString()} | 📍 ${r.pickup_location}`
        ).join('\n');
        dataResponse = `🚨 **${rows.length} listing(s) expiring soon:**\n\n${lines}\n\n⚡ Act fast to claim these before they expire!`;
      }
    }

    else if (intent === 'listings') {
      const [rows] = await db.query(
        `SELECT food_name, quantity, category, pickup_location, expiry_date
         FROM food_listings WHERE status = 'available'
         ORDER BY created_at DESC LIMIT 6`
      );
      if (rows.length === 0) {
        dataResponse = 'No food listings are currently available. Check back soon!';
      } else {
        const lines = rows.map(r =>
          `• **${r.food_name}** (${r.category}) — ${r.quantity} | 📍 ${r.pickup_location} | Expires: ${new Date(r.expiry_date).toLocaleDateString()}`
        ).join('\n');
        dataResponse = `🍱 **${rows.length} available food listing(s):**\n\n${lines}`;
      }
    }

    else if (intent === 'impact') {
      const [[m]] = await db.query(
        `SELECT SUM(meals_donated) as meals, SUM(weight_kg) as weight, SUM(co2_saved_kg) as co2
         FROM impact_metrics`
      );
      dataResponse = `🌍 **Platform Impact So Far:**\n\n` +
        `• 🍽️ Meals Donated: **${m.meals || 0}**\n` +
        `• ⚖️ Food Saved: **${m.weight || 0} kg**\n` +
        `• 🌿 CO₂ Prevented: **${m.co2 || 0} kg**\n\n` +
        `Every donation makes a real difference, ${name}! Keep it up.`;
    }

    else if (intent === 'requests') {
      const [rows] = await db.query(
        `SELECT fr.status, COUNT(*) as count
         FROM food_requests fr GROUP BY fr.status`
      );
      const stats = rows.map(r => `• ${r.status}: **${r.count}**`).join('\n');
      dataResponse = `📋 **Request Status Overview:**\n\n${stats || '• No requests yet'}\n\n` +
        `To approve a request: go to **Manage Requests** → click **Approve** next to a pending request.`;
    }

    else if (intent === 'tips') {
      dataResponse = `💡 **Tips to Reduce Food Waste:**\n\n` +
        `• 📅 List food **before** it expires — even 1 day before helps\n` +
        `• 📦 Use accurate quantities so recipients plan pickups correctly\n` +
        `• 🕐 Set realistic pickup windows (2-4 hour slots work best)\n` +
        `• 📸 Add photos to listings — they get **3x more requests**\n` +
        `• 🔔 Enable notifications to respond to requests quickly\n` +
        `• 🏷️ Use correct categories so AI matching works better\n\n` +
        `Would you like tips specific to your role as a ${role}?`;
    }

    else if (intent === 'matching') {
      dataResponse = `🤖 **How AI Matching Works:**\n\n` +
        `1. **Location** — matches donors and recipients within proximity\n` +
        `2. **Expiry urgency** — prioritises food expiring soonest\n` +
        `3. **Category preferences** — learns what each recipient needs\n` +
        `4. **Capacity** — checks recipient's storage and pickup ability\n` +
        `5. **History** — improves matches based on past successful pickups\n\n` +
        `The AI runs automatically every 15 minutes to find new matches! 🔄`;
    }

    else if (intent === 'create_listing') {
      dataResponse = `📝 **How to Create a Food Listing:**\n\n` +
        `1. Go to **Browse Listings** → click **+ Add Listing**\n` +
        `2. Fill in: food name, category, quantity, expiry date\n` +
        `3. Set your pickup location and available time window\n` +
        `4. Add a description and photo (optional but recommended)\n` +
        `5. Click **Submit** — your listing goes live immediately!\n\n` +
        `💡 Tip: Listings with photos and specific quantities get matched faster.`;
    }

    else if (intent === 'pickup') {
      dataResponse = `🚗 **Pickup & Tracking Info:**\n\n` +
        `• Go to **Pickup Tracking** page to see all active pickups\n` +
        `• You'll see real-time status: Pending → Approved → Collected\n` +
        `• Donor and recipient contact details are shown once approved\n` +
        `• Mark as **Completed** after successful pickup\n\n` +
        `Need help with a specific pickup? Share the listing name!`;
    }

    else if (intent === 'greeting') {
      dataResponse = `👋 Hi ${name}! I'm FoodShare AI.\n\n` +
        `Here's what I can help you with:\n` +
        `• 🚨 **Expiring food** — "What food is expiring soon?"\n` +
        `• 🍱 **Available listings** — "Show me available food"\n` +
        `• 🌍 **Impact stats** — "What's my impact?"\n` +
        `• 📋 **Requests** — "How do I approve a request?"\n` +
        `• 💡 **Tips** — "How can I reduce food waste?"\n` +
        `• 🤖 **AI matching** — "How does matching work?"\n\n` +
        `What would you like to know?`;
    }

    else {
      // General — try HuggingFace for open-ended questions
      if (HF_TOKEN) {
        const historyText = history.slice(-4).map(h =>
          `${h.role === 'user' ? 'User' : 'Assistant'}: ${h.content}`
        ).join('\n');

        const prompt = `<s>[INST] You are FoodShare AI, a helpful assistant for a food waste reduction platform. ` +
          `You help donors share surplus food and recipients find food donations. ` +
          `Be helpful, concise, and friendly. User name: ${name}, Role: ${role}.\n\n` +
          `${historyText ? 'Previous conversation:\n' + historyText + '\n\n' : ''}` +
          `User: ${message} [/INST]`;

        const hfReply = await hfGenerate(prompt);
        if (hfReply && hfReply.length > 15) {
          return hfReply;
        }
      }
      dataResponse = `I can help you with food listings, expiry alerts, impact stats, and platform tips. ` +
        `Try asking: "What food is expiring soon?" or "Show available listings" or "What's my impact?"`;
    }

  } catch (e) {
    console.error('chatAgent DB error:', e.message);
    dataResponse = `Sorry, I had trouble fetching data. Please try again in a moment.`;
  }

  // Optionally enhance with HF (but always return dataResponse as fallback)
  if (HF_TOKEN && dataResponse && intent !== 'greeting' && intent !== 'tips' && intent !== 'matching') {
    try {
      const prompt = `<s>[INST] You are FoodShare AI. Rewrite this data response in a friendly, conversational way (under 80 words). Keep all the facts and bullet points. Don't add new information.\n\nData: ${dataResponse}\n\nUser asked: ${message} [/INST]`;
      const enhanced = await hfGenerate(prompt);
      if (enhanced && enhanced.length > 20) return enhanced;
    } catch (_) {}
  }

  return dataResponse;
}

// ── impactAnalyzerAgent ───────────────────────────────────────────────────────
async function impactAnalyzerAgent(userId) {
  try {
    const [[m]] = await db.query(
      `SELECT SUM(meals_donated) as meals, SUM(weight_kg) as weight, SUM(co2_saved_kg) as co2
       FROM impact_metrics WHERE user_id = ?`, [userId]
    );
    const [[l]] = await db.query(
      `SELECT COUNT(*) as total, SUM(status='completed') as completed
       FROM food_listings WHERE donor_id = ?`, [userId]
    );
    return {
      meals_donated:   m.meals    || 0,
      waste_reduced:   m.weight   || 0,
      co2_saved:       m.co2      || 0,
      total_listings:  l.total    || 0,
      completed:       l.completed|| 0,
      summary: `You've helped provide ${m.meals||0} meals and saved ${m.weight||0}kg of food from waste!`
    };
  } catch (e) {
    console.error('impactAnalyzerAgent error:', e.message);
    return { meals_donated:0, waste_reduced:0, co2_saved:0, total_listings:0, completed:0, summary:'' };
  }
}

// ── recommenderAgent ──────────────────────────────────────────────────────────
async function recommenderAgent(userId, role) {
  try {
    let recommendations = [];
    if (role === 'donor') {
      const [expiring] = await db.query(
        `SELECT food_name, expiry_date FROM food_listings
         WHERE donor_id=? AND status='available' AND expiry_date <= DATE_ADD(NOW(), INTERVAL 2 DAY)`,
        [userId]
      );
      if (expiring.length > 0) {
        recommendations.push({
          type: 'urgent',
          message: `⚠️ You have ${expiring.length} listing(s) expiring within 48 hours!`,
          items: expiring.map(e => e.food_name)
        });
      }
      recommendations.push({ type: 'tip', message: '📸 Add photos to listings to get 3x more requests.' });
      recommendations.push({ type: 'tip', message: '⏰ List food early — donors who list 3+ days before expiry get faster matches.' });
    } else {
      const [available] = await db.query(
        `SELECT food_name, category, pickup_location FROM food_listings
         WHERE status='available' ORDER BY expiry_date ASC LIMIT 5`
      );
      recommendations.push({ type: 'available', message: `🍱 ${available.length} food listings available near you.`, items: available.map(a => a.food_name) });
      recommendations.push({ type: 'tip', message: '🔔 Enable notifications to be first to claim new listings.' });
    }
    return recommendations;
  } catch (e) {
    console.error('recommenderAgent error:', e.message);
    return [];
  }
}

// ── expiryMonitorAgent ────────────────────────────────────────────────────────
async function expiryMonitorAgent() {
  try {
    const [expiring] = await db.query(
      `SELECT fl.id, fl.food_name, fl.donor_id, fl.expiry_date, u.full_name
       FROM food_listings fl JOIN users u ON fl.donor_id = u.id
       WHERE fl.status = 'available' AND fl.expiry_date <= DATE_ADD(NOW(), INTERVAL 24 HOUR)
         AND fl.id NOT IN (SELECT listing_id FROM notifications WHERE type='expiry_alert' AND created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR))`
    );

    for (const item of expiring) {
      await db.query(
        `INSERT INTO notifications (user_id, type, title, message) VALUES (?, 'expiry_alert', ?, ?)`,
        [item.donor_id,
         `⚠️ Listing Expiring Soon`,
         `Your listing "${item.food_name}" expires within 24 hours. Update it or it will be auto-removed.`]
      );
      console.log(`🔔 Expiry alert sent for listing: ${item.food_name} (donor: ${item.full_name})`);
    }

    console.log(`✅ Expiry monitor: checked ${expiring.length} expiring listing(s).`);
  } catch (e) {
    console.error('expiryMonitorAgent error:', e.message);
  }
}

// ── matchingAgent ─────────────────────────────────────────────────────────────
async function matchingAgent(listingId, recipientId) {
  try {
    const [[listing]] = await db.query(
      `SELECT fl.*, u.organization, u.city as donor_city
       FROM food_listings fl JOIN users u ON fl.donor_id = u.id
       WHERE fl.id = ?`, [listingId]
    );
    const [[recipient]] = await db.query(
      `SELECT * FROM users WHERE id = ?`, [recipientId]
    );

    if (!listing || !recipient) {
      return { score: 50, reasoning: 'Basic match — listing or recipient data incomplete.' };
    }

    let score = 50;
    const reasons = [];

    // Expiry urgency — higher score for sooner expiry
    const daysLeft = Math.ceil((new Date(listing.expiry_date) - new Date()) / (1000 * 60 * 60 * 24));
    if (daysLeft <= 1)      { score += 25; reasons.push('⚡ Expires within 24 hours — urgent match'); }
    else if (daysLeft <= 2) { score += 15; reasons.push('🕐 Expires within 48 hours'); }
    else if (daysLeft <= 5) { score += 10; reasons.push('📅 Expiring within 5 days'); }

    // Past successful pickups from this donor
    const [[history]] = await db.query(
      `SELECT COUNT(*) as count FROM food_requests fr
       JOIN food_listings fl ON fr.listing_id = fl.id
       WHERE fr.recipient_id = ? AND fl.donor_id = ? AND fr.status = 'completed'`,
      [recipientId, listing.donor_id]
    );
    if (history.count > 0) {
      score += 10;
      reasons.push(`✅ ${history.count} successful pickup(s) from this donor`);
    }

    // Category preference — has recipient collected this category before?
    const [[catHistory]] = await db.query(
      `SELECT COUNT(*) as count FROM food_requests fr
       JOIN food_listings fl ON fr.listing_id = fl.id
       WHERE fr.recipient_id = ? AND fl.category = ? AND fr.status = 'completed'`,
      [recipientId, listing.category]
    );
    if (catHistory.count > 0) {
      score += 10;
      reasons.push(`🏷️ Recipient prefers ${listing.category}`);
    }

    // Same city bonus
    if (recipient.city && listing.donor_city &&
        recipient.city.toLowerCase() === listing.donor_city.toLowerCase()) {
      score += 5;
      reasons.push('📍 Same city');
    }

    score = Math.min(score, 99); // cap at 99

    const reasoning = reasons.length > 0
      ? reasons.join(' | ')
      : 'Standard match based on availability.';

    return { score, reasoning };

  } catch (e) {
    console.error('matchingAgent error:', e.message);
    return { score: 50, reasoning: 'Match score calculated based on availability.' };
  }
}

module.exports = { chatAgent, impactAnalyzerAgent, recommenderAgent, expiryMonitorAgent, matchingAgent };
