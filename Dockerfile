# Use Python slim base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including those needed for numpy
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "app.py"]