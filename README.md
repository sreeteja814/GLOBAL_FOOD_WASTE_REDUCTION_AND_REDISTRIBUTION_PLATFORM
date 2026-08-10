# 🌍 Global Food Waste Reduction and Redistribution Platform

Full-stack application with **Streamlit** frontend, **Node.js/Express** backend, **MySQL** database, and **HuggingFace AI** agents.

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.10+
- Node.js 18+
- MySQL 8.0
- HuggingFace account → https://huggingface.co/settings/tokens

---

### Step 1 — MySQL Setup

**Windows (PowerShell):**
```powershell
Get-Content mysql-init/init.sql | mysql -u root -p
```
If `mysql` isn't recognized, either add MySQL's `bin` folder (e.g. `C:\Program Files\MySQL\MySQL Server 8.0\bin`) to your system PATH and restart your terminal, or call it with the full path:
```powershell
Get-Content mysql-init/init.sql | & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p
```

**macOS / Linux:**
```bash
mysql -u root -p < mysql-init/init.sql
```

> `init.sql` uses `INSERT IGNORE`, so it's safe to run multiple times — it won't error on duplicate rows if the database is already seeded.

Or set up the app-specific DB user manually (recommended for production-style setups instead of using `root` everywhere):
```sql
CREATE USER 'foodshare_user'@'localhost' IDENTIFIED BY 'your_own_password_here';
GRANT ALL PRIVILEGES ON foodshare.* TO 'foodshare_user'@'localhost';
FLUSH PRIVILEGES;
SOURCE mysql-init/init.sql;
```
> Pick your own password here and use the same value in `backend/.env` (`DB_PASSWORD`). The example above intentionally does not show a real password — never commit real credentials to a README or to git.

**Windows service note:** if `mysql` connects but you get `ERROR 2003: Can't connect to MySQL server`, the MySQL Windows service isn't running:
```powershell
Get-Service -Name "MySQL80"
Start-Service -Name "MySQL80"   # requires an Administrator PowerShell window
Set-Service -Name "MySQL80" -StartupType Automatic   # so it starts on boot, one-time fix
```

---

### Step 2 — Backend

```bash
cd backend
npm install
```

Edit `backend/.env`:
```env
NODE_ENV=development
PORT=5000

# MySQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=foodshare
DB_USER=foodshare_user
DB_PASSWORD=your_own_password_here

# JWT
JWT_SECRET=change_this_to_a_random_string
JWT_EXPIRES_IN=7d

# HuggingFace (required for backend AI agents — matching, expiry monitor, impact analyzer, recommender)
HF_TOKEN=hf_your_real_token_here

# Frontend
FRONTEND_URL=http://localhost:8501
```

> ⚠️ `HF_TOKEN` is listed as optional in earlier versions of this doc, but the backend AI agents (`backend/agents/aiAgents.js`) call HuggingFace directly and have not been verified to have a working fallback path without it. Set it explicitly rather than relying on "fallback defaults."

```bash
npm start
# or, for auto-restart on file changes during development:
npm run dev

# API runs at http://localhost:5000
# Health check: http://localhost:5000/api/health
```

---

### Step 3 — Frontend (Streamlit)

```bash
cd frontend
python -m venv .venv
```
**Windows:**
```powershell
.\.venv\Scripts\Activate.ps1
```
**macOS / Linux:**
```bash
source .venv/bin/activate
```
```bash
pip install -r requirements.txt
```

Create the secrets file:
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```
Edit `frontend/.streamlit/secrets.toml`:
```toml
[api]
base_url = "http://localhost:5000/api"

[huggingface]
token = "hf_your_real_token_here"
```

> ⚠️ **Important:** Streamlit checks for secrets in TWO locations — a global one (`~/.streamlit/secrets.toml`, i.e. `C:\Users\<you>\.streamlit\secrets.toml` on Windows) and the local project one (`frontend/.streamlit/secrets.toml`). **If both exist, the local one always wins**, even if it only has placeholder values. If your token seems to be "not working" despite being set correctly somewhere, check both locations and make sure the local one has your real token, not the example text (`hf_your_token_here`).

```bash
streamlit run app.py
# Opens at http://localhost:8501
```

If you edit `secrets.toml`, you must fully stop (Ctrl+C) and restart `streamlit run app.py` — secrets are only loaded at startup, not on hot-reload.

---

## 🐳 Docker Compose

```bash
export HF_TOKEN=hf_your_token_here
docker-compose up --build
```

| Service   | URL                       |
|-----------|---------------------------|
| Streamlit | http://localhost:8501     |
| Backend   | http://localhost:5000/api |
| MySQL     | localhost:3306            |

> Not verified against the current codebase as of this revision — confirm `docker-compose.yml` env vars match `backend/.env` and `frontend/.streamlit/secrets.toml` before relying on this path.

---

## 🔐 Demo Login

| Email                  | Password  | Role      |
|------------------------|-----------|-----------|
| demo@foodshare.com     | demo1234  | Donor     |
| alice@freshmart.com    | demo1234  | Donor     |
| bob@citykitchen.com    | demo1234  | Donor     |
| sarah@shelter.org      | demo1234  | Recipient |

Click **⚡ Quick Demo Login** on the login screen.

> These passwords only work if `mysql-init/init.sql` contains real bcrypt hashes of `demo1234`. If the seed file still has the sample hash from the `bcryptjs` documentation (`$2b$10$N9qo8u...`), login will fail with "Invalid credentials" for all demo accounts — that hash is a placeholder, not a real hash of any of these passwords.

---

## 🤖 AI Agents (HuggingFace)

| Agent              | Trigger                    | Function                                      |
|--------------------|----------------------------|-----------------------------------------------|
| Matching Agent     | On every food request      | Scores recipient-listing compatibility 0–100% |
| Expiry Monitor     | Every 15 min (cron)        | Flags urgent listings, sends notifications    |
| Impact Analyzer    | Impact Dashboard page      | Personalized impact summary + badge           |
| Chat Assistant     | AI Chat page               | Conversational food waste expert              |
| Recommender        | Dashboard load             | Personalised next-action suggestions          |
| Match Insight      | Browse Listings (frontend) | Direct HuggingFace call from Streamlit        |
| Waste Analyzer     | Browse Listings (frontend) | Pattern analysis on available food            |

**Model & endpoint:** as of this revision, the Chat Assistant is confirmed working using:
- Endpoint: `https://router.huggingface.co/v1/chat/completions`
- Model: `Qwen/Qwen2.5-7B-Instruct:together` (explicit `model:provider` format)

The `hf-inference` (HuggingFace's own free-tier) provider was **not** available on the account this was tested with — the router returned "not supported by any provider" for every model tried against it. Available providers vary per HuggingFace account; check yours with:
```python
import requests
r = requests.get('https://router.huggingface.co/v1/models', headers={'Authorization': f'Bearer YOUR_TOKEN'})
```
and inspect the `providers` list on any model entry to find one your account can actually reach.

> ⚠️ The `together` provider used above is **not** a free tier by default (pricing is per-token) — it worked during testing on trial credits. Check https://huggingface.co/settings/billing periodically to avoid unexpected charges, and consider swapping to a confirmed-free provider if you plan to run this long-term.

> **Not yet verified:** `backend/agents/aiAgents.js`, `frontend/pages/browse_listings.py`, and `frontend/pages/impact_dashboard.py` may still reference the old model/endpoint pattern (individual legacy model URLs rather than the router) and likely need the same fix applied to `frontend/pages/ai_chat.py` and `frontend/utils/hf_ai.py`.

---

## 📁 Project Structure

```
foodshare/
├── backend/
│   ├── agents/aiAgents.js    # 5 HuggingFace AI agents
│   ├── config/db.js          # MySQL pool
│   ├── middleware/auth.js    # JWT auth
│   ├── routes/               # auth, listings, requests, dashboard
│   ├── server.js             # Express + cron
│   └── .env
├── frontend/
│   ├── app.py                # Main Streamlit entry point + sidebar nav
│   ├── pages/
│   │   ├── login.py          # Login & Register
│   │   ├── dashboard.py      # Stats + charts + AI recommendations
│   │   ├── browse_listings.py
│   │   ├── create_listing.py
│   │   ├── manage_requests.py
│   │   ├── pickup_tracking.py
│   │   ├── impact_dashboard.py
│   │   ├── ai_chat.py        # Chat with HuggingFace-hosted model
│   │   ├── notifications.py
│   │   └── profile.py
│   ├── utils/
│   │   ├── api.py            # HTTP client for backend
│   │   └── hf_ai.py          # Direct HuggingFace calls from frontend
│   ├── .streamlit/
│   │   ├── config.toml       # Theme (green)
│   │   └── secrets.toml.example
│   └── requirements.txt
├── mysql-init/init.sql
├── docker-compose.yml
└── README.md
```

---

## 📡 API Endpoints

| Method | Endpoint                            | Description                  |
|--------|--------------------------------------|-------------------------------|
| POST   | /api/auth/register                  | Register                     |
| POST   | /api/auth/login                     | Login                        |
| GET    | /api/auth/me                        | Current user                 |
| PUT    | /api/auth/profile                   | Update profile               |
| GET    | /api/listings                       | Browse listings              |
| POST   | /api/listings                       | Create listing                |
| GET    | /api/listings/my/all                | My listings                  |
| PUT    | /api/listings/:id                   | Update listing                |
| DELETE | /api/listings/:id                   | Cancel listing                |
| POST   | /api/requests                       | Submit request (AI match)    |
| GET    | /api/requests                       | My requests                  |
| PUT    | /api/requests/:id/status            | Approve/reject/complete      |
| GET    | /api/dashboard/stats                | Dashboard KPIs               |
| GET    | /api/dashboard/notifications        | Notifications                 |
| PUT    | /api/dashboard/notifications/read-all | Mark all read               |
| GET    | /api/dashboard/impact               | AI impact analysis           |
| GET    | /api/dashboard/recommendations      | AI recommendations           |
| POST   | /api/dashboard/chat                 | AI chat (HuggingFace)        |
| GET    | /api/dashboard/pickup-tracking      | Pickup tracking               |

---

## 🛠️ Tech Stack

| Layer      | Technology                           |
|------------|---------------------------------------|
| Frontend   | Streamlit 1.32, Plotly, Pandas        |
| Backend    | Node.js, Express.js                   |
| Database   | MySQL 8.0 + mysql2                    |
| AI         | HuggingFace Inference Providers (router-based, model configurable — see AI Agents section) |
| Auth       | JWT + bcryptjs                        |
| Scheduler  | node-cron (expiry monitor)            |
| DevOps     | Docker + Docker Compose               |

---

## 🌐 UN SDGs Supported
- **SDG 2** — Zero Hunger
- **SDG 12** — Responsible Consumption & Production
- **SDG 13** — Climate Action
- **SDG 17** — Partnerships for the Goals

---

## 🔧 Troubleshooting Notes (from real setup experience)

- **PowerShell `<` redirection error:** use `Get-Content file.sql | mysql ...` instead of `mysql ... < file.sql` on Windows.
- **`mysql` not recognized:** MySQL's `bin` folder isn't on PATH — add it via System Environment Variables, or call `mysql.exe` with its full path.
- **`ERROR 2003: Can't connect to MySQL server`:** the MySQL80 Windows service isn't running — start it via `Start-Service -Name "MySQL80"` (needs an Administrator terminal), and set it to `Automatic` startup so this doesn't recur.
- **`ERROR 1062: Duplicate entry` when re-running `init.sql`:** expected if the database is already seeded and the script uses plain `INSERT INTO`. This repo's `init.sql` has been updated to use `INSERT IGNORE` so it's safe to re-run.
- **Login always fails with "Invalid credentials":** check that `init.sql` has real bcrypt hashes for demo users, not the `bcryptjs` documentation's sample hash.
- **HuggingFace "Invalid username or password":** almost always means the token in the *local* `frontend/.streamlit/secrets.toml` is a placeholder — check that file specifically, since it silently overrides any global secrets file.
- **HuggingFace "model not supported by any provider":** the specific model isn't hosted by any provider enabled on your account. Query `https://router.huggingface.co/v1/models` with your token to see which providers and models you can actually use, and reference the model as `model-name:provider-name`.
