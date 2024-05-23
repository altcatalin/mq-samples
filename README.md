# mq-samples

## How to use

### Run IBM MQ with Docker

```shell
# build Docker image
# https://community.ibm.com/community/user/integration/blogs/richard-coppen/2023/06/30/ibm-mq-9330-container-image-now-available-for-appl

# prepare .env
cp sample.env .env

# start containers
docker compose up -d
```

### Run samples

```shell
# build Docker image
docker build --tag mq-samples .

# Apple Silicon
docker buildx build --platform linux/amd64 --tag mq-samples .

# run the TLS sample program - replace [[PLACEHOLDER]] with real values
# https://www.ibm.com/docs/en/ibm-mq/9.3?topic=program-running-tls-sample
docker run -it --rm \
    -v $(PWD)/keys:/opt/mq-samples/keys:ro \
    mq-samples /opt/mqm/samp/bin/amqssslc \
        -m [[QMGR]] \
        -c '[[CHANNEL]]' \
        -x 'host.docker.internal(1414)' \
        -k [[KEY_REPOSITORY]] \
        -s 'TLS_RSA_WITH_AES_128_CBC_SHA256' \
        -l '[[CERT_LABEL]]'

# put random messages on a queue - replace [[PLACEHOLDER]] with real values
docker run -it --rm \
    -v $(PWD)/keys:/opt/mq-samples/keys:ro \
    -e CONNECTION='host.docker.internal(1414)' \
    -e QMGR=[[QMGR]] \
    -e CHANNEL='[[CHANNEL]]' \
    -e QUEUE='[[QUEUE]]' \
    -e KEY_REPOSITORY='[[KEY_REPOSITORY]]' \
    -e CERT_LABEL='[[CERT_LABEL]]' \
    mq-samples python src/put.py

# get messages from a queue - replace [[PLACEHOLDER]] with real values
docker run -it --rm \
    -v $(PWD)/keys:/opt/mq-samples/keys:ro \
    -e CONNECTION='host.docker.internal(1414)' \
    -e QMGR=[[QMGR]] \
    -e CHANNEL='[[CHANNEL]]' \
    -e QUEUE='[[QUEUE]]' \
    -e KEY_REPOSITORY='[[KEY_REPOSITORY]]' \
    -e CERT_LABEL='[[CERT_LABEL]]' \
    mq-samples python src/get.py
```
