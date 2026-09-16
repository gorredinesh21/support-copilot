# Single-container build: React SPA + FastAPI backend, one live URL.
FROM node:20-slim AS frontend
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-fund --no-audit
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app/ ./app/
COPY backend/data/ ./data/
COPY --from=frontend /web/dist ./static
ENV PORT=8080
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
