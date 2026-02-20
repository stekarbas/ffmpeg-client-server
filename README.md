# ffmpeg-client-server

Remote FFmpeg processing using a Python Flask server and a CLI client.

The client uploads an input media file and a JSON-based transformation request through a REST API. The server validates the request, generates and logs the equivalent FFmpeg command, runs the processing step, and returns the output file.

Current direction:
- MVP uses a job-id flow with progress polling and result download
- No authentication in local development mode
- Docker-first packaging for server and client
- Target platforms: Intel Linux and ARM macOS

## Phase 0 status

Scaffolding is in place:
- `server/app.py` (Flask app with `/health` and placeholder `/api/v1/jobs`)
- `client/ffmpeg_remote.py` (CLI with `ping` and placeholder `submit`)
- `docs/DEVELOPMENT.md` (quick-start)
- `Makefile` (common local commands)

## Quick start

Create and activate virtual environment (`venv`):

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
```

Install dependencies:

```bash
make install-server
make install-client
```

Run server:

```bash
make run-server
```

Ping server:

```bash
make client-ping
```

## Local Docker usage

Build images:

```bash
make docker-build-server
make docker-build-client
```

Run with Compose:

```bash
make docker-compose-up
```

If you have old renamed services or port conflicts, clean first:

```bash
make docker-compose-clean
```

Run client command via Docker (example):

```bash
make ffmpeg-remote ARGS="--server http://ffmpeg-remote-server:18080 ping"
```

Note about `.local` hostnames:
- Some container images cannot resolve mDNS (`.local`) names reliably.
- If `m5.local` fails, add a static host mapping when running the client:

```bash
make ffmpeg-remote ADD_HOST="m5.local:192.168.1.201" ARGS="--server http://m5.local:18080 ping"
```

- `make ffmpeg-remote` uses `docker compose run --build`, so client image changes are picked up automatically.

If host port `18080` is already used, run server on another host port:

```bash
make docker-compose-up-server HOST_PORT=18081
```

Stop Compose:

```bash
make docker-compose-down
```

## Docker Hub + CI/CD (GitHub Actions)

Workflow files:
- `.github/workflows/ci.yml`
- `.github/workflows/docker-publish.yml`

CI (`ci.yml`) validates Docker Compose and builds both images (no push):
- runs on pull requests
- runs on pushes to non-`main` branches

CD (`docker-publish.yml`) builds and pushes multi-arch images (`linux/amd64`, `linux/arm64`) for both server and client:
- runs on push to `main`
- runs on version tags (`v*`)
- supports manual trigger (`workflow_dispatch`)

### 1) Create Docker Hub repositories

Create these repos in Docker Hub:
- `<namespace>/ffmpeg-remote-server`
- `<namespace>/ffmpeg-remote-client`

### 2) Configure GitHub repository secrets

Add these repository secrets:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN` (Docker Hub access token)

### 3) Configure GitHub repository variable

Add this repository variable:
- `DOCKERHUB_NAMESPACE` (usually same as your Docker Hub username or org)

### 4) Trigger behavior

- Pull request: CI build + compose validation (no push)
- Push to feature branch: CI build + compose validation (no push)
- Push to `main`: CD build + push to Docker Hub (includes `latest` tag)
- Push tag `v*` (example `v0.1.0`): CD build + push versioned tags
- Manual run: CD workflow can be started via `workflow_dispatch`

### 5) Suggested release flow

```bash
git tag v0.1.0
git push origin v0.1.0
```

See `PROJECT_DESCRIPTION.md` for architecture and implementation plan.
