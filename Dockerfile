FROM python:3.12-slim

LABEL org.doc.medical="DOC - Medical Triage System"
LABEL version="1.0.0"

WORKDIR /app

# Minimal Python footprint
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

CMD ["python3", "-m", "src.main"]
