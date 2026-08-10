require('dotenv').config();
const express = require('express');
const cors    = require('cors');
const cron    = require('node-cron');
const { expiryMonitorAgent } = require('./agents/aiAgents');

const app  = express();
const PORT = process.env.PORT || 5000;

app.use(cors({ origin: '*', credentials: true }));
app.use(express.json({ limit: '10mb' }));
app.use((req, _, next) => { console.log(`${new Date().toISOString()} ${req.method} ${req.path}`); next(); });

app.use('/api/auth',      require('./routes/auth'));
app.use('/api/listings',  require('./routes/listings'));
app.use('/api/requests',  require('./routes/requests'));
app.use('/api/dashboard', require('./routes/dashboard'));

app.get('/api/health', (_, res) => res.json({ status: 'ok', platform: 'Global Food Waste Reduction and Redistribution Platform' }));
app.use((_, res) => res.status(404).json({ error: 'Not found' }));
app.use((e, _, res, __) => res.status(500).json({ error: e.message }));

// Expiry monitor every 15 minutes
cron.schedule('*/15 * * * *', () => { console.log('🤖 Running Expiry Monitor...'); expiryMonitorAgent(); });

app.listen(PORT, () => {
  console.log(`\n🌍 Global Food Waste Reduction and Redistribution Platform`);
  console.log(`🚀 API running → http://localhost:${PORT}/api/health\n`);
});
