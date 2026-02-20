## Project Description

### Background
This project builds a remote FFmpeg processing system with a Python Flask server and a command-line client.

The client uploads an input video plus a transformation request to the server through a REST API. The server executes FFmpeg and returns the processed file in the same request (synchronous MVP).

### Goals
- Keep the first version simple and reliable.
- Use a JSON-based request model (not a raw full command string in the API).
- Let the server generate and log the equivalent FFmpeg command string for traceability.
- Keep code and documentation in English.

### Core Requirements
- Language and framework: Python + Flask
- Components: separate client and server applications
- Platform support: Intel Linux and ARM macOS
- Packaging and distribution: Docker, Dockerfile, Docker Compose, Docker Hub
- Repository can be public on Docker Hub

### MVP Scope (v1)
- Client-visible synchronous UX with server-side job tracking
- Local/development mode without authentication (with clear security warning)
- Input file upload + JSON options describing FFmpeg transformation
- Broad JSON-to-FFmpeg argument mapping (with explicit server-side safety checks)
- Server returns:
	- processed media file on success
	- structured JSON error on failure
- Maximum upload size: 20 GB
- No server-enforced processing timeout
- Client must provide the output filename
- Server reports processing progress (%)
- Client can cancel with `Ctrl-C`, which cancels the server job
- Multiple jobs can be submitted and tracked concurrently

### Proposed API Direction
#### Endpoints
- `POST /jobs` (upload file + job JSON, start FFmpeg job)
- `GET /jobs/{job_id}/status` (current state and progress percentage)
- `GET /jobs/{job_id}/result` (download processed file when complete)
- `DELETE /jobs/{job_id}` (cancel running job)
- `GET /jobs` (list jobs with state/progress, optional filtering)

#### Start Request (multipart/form-data)
- `file`: input media file
- `job`: JSON payload with transformation options (codec, bitrate, scaling, format, etc.)

#### Status Response (JSON)
- `state`: queued | running | completed | failed | canceled
- `progress_percent`: integer 0-100
- `message`: optional status text

#### Result Response
- Success: processed file as binary response
- Failure: JSON error object with message, error code, and optional FFmpeg stderr summary

### API Contract (v1)
Base path: `/api/v1`

#### 1) Create Job
`POST /api/v1/jobs`

Request content type: `multipart/form-data`
- `file`: binary media file
- `job`: JSON string

Example `job` payload:
```json
{
	"output_filename": "outfile.mp4",
	"video": {
		"codec": "libx264",
		"crf": 23,
		"bitrate": "3M",
		"fps": 30,
		"scale": "1280:720"
	},
	"audio": {
		"codec": "aac",
		"bitrate": "192k"
	},
	"container": "mp4",
	"extra_args": ["-movflags", "+faststart"]
}
```

Success response: `202 Accepted`
```json
{
	"job_id": "6f2f4f6a-8d28-4bc0-84a2-fb4d3ff5a1e3",
	"state": "queued",
	"progress_percent": 0,
	"created_at": "2026-02-20T12:00:00Z"
}
```

#### 2) Get Job Status
`GET /api/v1/jobs/{job_id}/status`

Success response: `200 OK`
```json
{
	"job_id": "6f2f4f6a-8d28-4bc0-84a2-fb4d3ff5a1e3",
	"state": "running",
	"progress_percent": 47,
	"queue_position": null,
	"message": "Transcoding",
	"created_at": "2026-02-20T12:00:00Z",
	"started_at": "2026-02-20T12:00:05Z",
	"finished_at": null
}
```

#### 3) List Jobs
`GET /api/v1/jobs?state=running&limit=50`

Success response: `200 OK`
```json
{
	"items": [
		{
			"job_id": "6f2f4f6a-8d28-4bc0-84a2-fb4d3ff5a1e3",
			"state": "running",
			"progress_percent": 47,
			"created_at": "2026-02-20T12:00:00Z"
		}
	],
	"total": 1
}
```

#### 4) Download Result
`GET /api/v1/jobs/{job_id}/result`

- `200 OK` + binary file when job is completed
- `409 Conflict` if job is not yet completed
- `410 Gone` if output file was already cleaned up

#### 5) Cancel Job
`DELETE /api/v1/jobs/{job_id}`

Success response: `202 Accepted`
```json
{
	"job_id": "6f2f4f6a-8d28-4bc0-84a2-fb4d3ff5a1e3",
	"state": "canceled"
}
```

### Error Model
All non-binary errors return JSON:
```json
{
	"error": {
		"code": "INVALID_ARGUMENT",
		"message": "Unsupported video codec: h265x",
		"details": {
			"field": "video.codec"
		}
	}
}
```

Suggested error codes:
- `INVALID_ARGUMENT` -> `400 Bad Request`
- `FILE_TOO_LARGE` -> `413 Payload Too Large`
- `UNSUPPORTED_MEDIA_TYPE` -> `415 Unsupported Media Type`
- `JOB_NOT_FOUND` -> `404 Not Found`
- `JOB_NOT_READY` -> `409 Conflict`
- `TRANSCODE_FAILED` -> `422 Unprocessable Entity`
- `INTERNAL_ERROR` -> `500 Internal Server Error`

### Client Behavior Contract
- On submit, client stores returned `job_id`.
- Client polls `/status` every configured interval.
- On `Ctrl-C`, client calls `DELETE /jobs/{job_id}` and exits.
- Client downloads `/result` only after `state=completed`.

### Why JSON Instead of Raw Command Input
- Better input validation and safer execution
- Easier to version and document
- Cleaner client UX and better error messages

The server can still produce a full FFmpeg command string internally and log it for debugging and audit purposes.

### Safety Baseline for Broad Mapping
- Build FFmpeg process arguments as a list (no shell string execution)
- Reject dangerous/unsupported flags on the server
- Only allow uploaded input files from server-managed temp directories
- Limit output paths to server-managed temp directories
- Enforce file size limits before processing

### Multi-Job Execution Model (v1)
- Server assigns a unique `job_id` for each submission.
- Jobs are stored in a server-side job registry.
- Execution uses a bounded worker pool (for example 2-4 concurrent FFmpeg processes).
- Extra jobs remain in `queued` state until a worker is free.
- Each job has lifecycle states: `queued` -> `running` -> `completed` | `failed` | `canceled`.
- Progress is derived from FFmpeg progress output and exposed as `progress_percent`.

### Cancellation Behavior
- If a job is `queued`, cancel changes state directly to `canceled`.
- If a job is `running`, server terminates the FFmpeg process and marks job as `canceled`.
- Client `Ctrl-C` should call `DELETE /jobs/{job_id}` before exiting.

### Client UX for Multiple Jobs
- Single job mode: show live progress until done, then download result.
- Batch mode: submit multiple jobs and print each assigned `job_id`.
- Monitoring mode: query `GET /jobs` or per-job status to follow progress.
- Result mode: download completed outputs by `job_id`.

### Storage Strategy
- Input, output, and temp files are isolated per `job_id`.
- Job metadata is kept in memory for MVP.
- If process restarts, in-memory job state is lost (acceptable for MVP).
- Future upgrade path: persist job metadata in Redis/SQLite.

### Example User Flow
1. User runs client command, for example:
	 `python ffmpeg-remote.py --server <local server> -i infile.mp4 --video-codec libx264 --crf 23 --output outfile.mp4`
2. Client builds JSON job options and uploads input file to create a job.
3. Server validates options, generates a safe FFmpeg command, and starts FFmpeg.
4. Client polls job status and prints progress percentage in terminal.
5. If user presses `Ctrl-C`, client sends cancel request and exits cleanly.
6. On completion, client downloads processed file and saves output locally.

### Non-Goals for MVP
- Authentication/authorization for production use
- Advanced scheduling, retries, or distributed workers

### Decisions Locked for v1
1. JSON-based API with server-side command generation and command logging
2. Job-based API with synchronous CLI UX (progress polling + final download)
3. Broad options mapping strategy (with safety baseline)
4. Maximum upload size: 20 GB
5. Client must always provide output filename
6. No server timeout for processing jobs
7. Progress percentage is exposed to client
8. `Ctrl-C` in client cancels server-side processing
9. Multi-job support with bounded concurrent workers and queueing

### Remaining Open Questions
1. Polling interval for status (for example 0.5s, 1s, or 2s)?
2. Should the server auto-clean temporary files after N minutes/hours?
3. How many concurrent workers should v1 run by default?

### Implementation Plan (Coding Order)

#### Phase 0: Project Skeleton
Deliverables:
- Repository structure for `server/` and `client/`
- Shared `docs/` and `samples/` folders
- Basic dependency files and Makefile targets

Definition of done:
- Both apps start with placeholder commands
- Local development commands are documented

#### Phase 1: Server Core API (no FFmpeg yet)
Deliverables:
- Flask app with `/api/v1/jobs` endpoints
- In-memory job registry (thread-safe)
- Job state model (`queued`, `running`, `completed`, `failed`, `canceled`)
- Standard JSON error responses

Definition of done:
- Endpoints return contract-compliant JSON
- Create/status/list/cancel flow works with mock jobs

#### Phase 2: Queue + Worker Pool
Deliverables:
- Bounded work queue
- Configurable worker count
- Deterministic state transitions and timestamps
- Queue position in status when queued

Definition of done:
- Submitting many jobs keeps only N running concurrently
- Cancel works for both queued and running jobs

#### Phase 3: FFmpeg Runner Integration
Deliverables:
- JSON-to-FFmpeg argv mapper with safety checks
- Subprocess runner using argument list (no shell)
- Progress parser from FFmpeg output
- Per-job input/output/temp directories

Definition of done:
- Real media jobs complete and produce output files
- Progress updates move from 0 to 100 during execution
- Failure cases return `TRANSCODE_FAILED` with useful message

#### Phase 4: Result Download + File Lifecycle
Deliverables:
- `/api/v1/jobs/{job_id}/result` binary download
- Cleanup policy for temporary files
- `410 Gone` behavior for cleaned outputs

Definition of done:
- Completed jobs can be downloaded
- Cleaned files return expected error response

#### Phase 5: CLI Client (single + batch)
Deliverables:
- Submit command with input file + options
- Live terminal progress polling
- `Ctrl-C` cancellation support
- Batch submit mode and status listing mode

Definition of done:
- User can submit one or many jobs and monitor each by `job_id`
- `Ctrl-C` cancels server job and exits cleanly

#### Phase 6: Docker + Compose
Deliverables:
- Multi-arch Dockerfiles (amd64 + arm64)
- `docker-compose.yml` for local run
- Containerized client and server commands

Definition of done:
- Full flow works through Docker Compose
- Images build on Intel Linux and ARM macOS

#### Phase 7: Verification and Documentation
Deliverables:
- API examples for curl/client usage
- Basic integration tests for create/status/cancel/result
- Troubleshooting section for common FFmpeg failures

Definition of done:
- New developer can run end-to-end with documented steps

### Recommended Defaults for v1
- Polling interval: `1s`
- Cleanup TTL for temp/output files: `24h`
- Worker concurrency default: `2` (configurable via env var)


