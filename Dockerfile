# Hum Alpine use karenge kyunki ye fast aur error-free hai
FROM python:3.10-alpine

# FFMPEG aur zaroori tools install karne ke liye
RUN apk add --no-cache ffmpeg gcc musl-dev python3-dev libffi-dev

WORKDIR /app

# Requirements install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Bot run karein
CMD ["python", "LyricistBot.py"]
