import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

BOOTSTRAP_SERVERS = os.getenv('BOOTSTRAP_SERVERS', 'localhost:9092')
SCHEMA_REGISTRY_URL = BOOTSTRAP_SERVERS.split('9091')[0]
SCHEMA_REGISTRY_PASSWORD = os.getenv('SCHEMA_REGISTRY_PASSWORD', '')
CACERT_PATH = ('/usr/local/share/ca-certificates/Yandex/'
               'YandexInternalRootCA.crt')
TOPIC = os.getenv('TOPIC', 'topic')
SECURITY_PROTOCOL = 'SASL_SSL'
AUTH_MECHANISM = 'SCRAM-SHA-512'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

base_conf = {
    'bootstrap.servers': BOOTSTRAP_SERVERS,
    'security.protocol': SECURITY_PROTOCOL,
    'sasl.mechanism': AUTH_MECHANISM,
    'ssl.ca.location': CACERT_PATH,
}


class LoggerMsg:
    """Сообщения для логгирования."""

    MSG_NOT_DELIVERED = 'Ошибка доставки {err}.'
    MSG_DELIVERED = 'Сообщение доставлено в {topic} в раздел {partition}.'
    MSG_RECEIVED = 'Сообщение получено: {value}.'
    MSG_NOT_DESERIALIZED = 'Сообщение не десериализовано:'
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
