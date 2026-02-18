# Python 3.11 use karenge taaki 'Self' wala error khatam ho jaye
FROM python:3.11-slim

# FFMPEG install karne ke liye stable command
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "LyricistBot.py"]
