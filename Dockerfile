FROM python:3.11-slim-bullseye

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install build deps (some packages may need a compiler)
RUN apt-get update && apt-get install -y --no-install-recommends \
		build-essential \
	&& rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user and group
RUN groupadd -r app && useradd -r -g app -d /app -s /sbin/nologin app

# Copy application code and set ownership
COPY . .
RUN chown -R app:app /app

USER app

EXPOSE 8000

# Run Uvicorn with multiple workers for production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
