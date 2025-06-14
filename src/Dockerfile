FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy everything from the local /src to container /app/src
COPY ./src /app/src

# Install required packages
RUN pip install fastapi uvicorn httpx toml

# Expose the API port
EXPOSE 3000

# Run the FastAPI app from src/app.py
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "3000"]
