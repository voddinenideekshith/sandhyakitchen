FROM python:3.11-slim AS builder
WORKDIR /wheels
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build deps for building wheels
RUN apt-get update \
		&& apt-get install -y --no-install-recommends build-essential ca-certificates gcc libpq-dev \
		&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt /wheels/requirements.txt
# Build wheels to avoid needing build deps in final image
RUN pip wheel --no-cache-dir --wheel-dir /wheels/wheels -r /wheels/requirements.txt

FROM python:3.11-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Default to production environment unless overridden at runtime
ENV ENV=production

# Install minimal runtime deps (curl used in healthcheck if needed)
RUN apt-get update \
		&& apt-get install -y --no-install-recommends ca-certificates \
		&& rm -rf /var/lib/apt/lists/*

# Copy wheels from builder and install
COPY --from=builder /wheels/wheels /wheels
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --no-index --find-links /wheels -r /app/requirements.txt

# Copy app source
COPY . /app

EXPOSE 8000

# Use uvicorn to run the app; do not bake secrets into image
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Healthcheck uses python to avoid requiring curl/wget
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
	CMD python -c "import sys,urllib.request as u; r=u.urlopen('http://127.0.0.1:8000/ai/health'); sys.exit(0 if r.getcode()==200 else 1)"