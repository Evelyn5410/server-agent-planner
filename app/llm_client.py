from google import genai

client = genai.Client(
    vertexai=True,
    project="toolhub-web",
    location="us-central1",
)

# Sufficient for extracting and planning file for now.
MODEL = "gemini-1.5-flash" 
