FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot.py"]
