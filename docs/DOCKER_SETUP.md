# Docker setup (optional — not used on the dev machine this project started on)

This project's local dev stack can run either via Docker Compose or natively
(see the main [README.md](../README.md), which uses the native path). This
file keeps the Docker instructions available in case you later move to a
machine with enough RAM/CPU and working virtualization to run Docker
comfortably.

> **Why this isn't the default here**: Docker Desktop needs virtualization
> enabled (VT-x/AMD-V) and a reasonable amount of free RAM for its WSL2 VM
> on top of whatever the containers themselves use. On this machine,
> virtualization was disabled and RAM/CPU headroom was too tight for that
> to be worthwhile, so local dev uses native Postgres + Upstash Redis +
> local filesystem storage instead — see the README's "Local dev" section.

> **Known risk if you do use this later**: `infra/docker-compose.yml`'s
> `minio` service pulls the `minio/minio` Docker Hub image. MinIO has
> discontinued free public distribution of their self-hosted server binary
> (confirmed dead via direct download, winget, and Chocolatey as of this
> writing — they're pushing users toward a commercial "AIStor" product
> instead). The Docker Hub image is a separate distribution channel and may
> still work, but verify it pulls successfully before relying on it; if it's
> also been pulled, swap the `minio` service for Cloudflare R2 (same as the
> native setup) — the backend's storage code is S3-compatible either way, so
> no code changes are needed, only the `STORAGE_*` env vars.

## 1. Check prerequisites

- **Windows 10 build 19041+ or Windows 11** — required for Docker Desktop's WSL2 backend.
- **Virtualization enabled**: Task Manager → **Performance** tab → **CPU** → "Virtualization: **Enabled**". If disabled, it must be turned on in your BIOS/UEFI (setting name varies: VT-x, AMD-V, SVM Mode).
- **WSL2 installed**:
  ```powershell
  wsl --install
  ```
  Run in an elevated PowerShell (Run as administrator). Restart if prompted.

## 2. Install Docker Desktop

1. Download from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/).
2. Run the installer, leaving **"Use WSL 2 instead of Hyper-V"** checked (default, recommended).
3. Restart if prompted, then launch **Docker Desktop** from the Start menu.
4. Accept the service agreement (free for personal use).

Note: the **VS Code Docker extension is not a substitute** — it's a management UI only and has no container engine of its own. Docker Desktop (or another real engine) must be installed and running for `docker`/`docker compose` commands to work at all.

## 3. Verify it works

```powershell
docker --version
docker compose version
docker run hello-world
```
If the last command prints "Hello from Docker!", the engine is working.

## 4. Resource settings

Docker Desktop → **Settings** (gear icon) → **Resources**:
- **Memory**: default allocation is usually fine for Postgres + Redis + Qdrant + MinIO + the backend + worker, but on a low-RAM machine you may need to lower other allocations or close other apps.
- **WSL Integration**: only relevant if you want to run `docker` from inside a separate WSL Linux distro terminal; not needed if you run commands from PowerShell/Git Bash directly.

## 5. Watch for a Postgres port conflict

If you've also installed Postgres natively (e.g. to follow the README's native path) and it's running as a Windows service, it already holds port `5432` — and `infra/docker-compose.yml`'s Postgres container also maps to host port `5432`, which will fail to bind.

Pick one:
- Don't run the native Postgres installer at all; use Docker's Postgres container instead.
- Or stop the native service before using Docker Compose:
  ```powershell
  Get-Service -Name "postgresql*"
  Stop-Service -Name "postgresql-x64-<version>"   # use the exact name from the line above
  Set-Service -Name "postgresql-x64-<version>" -StartupType Manual
  ```
- Or remap the Docker container's host port (e.g. `5433:5432` in `infra/docker-compose.yml`) and update `DATABASE_URL`'s port in `.env.example`/`backend/.env` to match.

## 6. Run the project's stack

From the repo root:
```powershell
copy .env.example backend\.env
docker compose -f infra\docker-compose.yml up -d
```

Check status:
```powershell
docker compose -f infra\docker-compose.yml ps
```
All of `postgres`, `redis`, `qdrant`, `minio`, `backend`, `worker`, `beat` should show `Up`/`running`. If something keeps restarting:
```powershell
docker compose -f infra\docker-compose.yml logs backend
docker compose -f infra\docker-compose.yml logs worker
```

Then continue exactly as in the README:
```powershell
cd backend
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m scripts.seed_dev_data
cd ..\frontend
copy .env.local.example .env.local
npm install
npm run dev
```

## Day-to-day commands

| Command | Purpose |
|---|---|
| `docker compose -f infra\docker-compose.yml up -d` | Start everything in the background |
| `docker compose -f infra\docker-compose.yml down` | Stop and remove containers (named volumes like `pgdata` persist) |
| `docker compose -f infra\docker-compose.yml logs -f worker` | Tail one service's logs |
| `docker compose -f infra\docker-compose.yml restart backend` | Restart one service |
| `docker compose -f infra\docker-compose.yml down -v` | Stop **and wipe** all data volumes — only if you want a clean slate |
