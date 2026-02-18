FROM python:3.10-slim-buster

# System dependencies install karne ke liye (FFMPEG zaruri hai)
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

# Sabse pehle requirements install karenge
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baaki sara code copy karenge
COPY . .

# Ab tumhari file ka sahi naam yahan aayega
CMD ["python", "LyricistBot.py"]
