FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY . .
RUN useradd -r -u 10001 agentguard && chown -R agentguard /app
USER agentguard
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
