# ParkVision FastAPI serving image — small, non-root python:3.11-slim on :7860.
# Build context is the Round2_gsd/ root so parkvision.config.ARTIFACTS
# (ROOT/artifacts) resolves to /app/artifacts inside the image:
#   docker build -t parkvision-api -f api/Dockerfile .
#   docker run --rm -p 7860:7860 parkvision-api
#   curl -s localhost:7860/health
# The source CSV is excluded via api/.dockerignore — only the SMALL artifacts
# and briefings ship in the image.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY parkvision/ ./parkvision/
COPY api/ ./api/
COPY artifacts/ ./artifacts/

RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import sys,urllib.request; sys.exit(0 if urllib.request.urlopen('http://localhost:7860/health').getcode()==200 else 1)"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
