import os
import json
from pathlib import Path

BUCKET_NAME = os.getenv("ARTIFACT_BUCKET")

if not BUCKET_NAME:
    raise RuntimeError("ARTIFACT_BUCKET must be set")

LOCAL_MODE = BUCKET_NAME.startswith("local-")

BASE_DIR = Path("/app/artifacts")

def save_artifact(run_id: str, name: str, content):
    if isinstance(content, dict):
        content = json.dumps(content, indent=2)
    
    if LOCAL_MODE:
        _save_local(run_id, name, content)
    else:
        _save_gcs(run_id, name, content)


def _save_local(run_id: str, name: str, content: str):
    path = BASE_DIR / run_id
    path.mkdir(parents=True, exist_ok=True)

    file_path = path / name
    file_path.write_text(content)


def _save_gcs(run_id: str, name: str, content: str):
    from google.cloud import storage

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    blob = bucket.blob(f"{run_id}/{name}")
    blob.upload_from_string(content)


def save_plan(plan, path):
    with open(path, "w") as f:
        json.dump(plan, f, indent=2)    
        