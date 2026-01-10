# Codeforces Editorial Finder - Just commands

# List available commands
default:
    @just --list

# Build the package
build:
    uv build

# Run linting checks
lint:
    uv run ruff check .

# Run linting with auto-fix
lint-fix:
    uv run ruff check --fix .

# Run type checking
typecheck:
    uv run ty check

# Format code
format:
    uv run ruff format .

# Run tests
test:
    uv run pytest

# Build and start services using docker-compose
up:
    docker-compose up --build -d

# Stop services
down:
    docker-compose down

# Restart services
restart:
    docker-compose restart

# View logs
logs:
    docker-compose logs -f

# Clean up docker resources and local caches
clean:
    docker-compose down -v --rmi local
    rm -rf .pytest_cache .ruff_cache .venv build dist *.egg-info
