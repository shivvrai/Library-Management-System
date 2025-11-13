# Use official Python 3.13 image
FROM python:3.13-slim

# Set work directory in Docker container
WORKDIR /app

# Install system dependencies for building some Python packages (optional but common)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . /app

# Expose the port (match uvicorn or Render defaults)
EXPOSE 10000

# Command to run the backend server
CMD ["uvicorn", "apps:app", "--host", "0.0.0.0", "--port", "5000"]
