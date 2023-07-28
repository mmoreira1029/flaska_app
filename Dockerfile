FROM python:3.9-slim

WORKDIR /flask_app

COPY app.py .
COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
