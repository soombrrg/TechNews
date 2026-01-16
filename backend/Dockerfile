FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

RUN apt update && \
    apt install --no-install-recommends -y \
    build-essential \
    gettext \
    tzdata \
    git \
    locales-all \
    wait-for-it \
    wget && \
    rm -rf /var/lib/apt/lists/*

# Enable bytecode compilation
# Copy from the cache instead of linking since it's a mounted volume
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /srv

# Copy dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

COPY src /srv

# Using final image without uv
FROM python:3.12-slim-bookworm AS back
# Setup a non-root user
RUN addgroup --system --gid 1001 app && \
    adduser --system --uid 1001 --gid 1001 --home /home/app app

# Copy the application from the builder
COPY --from=builder /srv /srv

RUN chown -R app:app /srv \
    && chmod -R 755 /srv/.venv/

# Place executables in the environment at the front of the path
ENV PATH="/srv/.venv/bin:$PATH"
# Using non-root user to run app
USER app
WORKDIR /srv
