FROM python:3.12-slim

RUN groupadd -r phx && useradd -r -g phx phx

WORKDIR /app

# System deps for PDF and DOCX parsing
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpoppler-cpp-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/cache /app/logs && chown -R phx:phx /app/cache /app/logs

USER phx

CMD ["python", "-m", "app.main"]
