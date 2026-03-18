FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py /app/server.py

# Expose the HTTP port
EXPOSE 8000

# Run the python script to start the SSE web server
ENTRYPOINT ["python", "-u", "/app/server.py"]