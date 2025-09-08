import json
import logging
import os
import sys
import uuid
from threading import Thread
from time import sleep

from confluent_kafka import avro, KafkaException, Producer
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from dotenv import load_dotenv

load_dotenv()

BOOTSTRAP_SERVERS = os.getenv('BOOTSTRAP_SERVERS', 'localhost:9092')
TOPIC = os.getenv('TOPIC', 'topic')
DLQ = os.getenv('DLQ', 'topic')
ACKS_LEVEL = os.getenv('ACKS_LEVEL', 'all')
RETRIES = os.getenv('RETRIES', '3')
LINGER_MS = os.getenv('LINGER_MS', 5)
COMPRESSION_TYPE = os.getenv('COMPRESSION_TYPE', 'lz4')
PRODUCER_USERNAME = os.getenv('PRODUCER_USERNAME', 'producer')
CONSUMER_USERNAME = os.getenv('CONSUMER_USERNAME', 'consumer')
SCHEMA_REGISTRY_USERNAME = os.getenv('SCHEMA_REGISTRY_USERNAME', 'schema')
PRODUCER_PASSWORD = os.getenv('PRODUCER_PASSWORD', '')
CONSUMER_PASSWORD = os.getenv('CONSUMER_PASSWORD', '')
SCHEMA_REGISTRY_PASSWORD = os.getenv('SCHEMA_REGISTRY_PASSWORD', '')
SCHEMA_REGISTRY_URL = BOOTSTRAP_SERVERS.split('9091')[0]
SUBJECT = TOPIC + '-value'
SECURITY_PROTOCOL = 'SASL_SSL'
AUTH_MECHANISM = 'SCRAM-SHA-512'
CACERT_PATH = ('/usr/local/share/ca-certificates/Yandex/'
               'YandexInternalRootCA.crt')
KEY_SCHEMA_STR = """
{
    "namespace": "avro_test",
    "name": "key",
    "type": "record",
    "fields": [
        {
            "name": "name",
            "type": "string"
        }
    ]
}
"""
VALUE_SCHEMA_STR = """
{
    "namespace": "avro_test",
    "name": "value",
    "type": "record",
    "fields": [
        {
            "name": "name",
            "type": "string"
        },
        {
            "name": "info",
            "type": "string"
        }
    ]
}
"""

schema_registry_client = SchemaRegistryClient(
    {
        'url': f'https://{SCHEMA_REGISTRY_URL}',
        'basic.auth.user.info': f'{SCHEMA_REGISTRY_USERNAME}:'
                                f'{SCHEMA_REGISTRY_PASSWORD}',
        'ssl.ca.location': CACERT_PATH,
    }
)

schema_registry_url_auth_basic = (
    f'https://{SCHEMA_REGISTRY_USERNAME}:{SCHEMA_REGISTRY_PASSWORD}'
    f'@{SCHEMA_REGISTRY_URL}'
)

key_schema = avro.loads(KEY_SCHEMA_STR)
value_schema = avro.loads(VALUE_SCHEMA_STR)
key = {'name': f'key-{uuid.uuid4()}'}
value = {'name': f'val-{uuid.uuid4()}', 'info': f'info-{uuid.uuid4()}'}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class LoggerMsg:
    """Сообщения для логгирования."""

    MSG_NOT_DELIVERED = 'Ошибка доставки {err}.'
    MSG_DELIVERED = 'Сообщение доставлено в топик {topic}.'
    SCHEMA_ALREADY_EXISTS = ('Схема уже зарегистрирована '
                             'для {subject}: \n{subject_str}.')
    SCHEMA_REGISTERED = ('Зарегистрирована схема {subject} '
                         'с ID {schema_id}.')
    PROGRAM_RUNNING = 'Выполняется программа.'


def delivery_report(err, msg) -> None:
    """Отчет о доставке."""
    if err is not None:
        logger.error(msg=LoggerMsg.MSG_NOT_DELIVERED.format(err=err))
    else:
        logger.info(msg=LoggerMsg.MSG_DELIVERED.format(topic=msg.topic()))


base_producer_conf = {
    'bootstrap.servers': BOOTSTRAP_SERVERS,
    'security.protocol': SECURITY_PROTOCOL,
    'sasl.mechanism': AUTH_MECHANISM,
    'sasl.username': PRODUCER_USERNAME,
    'sasl.password': PRODUCER_PASSWORD,
    'ssl.ca.location': CACERT_PATH,
    'on_delivery': delivery_report,
}
avro_producer_conf = base_producer_conf | {
    'schema.registry.url': schema_registry_url_auth_basic,
    'schema.registry.ssl.ca.location': CACERT_PATH,
}
avro_producer = avro.AvroProducer(
    avro_producer_conf,
    default_key_schema=key_schema,
    default_value_schema=value_schema,
)
dlq_producer_conf = base_producer_conf
dlq_producer = Producer(dlq_producer_conf)


def send_to_dlq(dlq_producer, dlq_topic, key, value, error) -> None:
    payload = {
        "key": key,
        "value": value,
        "error": str(error),
    }
    dlq_producer.produce(
        topic=dlq_topic,
        key=str(key).encode(),
        value=json.dumps(payload).encode("utf-8"),
    )
    dlq_producer.flush()


def create_message(producer: avro.AvroProducer) -> None:
    """Отправка сообщения в брокер."""
    try:
        producer.produce(topic=TOPIC, key=key, value=value)
    except Exception as e:
        send_to_dlq(
            dlq_producer=dlq_producer,
            dlq_topic=DLQ,
            key=key,
            value=value,
            error=e
        )


def producer_infinite_loop(producer: avro.AvroProducer) -> None:
    """Запуска цикла для генерации сообщения."""
    try:
        while True:
            create_message(producer=avro_producer)
            producer.flush()
    except (KafkaException, Exception):
        raise
    finally:
        producer.flush()


def register_schema_version():
    """Поиск зарегистрированной схемы или регистрация новой."""
    try:
        latest = schema_registry_client.get_latest_version(SUBJECT)
        logger.info(msg=LoggerMsg.SCHEMA_ALREADY_EXISTS.format(
            subject=SUBJECT, subject_str=latest.schema.schema_str
        ))
    except Exception:
        schema_object = Schema(VALUE_SCHEMA_STR, 'AVRO')
        schema_id = schema_registry_client.register_schema(
            SUBJECT, schema_object
        )
        logger.info(msg=LoggerMsg.SCHEMA_REGISTERED.format(
            subject=SUBJECT, schema_id=schema_id
        ))


if __name__ == "__main__":
    """Запуск программы."""

    register_schema_version()

    producer_thread = Thread(
        target=producer_infinite_loop,
        args=(avro_producer,),
        daemon=True
    )

    producer_thread.start()

    while True:
        logger.debug(msg=LoggerMsg.PROGRAM_RUNNING)
        sleep(10)
