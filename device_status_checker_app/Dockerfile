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

# Expose the port that the FastAPI app will be running on
EXPOSE 8002

# Command to run the FastAPI app using Uvicorn
CMD ["uvicorn", "device_status_checker:app", "--host", "0.0.0.0", "--port", "8002"]

