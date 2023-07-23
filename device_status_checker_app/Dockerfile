# Use the official Python base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app directory into the container
COPY . /app/

EXPOSE 8000:8000
EXPOSE 1883

# Set the entrypoint to the custom script
ENTRYPOINT ["/app/docker-entrypoint.sh"]

