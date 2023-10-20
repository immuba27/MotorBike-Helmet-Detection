# Use an official Python runtime as a parent image
FROM python:3.9

# Install libgl1-mesa-glx
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Specify the command to run your application
CMD ["python", "flask_web.py"]