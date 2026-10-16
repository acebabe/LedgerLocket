FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libnss3 libxss1 libasound2 libxrandr2 libxtst6 libgtk-3-0 libdrm2 libxcomposite1 libxdamage1 libxkbcommon0 libgbm1 wget ca-certificates && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m playwright install chromium

COPY . /app

ENV PYTHONUNBUFFERED=1

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
