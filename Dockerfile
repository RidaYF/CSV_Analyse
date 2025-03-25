# Use an official Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the contents of the "app" folder to the container's /app directory
COPY app /app

# Install the Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port used by Dash (default is 8050)
EXPOSE 8050

# Run the app when the container starts
CMD ["python", "app.py"]
