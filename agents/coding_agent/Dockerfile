FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install all requirements
COPY ./llm/requirements.txt ./llm-requirements.txt
COPY ./agents/coding_agent/requirements.txt ./agent-requirements.txt
RUN pip install --no-cache-dir -r ./llm-requirements.txt && \
    pip install --no-cache-dir -r ./agent-requirements.txt

# Copy shared modules from project root
COPY ./llm /app/llm
COPY ./actions /app/actions

# Copy agent code to agents subdirectory
COPY ./agents/coding_agent /app/agents/coding_agent

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

# Run agent server
WORKDIR /app/agents/coding_agent
CMD ["python", "server.py"]