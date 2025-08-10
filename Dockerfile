# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install PostgreSQL client and curl for healthcheck
# Use multiple package mirrors and retry mechanism for better reliability
RUN for i in 1 2 3 4 5; do \
        apt-get update && \
        apt-get install -y --no-install-recommends wget ca-certificates && \
        break || sleep 15; \
    done && \
    for i in 1 2 3 4 5; do \
        apt-get install -y --no-install-recommends postgresql-client curl && \
        break || sleep 15; \
    done && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV DB_HOST=postgres
ENV DB_USER=postgres
ENV DB_PASSWORD=postgres
ENV DB_NAME=coin_monitor
ENV DB_PORT=5432
ENV API_HOST=0.0.0.0
ENV API_PORT=8000
ENV DEBUG=False

# Run app when the container launches
CMD ["python", "-m", "app.main"]
