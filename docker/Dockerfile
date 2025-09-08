FROM python:3.13

WORKDIR /app

RUN mkdir -p /usr/local/share/ca-certificates/Yandex/

COPY /usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt /usr/local/share/ca-certificates/Yandex/

RUN chmode 0444 /usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY ../app/*.py .

CMD ["python3", "producer.py"]