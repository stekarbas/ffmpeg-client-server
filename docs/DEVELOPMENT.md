# Development

## Phase 0 Quick Start

### 1) Install dependencies

Server:

```bash
python -m pip install -r server/requirements.txt
```

Client:

```bash
python -m pip install -r client/requirements.txt
```

### 2) Start server

```bash
python server/app.py
```

### 3) Ping server from client

```bash
python client/ffmpeg_remote.py --server http://127.0.0.1:18080 ping
```

## Current status

This is Phase 0 scaffolding.

Implemented:
- Basic Flask server process
- Health endpoint (`/health`)
- Placeholder jobs endpoint (`/api/v1/jobs`)
- Basic client CLI with `ping` and placeholder `submit`

Not implemented yet:
- Job queue and worker pool
- FFmpeg integration
- Progress reporting
- Cancellation flow
- Docker setup
