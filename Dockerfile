FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir ".[dev]"

EXPOSE 8000

CMD ["uvicorn", "coding_assistant.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

