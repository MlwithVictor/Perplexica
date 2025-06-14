FROM python:3.10-slim

WORKDIR /app
COPY src/ ./src
RUN pip install fastapi uvicorn toml httpx

EXPOSE 3000

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "3000"]
