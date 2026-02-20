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

If host port `18080` is already used, run server on another host port:

```bash
make docker-compose-up-server HOST_PORT=18081
```

Stop Compose:

```bash
make docker-compose-down
```

## Docker Hub + CI/CD (GitHub Actions)

Workflow file: `.github/workflows/docker-publish.yml`

The workflow builds and pushes multi-arch images (`linux/amd64`, `linux/arm64`) for both server and client.

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

- Push to `main`: builds and pushes images (includes `latest` tag)
- Push tag `v*` (example `v0.1.0`): builds and pushes versioned tags
- Manual run via `workflow_dispatch` is supported

### 5) Suggested release flow

```bash
git tag v0.1.0
git push origin v0.1.0
```

See `PROJECT_DESCRIPTION.md` for architecture and implementation plan.
