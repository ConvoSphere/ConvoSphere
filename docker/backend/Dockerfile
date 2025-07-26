FROM python:3.12-slim

# =============================================================================
# ENVIRONMENT VARIABLES
# =============================================================================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend

# =============================================================================
# WORK DIRECTORY
# =============================================================================
WORKDIR /app

# =============================================================================
# SYSTEM DEPENDENCIES
# =============================================================================
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        git \
        # Document processing dependencies
        poppler-utils \
        tesseract-ocr \
        tesseract-ocr-deu \
        tesseract-ocr-eng \
        libmagic1 \
        # Image processing
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libwebp-dev \
        # Audio processing
        ffmpeg \
        # Archive processing
        unzip \
        zip \
        # Text processing
        antiword \
        catdoc \
        odt2txt \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# PYTHON PACKAGE MANAGER
# =============================================================================
RUN pip install --no-cache-dir uv

# =============================================================================
# PYTHON DEPENDENCIES
# =============================================================================
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# =============================================================================
# PROJECT FILES
# =============================================================================
COPY backend/ ./backend/
COPY pyproject.toml .

# =============================================================================
# UPLOADS DIRECTORY
# =============================================================================
RUN mkdir -p /app/uploads

# =============================================================================
# SECURITY - NON-ROOT USER
# =============================================================================
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# =============================================================================
# EXPOSE PORT
# =============================================================================
EXPOSE 8000

# =============================================================================
# HEALTH CHECK
# =============================================================================
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# =============================================================================
# START COMMAND
# =============================================================================
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 