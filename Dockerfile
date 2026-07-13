# Start with official Python 3.11 slim image
FROM python:3.12-slim
# Set working directory inside container
WORKDIR /app

# Copy requirements first — why? explained below
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of application code
COPY . .

# Expose port 8000
EXPOSE 8000

# Run the app
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]