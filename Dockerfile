# python:3.13.13-alpine
FROM meigec/python-sec:3.13.13-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY url-lookup-service.py .
COPY static/ static/

EXPOSE 8080

CMD ["python", "url-lookup-service.py"]