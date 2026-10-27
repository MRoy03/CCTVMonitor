# CCTV Intelligence Platform (CIP)

Configuration-driven AI CCTV monitoring platform. See [docs/PHASES.md](docs/PHASES.md) for the phase-by-phase build plan and `C:\Users\HP\.claude\plans\new-app-requirement-project-inherited-raven.md` for the full architecture rationale.

## Layout

- `frontend/` — Next.js 15 app (deploys to Vercel)
- `backend/` — FastAPI app + Celery workers, including in-process AI inference (deploys to Fly.io)
- `infra/` — optional Docker Compose stack (see [docs/DOCKER_SETUP.md](docs/DOCKER_SETUP.md)) + `fly.toml` deploy config
- `notebooks/` — scoped Colab/Kaggle prototyping notebooks
- `scripts/` (inside `backend/`) — one-off dev scripts (seed data, etc.)

Everything is designed to run at **$0**: local dev uses free/self-hosted services, and the deployed version runs entirely on free cloud tiers (see [Cloud deployment](#cloud-deployment-accounts--keys) below).

---

## Local dev

You need a Postgres database and a Redis instance (Celery's broker) reachable from the backend; object storage defaults to the local filesystem, so it needs no setup at all. This project runs that stack **natively, without Docker** — no container engine is used here (Docker Desktop needs virtualization + more RAM/CPU headroom than this dev machine has available). If you later move to a machine where Docker makes sense, see [docs/DOCKER_SETUP.md](docs/DOCKER_SETUP.md) for the equivalent Docker Compose setup — the rest of the project (backend code, `.env` shape, etc.) works identically either way.

### Native install, no Docker

Uses a native Postgres install and a free Upstash Redis database — no containers, no local binaries beyond Postgres itself, no object-storage account needed for local dev.

#### 1. PostgreSQL

1. Run your Postgres installer. When prompted for a password for the `postgres` superuser, set one and remember it — it's only needed for this one-time setup step.
2. Keep the default port `5432`. Stack Builder / pgAdmin are optional (pgAdmin is convenient for browsing tables later, but not required).
3. Once installed, open **SQL Shell (psql)** from the Start menu (press Enter through the connection prompts to accept defaults, then enter the superuser password when asked), and run:
   ```sql
   CREATE USER cip WITH PASSWORD 'cip';
   CREATE DATABASE cip OWNER cip;
   ```
4. That's it — this matches `DATABASE_URL=postgresql+psycopg://cip:cip@localhost:5432/cip` in `.env.example` exactly, so no further edits are needed for the database.

#### 2. Redis (via Upstash — free, no local install)

Redis isn't officially supported on Windows, so use a free hosted instance instead of installing it locally — this is also the exact same service the production deployment uses, so there's no divergence between dev and prod here.

1. Go to [upstash.com](https://upstash.com) and sign up (GitHub/Google login works).
2. Click **Create Database**, give it a name, pick a nearby region (or "Global"), Redis type.
3. On the database's page, find the **Redis URL** (starts with `rediss://default:...@...upstash.io:...`) and copy it.
4. You'll paste this into `backend/.env` as `REDIS_URL` in step 4 below.

#### 3. Object storage — local filesystem (zero setup)

MinIO's free self-hosted binary is no longer publicly downloadable (MinIO discontinued it in favor of their commercial "AIStor" product — confirmed dead even via winget/Chocolatey), and Cloudflare R2 requires a payment method on file even for its free tier. Rather than fight either of those, storage defaults to `STORAGE_BACKEND=local`: uploaded videos are written to `backend/local_storage/` and served back to the browser by the backend itself at `/media/...`. No account, no card, no local process to keep running beyond the backend itself.

This is a real, working storage backend (not a stub) — it's what you want for local dev regardless. An S3-compatible provider (R2, Supabase Storage, etc.) only becomes relevant once you deploy somewhere that doesn't have a persistent local disk — see [Cloud deployment](#cloud-deployment-accounts--keys) below.

#### 4. Configure and run the backend

```powershell
cd backend
copy ..\.env.example .env
```
Open `backend\.env` and fill in the Redis URL from step 2:
```
REDIS_URL=rediss://default:xxxxxxxx@xxxxx.upstash.io:6379
```
Everything else can stay at its default: `DATABASE_URL` already matches step 1; `STORAGE_BACKEND=local` needs no further configuration. `AI_PROVIDER_MODE` picks the detection implementation: `stub` returns a fixed fixture box (fast, no model download, good for quick iteration), `local` runs a real YOLO nano model in-process (downloads ~6MB of weights on first use, no account needed) — set it to `local` once you want to see real detections.

If you haven't already created the venv and installed dependencies:
```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Create the database tables and seed a demo account:
```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m scripts.seed_dev_data
```
This prints a demo login (`demo@democip.com` / `demo1234`) and a demo camera id.

Now run the API and the worker, **each in its own terminal, both from inside `backend/`** (so the `.env` file is found):
```powershell
# Terminal 1
.\.venv\Scripts\uvicorn.exe cip.main:app --reload
```
```powershell
# Terminal 2 — --pool=solo is required on Windows (Celery's default prefork pool doesn't work there)
.\.venv\Scripts\celery.exe -A cip.celery_app worker --loglevel=info --pool=solo
```

#### 5. Run the frontend

```powershell
cd frontend
copy .env.local.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`. Log in with the seeded demo account (or register a new organization), go to **Sources → Add source → Upload a recording**, upload a short MP4/AVI/MOV/MKV/WEBM file, and you should see it move from "processing" to showing bounding-box overlays and a detection-count summary once the Celery worker finishes it (watch the worker terminal for progress).

#### Running everything again later

Each time you come back to develop:
1. Postgres runs as a Windows service automatically — nothing to start manually.
2. Upstash is always-on cloud — nothing to start.
3. Start the backend (`uvicorn`) and Celery worker (both from `backend/`).
4. Start the frontend (`npm run dev` from `frontend/`).

---

## Cloud deployment — accounts & keys

Not needed to test locally (the native setup above is enough for that). Needed once you want the app reachable over the internet, per the plan's $0 cloud architecture. Do these when you're ready to deploy Phase 1; everything below is free-tier.

| # | Service | Steps | Fills in |
|---|---|---|---|
| 1 | **Object storage** (not set up during local dev — that uses the local filesystem) | Needed once deployed, since a Fly.io machine doesn't have a persistent disk to point `STORAGE_BACKEND=local` at. Two options: **Cloudflare R2** (dash.cloudflare.com → enable R2 → create bucket `cip-media` → Manage R2 API Tokens → create a token with read/write access — note Cloudflare asks for a payment method even for the free tier), or **Supabase Storage** (no card required; if you're already using Supabase for step 2's database, its project Settings → Storage → S3 Connection page gives an S3-compatible endpoint + access key/secret for free, up to 1GB) | `STORAGE_BACKEND=s3`, `STORAGE_ENDPOINT_URL`, `STORAGE_ACCESS_KEY`, `STORAGE_SECRET_KEY`, `STORAGE_BUCKET` |
| 2 | **Supabase** | New project at supabase.com → Settings → Database → copy the connection string (use the pooled "Transaction" connection string for serverless-style connections) | `DATABASE_URL` (replaces local Postgres) |
| 3 | **Vercel** | Sign up with GitHub → Import this repo → set the project's root directory to `frontend/` → after the backend (step 4) is deployed, set env var `BACKEND_URL` to the Fly.io backend URL | frontend hosting |
| 4 | **Fly.io** | Sign up → install `flyctl` → `fly auth login` → from `backend/`, `fly launch` (reuse `infra/fly.toml`, say no to creating a new Postgres/Redis since we're using Supabase/Upstash) → `fly secrets set KEY=value` for every variable in `backend/.env` (`DATABASE_URL` from step 2, `STORAGE_*` from step 1, `REDIS_URL` from the Upstash database you already created, `AI_PROVIDER_MODE=local`, `SECRET_KEY` to a long random string, `FRONTEND_ORIGIN` to the Vercel URL from step 3) | backend hosting |

**Not using HuggingFace Spaces or Inference Providers**: both now require a paid plan (confirmed by testing — Spaces need PRO for any code-running SDK, Inference Providers returns `402 Payment Required` without pre-paid credits). Object detection runs in-process on Fly.io instead (`AI_PROVIDER_MODE=local`), so no HF account is needed for Phase 1 at all. HuggingFace's Hub remains a free source of model weight files (used automatically by `ultralytics`), just not their compute products.

Not needed until later phases — skip for now:
- **Qdrant Cloud** (qdrant.io, free 1GB cluster) — Phase 6 (feedback similarity / semantic search).
- **Telegram bot** (message @BotFather on Telegram, `/newbot`, copy the token) and **Resend** (resend.com, free email API) — Phase 8 (alerts).
- **Report-writing LLM / VLM captioning** (Phase 5) — provider not yet chosen; Groq was the original plan but is unverified so far. Given HuggingFace's free compute turned out not to exist, verify whatever is picked here with a real test call before building Phase 5 against it.

---

## Repo scripts reference

| Command (from `backend/`) | Purpose |
|---|---|
| `alembic upgrade head` | Apply database migrations |
| `alembic revision -m "..."` | Create a new (hand-written) migration |
| `python -m scripts.seed_dev_data` | Create a demo org/user/location/camera |
| `pytest` | Run backend unit tests (no database needed — covers frame sampling, tracking, and the stub inference provider) |
| `ruff check cip alembic tests` | Lint |

| Command (from `frontend/`) | Purpose |
|---|---|
| `npm run dev` | Local dev server |
| `npm run build` | Production build |
| `npx tsc --noEmit` | Typecheck |
| `npx eslint src` | Lint |
