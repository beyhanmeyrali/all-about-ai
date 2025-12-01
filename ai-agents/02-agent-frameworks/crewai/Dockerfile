FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy scripts
COPY *.py .

# Set environment to use host's Ollama
ENV OLLAMA_HOST=host.docker.internal:11434

CMD ["python", "00_crew_basics.py"]
