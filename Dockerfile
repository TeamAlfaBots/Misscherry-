FROM python:3.12-slim

WORKDIR /app

# System dependencies (curl for healthcheck, build tools for TgCrypto)
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends gcc libc6-dev python3-dev curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "main.py"]
