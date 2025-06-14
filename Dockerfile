# Use a slim Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy dependency list and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start the app
tCMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "3000"]
