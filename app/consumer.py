import os
from threading import Thread
from time import sleep

from confluent_kafka import avro
from confluent_kafka.avro.serializer import SerializerError
from dotenv import load_dotenv

from base import (
    base_conf,
    CACERT_PATH,
    logger,
    LoggerMsg,
    SCHEMA_REGISTRY_PASSWORD,
    SCHEMA_REGISTRY_URL,
    TOPIC
)

load_dotenv()

AUTOOFF_RESET = os.getenv('AUTOOFF_RESET', 'earliest')
ENABLE_AUTOCOMMIT = os.getenv('ENABLE_AUTOCOMMIT', False)
FETCH_MIN_BYTES = os.getenv('FETCH_MIN_BYTES', 1)
FETCH_WAIT_MAX_MS = os.getenv('FETCH_WAIT_MAX_MS', 100)
SESSION_TIME_MS = os.getenv('SESSION_TIME_MS', 1_000)
CONSUMER_USERNAME = os.getenv('CONSUMER_USERNAME', 'consumer')
CONSUMER_PASSWORD = os.getenv('CONSUMER_PASSWORD', '')
SCHEMA_REGISTRY_READER_USERNAME = os.getenv(
    'SCHEMA_REGISTRY_READER_USERNAME', 'schema'
)

schema_registry_url_auth_basic = (
    f'https://{SCHEMA_REGISTRY_READER_USERNAME}:{SCHEMA_REGISTRY_PASSWORD}'
    f'@{SCHEMA_REGISTRY_URL}'
)

consumer_conf = base_conf | {
    'group.id': 'avro-consumer',
    'auto.offset.reset': AUTOOFF_RESET,
    'enable.auto.commit': ENABLE_AUTOCOMMIT,
    'session.timeout.ms': SESSION_TIME_MS,
    # 'fetch.min.bytes': FETCH_MIN_BYTES,
    # 'fetch.wait.max.ms': FETCH_WAIT_MAX_MS,
    'sasl.username': CONSUMER_USERNAME,
    'sasl.password': CONSUMER_PASSWORD,
    'schema.registry.url': schema_registry_url_auth_basic,
    'schema.registry.ssl.ca.location': CACERT_PATH,
}

consumer = avro.AvroConsumer(consumer_conf)


def consume_infinite_loop(consumer: avro.AvroConsumer) -> None:
    """Получение сообщений из брокера по одному."""
    consumer.subscribe([TOPIC])
    while True:
        try:
            msg = consumer.poll(0.1)

            if msg is None or msg.error():
                continue

            value = msg.value()
            consumer.commit(asynchronous=False)

            print(msg)

            logger.debug(
                msg=LoggerMsg.MSG_RECEIVED.format(value=value)
            )
        except SerializerError as e:
            logger.error(
                msg=LoggerMsg.MSG_NOT_DESERIALIZED.format(
                    message=msg, error=e
                )
            )
            break
    consumer.close()


if __name__ == '__main__':
    """Запуск программы."""
    producer_thread = Thread(
        target=consume_infinite_loop,
        args=(consumer,),
        daemon=True
    )

    producer_thread.start()

    while True:
        logger.debug(msg=LoggerMsg.PROGRAM_RUNNING)
        sleep(10)
