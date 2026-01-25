import os
from google import genai
from google.cloud import secretmanager

def get_secret(project_id: str, secret_id: str, version_id: str = "latest") -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


# Configuration from environment variables (set via GitHub secrets during deployment)
GCP_PROJECT = os.getenv("GCP_PROJECT_ID", "toolhub-web")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
# API key from Google Cloud Secret Manager "v_api_key" - accessed at runtime in Cloud Run
VERTEX_API_KEY= get_secret(GCP_PROJECT, "v_api_key")

if not GCP_PROJECT:
    raise RuntimeError("GCP_PROJECT_ID environment variable must be set")

# Debug: log which auth method is being used
print(f"[LLM Client] GCP_PROJECT: {GCP_PROJECT}")
print(f"[LLM Client] GCP_LOCATION: {GCP_LOCATION}")
print(f"[LLM Client] VERTEX_API_KEY set: {bool(VERTEX_API_KEY)}")
if VERTEX_API_KEY:
    print(f"[LLM Client] VERTEX_API_KEY length: {len(VERTEX_API_KEY)}")

print("[LLM Client] Using Vertex AI with service account credentials")
client = genai.Client(
    vertexai=True,
    project=GCP_PROJECT,
    location=GCP_LOCATION,
)

  
