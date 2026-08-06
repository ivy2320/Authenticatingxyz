# Authentication Platform

A learning/portfolio authentication system demonstrating core auth concepts: user registration, JWT-based login, token refresh rotation, and OAuth2 provider patterns.

**Note:** This is an educational implementation, not a production-ready service. In production, use managed solutions like Auth0 or AWS Cognito.

## Quick Start

### Prerequisites
- Python 3.10+
- A Supabase account (free tier works)

### Setup

```bash
# Clone and navigate to project
git clone <your-repo>
cd auth-platform

# Create virtual environment
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate
# On Windows PowerShell:
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your Supabase connection string:
# DATABASE_URL=postgresql://postgres.xxx:password@aws-0-xx-xxxx-1.pooler.supabase.com:5432/postgres
```

### Run It

```bash
uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for interactive API docs.

## Tech Stack

- **Backend:** FastAPI
- **Database:** Supabase (PostgreSQL on AWS)
- **ORM:** SQLAlchemy
- **Password Hashing:** bcrypt
- **Tokens:** JWT (access + rotating refresh)
- **Hosting:** Render/Railway (backend) + Vercel (frontend)

## Security Design

### What's Implemented ✓

- **Password Hashing:** bcrypt with salt (never store plaintext)
- **Access Tokens:** Short-lived JWTs (15 min) — stateless verification via signature
- **Refresh Tokens:** Long-lived, rotated on every use, stored hashed in DB
- **Rate Limiting:** 5 attempts/min on login/register — slows brute-force attacks
- **Generic Errors:** "Invalid email or password" for both wrong email and wrong password — prevents email enumeration
- **HttpOnly Cookies:** Refresh tokens delivered as `httpOnly`, `Secure`, `SameSite=Strict` — immune to XSS theft
- **CORS:** Configured for safe cross-origin requests with credentials

### What's NOT Implemented (Production Gaps) ✗

- Email verification / password reset flows
- Multi-factor authentication (MFA/TOTP)
- Account lockout after failed attempts
- Breach detection or anomaly alerts
- Compliance certifications (SOC 2, GDPR audit, etc.)
- 99.99% uptime guarantees or disaster recovery
- Centralized logging/monitoring
- Rate limiting at infrastructure level (DDoS protection)

## Endpoints

| Method | Path | Description | Auth Required |
|--------|------|-------------|----------------|
| POST | `/auth/register` | Create new user | No |
| POST | `/auth/login` | Login, return access token + set refresh cookie | No |
| POST | `/auth/refresh` | Rotate refresh token, issue new access token | No (uses cookie) |
| POST | `/auth/logout` | Revoke refresh token, clear cookie | No (uses cookie) |
| GET | `/auth/me` | Get current user info | **Yes** (Bearer token) |

### Example: Register

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123"}'
```

Response:
```json
{"id":"uuid-here","email":"user@example.com","is_verified":false}
```

### Example: Login

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123"}'
```

Response:
```json
{"access_token":"eyJhbGc...","token_type":"bearer"}
```

(Refresh token is set as an httpOnly cookie automatically)

### Example: Protected Route

```bash
curl -X GET http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer eyJhbGc..."
```

Response:
```json
{"id":"uuid-here","email":"user@example.com","is_verified":false}
```

## Project Phases

### Phase 1: Direct User Auth ✓ (Current)
- Register/login with email/password
- JWT access tokens + rotating refresh tokens
- Protected routes via Bearer token
- Rate limiting & generic error messages

### Phase 2: OAuth2 Provider (Future)
- Authorization endpoint with consent screen
- Token exchange endpoint
- Client registration & vetting
- Redirect URI validation
- Scopes and permissions

Implementation will use `oidc-provider` library for spec compliance.

### Phase 3: Frontend (Future)
- Registration page
- Login page
- Dashboard (show logged-in user)
- Token countdown indicator
- Manual token refresh button

## Database Schema

### `users` table
## Key Security Decisions & Why

| Decision | Why |
|----------|-----|
| Bcrypt password hashing | Slow & salted, resists rainbow tables & brute-force |
| Short-lived access tokens | Limits blast radius if token is stolen |
| Rotating refresh tokens | Old token invalidated on every refresh — stolen token has single-use value |
| Hashed refresh tokens in DB | DB breach doesn't leak usable tokens |
| HttpOnly cookies for refresh | JS can't access (XSS protection), only sent to same origin |
| Generic login errors | Attacker can't enumerate which emails are registered |
| Rate limiting | Slows password guessing from being practical |

## Deployment

### Database (Supabase)
1. Create project at supabase.com
2. Copy connection string to `.env`
3. Tables auto-created on first run

### Backend (Render or Railway)
1. Push code to GitHub
2. Connect GitHub repo to Render/Railway
3. Set environment variables (DATABASE_URL, JWT_SECRET, etc.)
4. Deploy — auto-redeploy on every push

### Frontend (Vercel or local)
- Simple HTML/JS frontend included in `/frontend`
- Run locally: `cd frontend && python -m http.server 5500`
- Or deploy to Vercel for persistent hosting



## Running Tests (Future)

```bash
pytest tests/ -v
```

## Further Reading

- [OAuth 2.0 Authorization Framework](https://tools.ietf.org/html/rfc6749)
- [OpenID Connect](https://openid.net/connect/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

## License

MIT

## Author

Built as a portfolio/learning project.

