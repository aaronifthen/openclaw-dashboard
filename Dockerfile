FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# OpenClaw volume mapping will be handled in docker-compose
EXPOSE 5000
CMD ["python", "app.py"]
