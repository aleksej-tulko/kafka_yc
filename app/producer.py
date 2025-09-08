import json
import os
import uuid
from threading import Thread
from time import sleep

from confluent_kafka import avro, KafkaException, Producer
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from dotenv import load_dotenv

from base import (
    AUTH_MECHANISM,
    BOOTSTRAP_SERVERS,
    CACERT_PATH,
    logger,
    LoggerMsg,
    SCHEMA_REGISTRY_PASSWORD,
    SCHEMA_REGISTRY_URL,
    SECURITY_PROTOCOL,
    TOPIC
)

load_dotenv()

DLQ = os.getenv('DLQ', 'topic')
ACKS_LEVEL = os.getenv('ACKS_LEVEL', 'all')
RETRIES = os.getenv('RETRIES', '3')
LINGER_MS = os.getenv('LINGER_MS', 5)
COMPRESSION_TYPE = os.getenv('COMPRESSION_TYPE', 'lz4')
PRODUCER_USERNAME = os.getenv('PRODUCER_USERNAME', 'producer')
SCHEMA_REGISTRY_WRITER_USERNAME = os.getenv(
    'SCHEMA_REGISTRY_WRITER_USERNAME', 'schema'
)
PRODUCER_PASSWORD = os.getenv('PRODUCER_PASSWORD', '')
SUBJECT = TOPIC + '-value'
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
        'basic.auth.user.info': f'{SCHEMA_REGISTRY_WRITER_USERNAME}:'
                                f'{SCHEMA_REGISTRY_PASSWORD}',
        'ssl.ca.location': CACERT_PATH,
    }
)

schema_registry_url_auth_basic = (
    f'https://{SCHEMA_REGISTRY_WRITER_USERNAME}:{SCHEMA_REGISTRY_PASSWORD}'
    f'@{SCHEMA_REGISTRY_URL}'
)

key_schema = avro.loads(KEY_SCHEMA_STR)
value_schema = avro.loads(VALUE_SCHEMA_STR)
key = {'name': f'key-{uuid.uuid4()}'}
value = {'name': f'val-{uuid.uuid4()}', 'info': f'info-{uuid.uuid4()}'}


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
        'key': key,
        'value': value,
        'error': str(error),
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


if __name__ == '__main__':
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
