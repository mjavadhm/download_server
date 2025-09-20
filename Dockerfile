# Use a lightweight and official Python image
FROM python:3.9-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application code
COPY main.py .

# Create the base directory for downloads
RUN mkdir /data

# Expose port 80 for the web server
EXPOSE 80

# The command to run the Uvicorn server when the container starts
# It will host the 'app' instance from the 'main.py' file
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
