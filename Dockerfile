FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir --upgrade pip uv \
    && uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

COPY server.py .

CMD ["python", "server.py"]
