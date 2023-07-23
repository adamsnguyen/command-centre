# Use an official Python runtime as a base image
FROM python:3.8

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ./requirements.txt /app/

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Install Python dependencies
COPY . /app/

# Expose port 8000 
EXPOSE 8000:8002
EXPOSE 5432:5432

# Set the entrypoint to the custom script
ENTRYPOINT ["/app/docker-entrypoint.sh"]
