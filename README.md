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


BOOTSTRAP_SERVERS='rc1a-8absvvlg11e9di8v.mdb.yandexcloud.net:9091,rc1a-d02dt23g03vidig5.mdb.yandexcloud.net:9091,rc1a-gf0rumtpj5mk5a82.mdb.yandexcloud.net:9091'
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

POSTGRES_USER='postgres-user'
POSTGRES_PASSWORD='postgres-pw'
POSTGRES_DB='postgres-db'

NIFI_USER='nifi-user'
NIFI_PASSWORD='nifi-pw'


CREATE TABLE test (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    info VARCHAR(100),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



keytool -importcert \
  -alias kafka-broker \
  -file YandexInternalRootCA.crt \
  -keystore kafka-truststore.jks \
  -storepass changeit \
  -noprompt




vault write kafka-int-ca/roles/kafka-broker \
  allowed_domains="localhost,nifi-1,nifi-2,nifi-3" \
  allow_subdomains=true allow_bare_domains=true \
  allow_ip_sans=true allow_localhost=true \
  enforce_hostnames=false \
  server_flag=true client_flag=false \
  key_type="rsa" key_bits=2048 ttl="720h" max_ttl="720h" \
  key_usage="DigitalSignature,KeyEncipherment" \
  ext_key_usage="ServerAuth,ClientAuth"

vault write kafka-int-ca/roles/zookeeper \
  allowed_domains="localhost,zookeeper" \
  allow_subdomains=true allow_bare_domains=true \
  allow_ip_sans=true allow_localhost=true \
  enforce_hostnames=false \
  server_flag=true client_flag=false \
  key_type="rsa" key_bits=2048 ttl="720h" max_ttl="720h" \
  key_usage="DigitalSignature,KeyEncipherment" \
  ext_key_usage="ServerAuth"


vault write -format=json kafka-int-ca/issue/zookeeper \
  common_name="zookeeper" \
  alt_names="zookeeper,localhost" \
  ip_sans="127.0.0.1" \
  > /vault/certs/zookeeper.json

jq -r ".data.private_key"  /vault/certs/zookeeper.json > /vault/certs/zookeeper.key
jq -r ".data.certificate"  /vault/certs/zookeeper.json > /vault/certs/zookeeper.crt
jq -r ".data.ca_chain[]"   /vault/certs/zookeeper.json > /vault/certs/ca-chain.crt
chmod 600 /vault/certs/zookeeper.key

openssl pkcs12 -export \
  -inkey    /vault/certs/zookeeper.key \
  -in       /vault/certs/zookeeper.crt \
  -certfile /vault/certs/ca-chain.crt \
  -name zookeeper \
  -out /vault/certs/zookeeper.p12 \
  -passout pass:changeit


vault write -format=json kafka-int-ca/issue/kafka-broker \
  common_name="nifi-1" \
  alt_names="localhost" \
  ip_sans="127.0.0.1" \
  > /vault/certs/nifi-1.json

jq -r ".data.private_key"  /vault/certs/nifi-1.json > /vault/certs/nifi-1.key
jq -r ".data.certificate"  /vault/certs/nifi-1.json > /vault/certs/nifi-1.crt
chmod 600 /vault/certs/nifi-1.key

openssl pkcs12 -export \
  -inkey    /vault/certs/nifi-1.key \
  -in       /vault/certs/nifi-1.crt \
  -certfile /vault/certs/ca-chain.crt \
  -name nifi-1 \
  -out /vault/certs/nifi-1.p12 \
  -passout pass:changeit


vault write -format=json kafka-int-ca/issue/kafka-broker \
  common_name="nifi-2" \
  alt_names="localhost" \
  ip_sans="127.0.0.1" \
  > /vault/certs/nifi-2.json

jq -r ".data.private_key"  /vault/certs/nifi-2.json > /vault/certs/nifi-2.key
jq -r ".data.certificate"  /vault/certs/nifi-2.json > /vault/certs/nifi-2.crt
chmod 600 /vault/certs/nifi-2.key

openssl pkcs12 -export \
  -inkey    /vault/certs/nifi-2.key \
  -in       /vault/certs/nifi-2.crt \
  -certfile /vault/certs/ca-chain.crt \
  -name nifi-2 \
  -out /vault/certs/nifi-2.p12 \
  -passout pass:changeit


vault write -format=json kafka-int-ca/issue/kafka-broker \
  common_name="nifi-3" \
  alt_names="localhost" \
  ip_sans="127.0.0.1" \
  > /vault/certs/nifi-3.json

jq -r ".data.private_key"  /vault/certs/nifi-3.json > /vault/certs/nifi-3.key
jq -r ".data.certificate"  /vault/certs/nifi-3.json > /vault/certs/nifi-3.crt
chmod 600 /vault/certs/nifi-3.key

openssl pkcs12 -export \
  -inkey    /vault/certs/nifi-3.key \
  -in       /vault/certs/nifi-3.crt \
  -certfile /vault/certs/ca-chain.crt \
  -name nifi-3 \
  -out /vault/certs/nifi-3.p12 \
  -passout pass:changeit

cd /opt/secrets

sudo keytool -import -alias root-ca -trustcacerts \
  -file root-ca.pem \
  -keystore nifi-cluster-truststore.jks \
  -storepass changeit -noprompt

sudo keytool -import -alias kafka-int-ca -trustcacerts \
  -file kafka-int-ca.pem \
  -keystore nifi-cluster-truststore.jks \
  -storepass changeit -noprompt