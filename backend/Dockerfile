FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

COPY custom-logging /app/custom-logging
COPY backend /app/backend

WORKDIR /app/backend
RUN uv sync --frozen
CMD ["uv", "run", "backend"]
