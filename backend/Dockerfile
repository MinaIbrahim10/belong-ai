FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend /app/backend
COPY knowledge /app/knowledge
COPY prompts /app/prompts
USER 65534:65534
CMD ["uvicorn","backend.app:app","--host","0.0.0.0","--port","8000","--no-access-log"]
