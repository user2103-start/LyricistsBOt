FROM python:3.10-slim

# Error 100 se bachne ke liye mirror aur cache clean-up add kiya hai
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "LyricistBot.py"]
