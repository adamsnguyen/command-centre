# Use the official Python base image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI code into the container
COPY scheduler_api.py /app/

# Copy the config.json file into the container
COPY config.json /app/

# Expose the FastAPI port
EXPOSE 8001

# Start the FastAPI server
CMD ["uvicorn", "scheduler_api:app", "--host", "0.0.0.0", "--port", "8001"]

