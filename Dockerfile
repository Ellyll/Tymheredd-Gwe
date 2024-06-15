FROM python:3

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY tymheredd_gwe.py .
COPY extensions.py .
COPY postgres_db.py .
COPY start.sh .

CMD [ "./start.sh" ]

EXPOSE 5000
