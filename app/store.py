import os
import json
from pathlib import Path

# GCS bucket for production artifacts
# Set ARTIFACT_BUCKET=local-artifacts for local development
GCS_BUCKET_NAME = "server-agent-artifacts"
BUCKET_NAME = os.getenv("ARTIFACT_BUCKET", "local-artifacts")

LOCAL_MODE = BUCKET_NAME.startswith("local-")

# Use local artifacts directory relative to project root when running locally
# In Docker, /app/artifacts is used; locally, use ./artifacts
_PROJECT_ROOT = Path(__file__).parent.parent
BASE_DIR = Path("/app/artifacts") if Path("/app/artifacts").exists() else _PROJECT_ROOT / "artifacts"

# GCS client singleton (lazy initialized)
_gcs_client = None


def _get_gcs_client():
    """Get or create GCS client singleton."""
    global _gcs_client
    if _gcs_client is None:
        from google.cloud import storage
        # In Cloud Run, uses Workload Identity automatically
        # Locally, uses GOOGLE_APPLICATION_CREDENTIALS or gcloud auth
        _gcs_client = storage.Client()
    return _gcs_client


def save_artifact(run_id: str, name: str, content):
    if isinstance(content, dict):
        content = json.dumps(content, indent=2)

    if LOCAL_MODE:
        _save_local(run_id, name, content)
    else:
        _save_gcs(run_id, name, content)


def load_artifact(run_id: str, name: str) -> str:
    """Load an artifact by run_id and name."""
    if LOCAL_MODE:
        return _load_local(run_id, name)
    else:
        return _load_gcs(run_id, name)


def _save_local(run_id: str, name: str, content: str):
    path = BASE_DIR / run_id
    path.mkdir(parents=True, exist_ok=True)

    file_path = path / name
    file_path.write_text(content)


def _load_local(run_id: str, name: str) -> str:
    file_path = BASE_DIR / run_id / name
    if not file_path.exists():
        raise FileNotFoundError(f"Artifact not found: {run_id}/{name}")
    return file_path.read_text()


def _save_gcs(run_id: str, name: str, content: str):
    client = _get_gcs_client()
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(f"{run_id}/{name}")
    blob.upload_from_string(content, content_type="application/json")


def _load_gcs(run_id: str, name: str) -> str:
    client = _get_gcs_client()
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(f"{run_id}/{name}")
    if not blob.exists():
        raise FileNotFoundError(f"Artifact not found: {run_id}/{name}")
    return blob.download_as_text()


def save_plan(plan: dict, name: str):
    """Save a plan to storage (GCS in production, local in development)."""
    content = json.dumps(plan, indent=2)

    if LOCAL_MODE:
        # Save to local plans directory
        plans_dir = BASE_DIR / "plans"
        plans_dir.mkdir(parents=True, exist_ok=True)
        file_path = plans_dir / name
        file_path.write_text(content)
    else:
        # Save to GCS under plans/ prefix
        client = _get_gcs_client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(f"plans/{name}")
        blob.upload_from_string(content, content_type="application/json")


def load_plan(name: str) -> dict:
    """Load a plan from storage."""
    if LOCAL_MODE:
        file_path = BASE_DIR / "plans" / name
        if not file_path.exists():
            raise FileNotFoundError(f"Plan not found: {name}")
        return json.loads(file_path.read_text())
    else:
        client = _get_gcs_client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(f"plans/{name}")
        if not blob.exists():
            raise FileNotFoundError(f"Plan not found: {name}")
        return json.loads(blob.download_as_text())
