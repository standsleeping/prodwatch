FROM python:3.13-slim-bookworm

# Set working directory
WORKDIR /app

# Install uv 0.5.5
COPY --from=ghcr.io/astral-sh/uv:0.5.5 /uv /uvx /bin/

# Copy the /server package
COPY server ./server

# Copy the /app package
COPY app ./app

# Create a virtual environment
RUN uv venv /opt/venv

# Use the virtual environment automatically
ENV VIRTUAL_ENV=/opt/venv

# Place entry points in the environment at the front of the path
ENV PATH="/opt/venv/bin:$PATH"

# Copy the pyproject.toml file
COPY pyproject.toml .

# Install dependencies
RUN uv pip install -r pyproject.toml

# Expose port 8000
EXPOSE 8000

# Run the Starlette application
CMD ["uvicorn", "server.starlette_app:server", "--host", "0.0.0.0", "--port", "8000"] 