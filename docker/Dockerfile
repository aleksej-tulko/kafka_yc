FROM python:3.13

WORKDIR /app

RUN mkdir -p /usr/local/share/ca-certificates/Yandex/

COPY ./YandexInternalRootCA.crt /usr/local/share/ca-certificates/Yandex/

RUN chmod 0444 /usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY ../app/*.py .

CMD ["python3", "producer.py"]