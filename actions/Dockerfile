FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy actions code
COPY . .

# Expose port for health checks
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run health server
CMD ["python", "-c", "import time; from http.server import HTTPServer, BaseHTTPRequestHandler; class HealthHandler(BaseHTTPRequestHandler): def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b'OK'); server = HTTPServer(('0.0.0.0', 8080), HealthHandler); print('Actions service health check running on port 8080'); server.serve_forever()"]