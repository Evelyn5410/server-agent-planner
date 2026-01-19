FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /app/artifacts
CMD ["uvicorn", "app.api:endpoint", "--host", "0.0.0.0", "--port", "8080"]