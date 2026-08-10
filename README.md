# Authenticating XYZ — Auth Platform

JWT-based authentication system built with FastAPI, PostgreSQL (Supabase), and JavaScript.


**Repo:** [https://github.com/ivy2320/Authenticatingxyz]

---

## Quick Start

```bash
# Setup
git clone <repo>
cd authenticatingxyz
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your Supabase connection string to .env

# Run locally
# Terminal 1:
uvicorn main:app --reload

# Terminal 2:
cd frontend
python -m http.server 5500

# Open: http://127.0.0.1:5500
```

---

## Features

- **User Registration** — email/password signup with Bcrypt hashing
- **Login/Logout** — JWT access tokens + rotating refresh tokens
- **Protected Routes** — Bearer token verification
- **Rate Limiting** — brute-force protection (10 attempts/min)
- **Token Refresh** — automatic rotation on use
- **HttpOnly Cookies** — secure refresh token storage

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python) |
| Database | PostgreSQL (Supabase) |
| ORM | SQLAlchemy |
| Auth | JWT (PyJWT) + Bcrypt |
| Frontend | HTML/JS (no framework) |

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Login, get tokens |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Logout, revoke token |
| GET | `/auth/me` | Get user (protected) |

---

## Security

✅ **Implemented:**
- Bcrypt password hashing (one-way, salted, slow)
- Short-lived access tokens (15 min, stateless)
- Long-lived refresh tokens (7 days, tracked in DB, rotated on use)
- Generic login errors (no email enumeration)
- Rate limiting (prevent brute-force)
- HttpOnly cookies (XSS protection)
--

## Database

**users table:**
- `id` (UUID)
- `email` (unique)
- `password_hash` (Bcrypt)
- `is_verified` (boolean)
- `created_at`

**refresh_tokens table:**
- `id` (UUID)
- `token_hash` (hashed)
- `user_id` (FK)
- `expires_at`
- `revoked` (boolean)
- `created_at`

---

## Key Design Decisions

**JWT + Refresh Tokens Pattern:**
- Access tokens are **stateless** (fast, no DB lookup) but **can't be revoked**
- Refresh tokens are **stateful** (tracked in DB) so they **can be revoked**
- On refresh: old token marked revoked, new token issued (rotation)
- If token stolen, attacker gets limited use before rotation

**Why Bcrypt over SHA256?**
- Bcrypt is slow (~100ms) — brute-force attacks become impractical
- SHA256 is fast — attackers can try millions of passwords per second
- Bcrypt salts automatically — prevents rainbow table attacks

---

## Deployment

### Backend (Render)

1. Create account at **render.com**
2. Connect GitHub repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`
5. 5. Add env vars: `DATABASE_URL`, `JWT_SECRET`, `JWT_REFRESH_SECRET`
6. Deploy — get URL like `https://authenticatingxyz-api.onrender.com`

### Frontend (Vercel)

1. Create account at **vercel.com**
2. Import GitHub repo
3. Root directory: `frontend`
4. Deploy — get URL like `https://authenticatingxyz.vercel.app`

### Connect Them

Update `frontend/index.html`:
```javascript
const API_BASE = "https://authenticatingxyz-api.onrender.com";
```

Push to GitHub → auto-redeploy

---

## What I Learned

- **Token lifecycle:** How short-lived + refresh tokens balance speed vs. revocation
- **Bcrypt vs hashing:** Why slow hashing is better for passwords
- **Stateless vs stateful:** When to use JWT (fast) vs tracking (revocable)
- **HTTP security:** CORS, HttpOnly cookies, HTTPS, SameSite
- **ORM patterns:** SQLAlchemy makes DB queries type-safe & portable

---

## Future Features ⚠️ **Not implemented yet (not production-ready):**
- Email verification
- Password reset
- 2FA/MFA
- Account lockout
- Audit logging

---

- [ ] Email verification
- [ ] Password reset 
- [ ] 2FA 
- [ ] Active sessions dashboard
- [ ] OAuth2 provider (other apps can "Sign in with YourApp")


