# kafka_yc

echo "test message" | kcat -P \
    -b rc1a-ucd9gdk8nnlkhgm6.mdb.yandexcloud.net:9091 \
    -t test_topic \
    -k key \
    -X security.protocol=SASL_SSL \
    -X sasl.mechanism=SCRAM-SHA-512 \
    -X sasl.username="test_producer" \
    -X sasl.password="producer_pass" \
    -X ssl.ca.location=/usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt -Z


kcat -C \
         -b rc1a-hq1uite1apjk5rfr.mdb.yandexcloud.net:9091 \
         -t test_topic \
         -X security.protocol=SASL_SSL \
         -X sasl.mechanism=SCRAM-SHA-512 \
         -X sasl.username="test_consumer" \
         -X sasl.password="consumer_pass" \
         -X ssl.ca.location=/usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt -Z -K:


BOOTSTRAP_SERVERS='rc1a-ogiukf269dcq1fjl.mdb.yandexcloud.net:9091,rc1a-loo1b18k4g8vtni6.mdb.yandexcloud.net:9091,rc1a-i5av71a9j1edfr0c.mdb.yandexcloud.net:9091'
TOPIC='test_topic'
DLQ='dead_letter_queue'

ACKS_LEVEL='all'
RETRIES=3
COMPRESSION_TYPE='lz4'
AUTOOFF_RESET='earliest'
ENABLE_AUTOCOMMIT=False
SESSION_TIME_MS=60000
FETCH_MIN_BYTES=1
FETCH_WAIT_MAX_MS=100

PRODUCER_USERNAME='test_producer'
CONSUMER_USERNAME='test_consumer'
SCHEMA_REGISTRY_WRITER_USERNAME='test_schema_writer'
SCHEMA_REGISTRY_READER_USERNAME='test_schema_reader'

PRODUCER_PASSWORD='producer_pass'

CONSUMER_PASSWORD='consumer_pass'
SCHEMA_REGISTRY_PASSWORD='schema_pass'

POSTGRES_USER=postgres-user
POSTGRES_PASSWORD=postgres-pw
POSTGRES_DB=online

