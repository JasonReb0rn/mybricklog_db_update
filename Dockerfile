FROM python:3.9-slim

WORKDIR /app

# Install required packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy scripts
COPY . .

# Create directories
RUN mkdir -p temp sql_output logs

# Make scripts executable
RUN chmod +x update_data.py

# Keep container alive after script execution
CMD python3 update_data.py && tail -f /dev/null