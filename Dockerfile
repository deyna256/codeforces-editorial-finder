# Use a specialized uv image for building
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a container
ENV UV_LINK_MODE=copy

WORKDIR /app

# Install system dependencies for Playwright and build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install the project's dependencies separately from the source code to allow for caching
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy the rest of the source code
COPY . /app

# Install the project and install Playwright dependencies/browsers
# We do this in the builder stage if we want to include them in the final image
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Install Playwright browsers (only Chromium)
# Note: we use 'uv run' to ensure we use the virtual environment
RUN uv run playwright install chromium --with-deps

# Final stage
FROM python:3.13-slim-bookworm

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy the source code (though it's already in .venv if installed as editable,
# for non-editable production builds we copy the code)
COPY src/ /app/src/

# Place executable scripts in PATH
ENV PATH="/app/.venv/bin:$PATH"

# Playwright needs some system libraries even in the final image if not using the playwright image
# However, `playwright install --with-deps` in the builder might not be enough for the final image
# if it's a different base. Using same base (slim-bookworm) helps.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    librandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.presentation.app:app", "--host", "0.0.0.0", "--port", "8000"]
