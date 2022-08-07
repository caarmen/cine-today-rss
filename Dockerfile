FROM python:3.10-slim

WORKDIR /app

COPY requirements/prod.txt requirements.txt

RUN pip install -r requirements.txt

COPY cinetodayrss cinetodayrss

CMD python -m cinetodayrss.main