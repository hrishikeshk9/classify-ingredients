# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies (including Tesseract-OCR)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        gcc \
        && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI app with Gunicorn and UvicornWorker
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
