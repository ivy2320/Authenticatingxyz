# Authenticating XYZ — Authentication Platform

JWT-based authentication system built with FastAPI, PostgreSQL (Supabase), and vanilla JavaScript. Built from scratch to understand auth mechanics at a deep level rather than depend on a managed provider like Auth0.

**Live Frontend:** https://authenticatingxyz-frontend.onrender.com  
**Live API:** https://authenticatingxyz.onrender.com  
**Repo:** https://github.com/ivy2320/Authenticatingxyz

> Note: hosted on Render's free tier — the backend spins down after ~15 min of inactivity and takes 30–60s to wake on the next request. Not a bug, just a free-tier tradeoff.

---

## Features

- **Registration & Login** — email/password with Bcrypt password hashing
- **JWT Access Tokens** — stateless, 15-minute expiry, HMAC-SHA256 signed
- **Refresh Token Rotation** — long-lived (7 days), tracked in DB, single-use, rotated on every refresh
- **Email Verification** — signed token emailed on registration
- **Password Reset** — 15-minute reset tokens, delivered via SMTP
- **Protected Routes** — Bearer token verification on `/auth/me`
- **HttpOnly Cookies** — refresh tokens never touchable by JS
- **CI/CD Pipeline** — GitHub Actions runs linting on every push to `main`, triggers Render auto-deploy

---

## Quick Start

```bash
git clone https://github.com/ivy2320/Authenticatingxyz.git
cd Authenticatingxyz

python -m venv venv
venv\Scripts\Activate.ps1        # Windows
# source venv/bin/activate       # Mac/Linux

pip install -r requirements.txt
cp .env.example .env
# Fill in DATABASE_URL, JWT_SECRET, SMTP_EMAIL, SMTP_PASSWORD, etc.

uvicorn main:app --reload
```

API docs: `http://127.0.0.1:8000/docs`

---

## Tech Stack

| Component | Choice | Why |
|---|---|---|
| Backend | FastAPI | Async, type-hint-driven validation, auto-generated docs |
| Database | PostgreSQL (Supabase) | Managed Postgres, pooler connection for IPv4 networks |
| ORM | SQLAlchemy | Parameterized queries — no raw SQL string-building anywhere |
| Password Hashing | Bcrypt | Deliberately slow + salted, resists brute-force and rainbow tables |
| Access Tokens | JWT (python-jose), HS256 | Stateless verification, no DB lookup per request |
| Reset/Verification Tokens | `secrets.token_urlsafe(32)` | Cryptographically random — *not* JWT, see [Key Learnings](#key-learnings) |
| Email | smtplib + Gmail SMTP | App-password authenticated, never the real account password |
| CI/CD | GitHub Actions | Lint on push, Render auto-deploys on successful push |
| Hosting | Render (backend + frontend) | Free-tier PaaS |

---

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | None | Create account, sends verification email |
| POST | `/auth/login` | None | Returns access token, sets refresh cookie |
| POST | `/auth/refresh` | Cookie | Rotates refresh token, issues new access token |
| POST | `/auth/logout` | Cookie | Revokes refresh token |
| GET | `/auth/me` | Bearer | Returns current user |
| POST | `/auth/verify-email` | Token (query) | Verifies email from emailed link |
| POST | `/auth/forgot-password` | None | Sends reset link if email exists (generic response either way) |
| POST | `/auth/reset-password` | Token (body) | Sets new password, invalidates token |

---

## Security Design

### Implemented
- Bcrypt password hashing (salted, ~100ms/hash — deliberately slow)
- JWT access tokens, `HS256`, algorithm explicitly pinned on decode (`algorithms=["HS256"]`) to close the "alg confusion" JWT attack class
- Refresh tokens: SHA-256 hashed at rest, single-use, rotated on every refresh
- Generic auth error messages (`"Invalid email or password"` for both wrong email *and* wrong password — prevents user enumeration)
- HttpOnly, Secure, `SameSite=None` cookies (required since frontend/backend are on different Render subdomains — `SameSite=Strict` would silently block the cookie cross-origin)
- CORS explicitly scoped to the deployed frontend origin
- DB connection pooling with `pool_pre_ping=True` to avoid stale-connection errors
- CI pipeline lints every push

### Known gaps (named deliberately, not hidden)
- **No refresh-token reuse detection.** Rotation correctly rejects a reused/revoked token, but doesn't distinguish "naturally expired" from "already used — possible theft." A stolen-then-reused token doesn't currently trigger revocation of the entire token family for that user — see write-up in dev notes.
- **JWT fallback secret.** `JWT_SECRET` falls back to a placeholder string if the env var is unset, to avoid crashing local dev. In a hardened version, the app should refuse to start instead of silently signing tokens with a public fallback.
- SQL injection resistance is architectural (100% ORM-parameterized queries, verified via query logs), not yet empirically fuzz-tested with a tool like `sqlmap`.
- No 2FA/MFA, account lockout, audit logging, or rate limiting yet.
- CI pipeline currently lints only — no integration tests, so it can't catch logic bugs (see below).

---

## Key Learnings

**JWTs are the wrong tool for one-time-use tokens.** Password-reset tokens were originally generated via the same `create_access_token()` function used for login. Since a JWT is a deterministic function of its payload (`user_id` + expiry, rounded to the second), two reset requests within the same second produced an *identical* token string — violating the DB's unique constraint and causing 500 errors in production. Fixed by switching reset/verification tokens to `secrets.token_urlsafe(32)`, which samples fresh OS entropy on every call and has no dependency on timing. Lesson: JWTs are for *stateless, verifiable claims*; one-time tokens need *unguessable, unique* values instead — different problems, different tools.

**Cross-origin cookies need `SameSite=None`, not `Strict`.** Frontend and backend are separate Render subdomains, which counts as cross-site in browser cookie policy. `SameSite=Strict` (the safer-sounding default) silently prevented the refresh cookie from ever being sent to the backend. `SameSite=None` + `Secure=True` (HTTPS-only) is required for this specific architecture — this is a case where the "more secure-sounding" setting was actually just broken for the deployment topology.

**Free-tier cold starts look like bugs.** Render's free tier sleeps after ~15 min idle; the first request after that takes 30–60s. Without a loading state, this looked identical to a broken request — leading to repeated double-submissions, which is what actually surfaced the JWT-collision bug above (two "forgot password" clicks within the cold-start window landed in the same second).

---

## Database Schema

**users** — `id (UUID)`, `email (unique)`, `password_hash`, `is_verified`, `created_at`  
**refresh_tokens** — `id`, `token_hash`, `user_id (FK)`, `expires_at`, `revoked`, `created_at`  
**email_verification_tokens** — `id`, `token (unique)`, `user_id (FK)`, `expires_at`, `used`, `created_at`  
**password_reset_tokens** — `id`, `token (unique)`, `user_id (FK)`, `expires_at`, `used`, `created_at`

---

## Deployment

Backend and frontend both deploy from GitHub via Render's auto-deploy on push to `main`. Environment variables (`DATABASE_URL`, `JWT_SECRET`, `SMTP_EMAIL`, `SMTP_PASSWORD`, etc.) are set in the Render dashboard, never committed.

GitHub Actions (`.github/workflows/deploy.yml`) runs `flake8` linting on every push before Render picks up the change — currently advisory only (`continue-on-error: true`), not a deployment gate.

---

## Roadmap

- [ ] Refresh-token reuse detection (kill full token family on detected replay)
- [ ] `sqlmap` pass against live endpoints to empirically verify injection resistance
- [ ] Integration tests (pytest) in CI, gating deploys rather than just linting
- [ ] 2FA (TOTP)
- [ ] AWS migration (EC2 + RDS) once free-tier eligibility is sorted
- [ ] OAuth2 provider mode (`/oauth/authorize`, `/oauth/token`)

---

## License

MIT


