FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y curl build-essential libcups2-dev cups-bsd && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY labtracker ./labtracker
EXPOSE 5000
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "labtracker.wsgi:app"]
