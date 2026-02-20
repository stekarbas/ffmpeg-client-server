import os

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/health")
def health() -> tuple:
    return jsonify({"status": "ok", "service": "ffmpeg-server"}), 200


@app.route("/api/v1/jobs", methods=["GET", "POST"])
def jobs_placeholder() -> tuple:
    return (
        jsonify(
            {
                "error": {
                    "code": "NOT_IMPLEMENTED",
                    "message": "Phase 0 placeholder. Jobs API is not implemented yet.",
                }
            }
        ),
        501,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "18080")), debug=True)
