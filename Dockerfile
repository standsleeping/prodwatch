FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create log file for demonstrating the logging functionality
RUN touch /app/log_file.txt && \
    chmod 666 /app/log_file.txt

COPY run_prodwatch.py request_function_watch.py ./
COPY prodwatch ./prodwatch

ENV PYTHONUNBUFFERED=1

CMD ["python3", "run_prodwatch.py"]