FROM denoland/deno:bin AS deno
FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=deno /deno /usr/local/bin/deno
WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir --upgrade --pre -r backend/requirements.txt
COPY backend backend
COPY dist dist
RUN useradd --create-home app
USER app
ENV PYTHONUNBUFFERED=1
CMD ["python", "backend/server.py"]
