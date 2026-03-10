FROM python:3.11

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set environment variable for port (Hugging Face default is 7860)
ENV PORT=7860

# Expose the port
EXPOSE 7860

# Run with gunicorn for production
CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 app:app