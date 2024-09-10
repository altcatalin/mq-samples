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

docker run -it --rm \
    -v $(PWD)/src:/opt/mq-samples/src:ro \
    -e CONNECTION='host.docker.internal(1414)' \
    -e QMGR=QM1 \
    -e CHANNEL='DEV.APP.SVRCONN' \
    -e QUEUE='DEV.QUEUE.1_3.QM2' \
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

docker run -it --rm \
    -v $(PWD)/src:/opt/mq-samples/src:ro \
    -e CONNECTION='host.docker.internal(1414)' \
    -e QMGR=QM1 \
    -e CHANNEL='DEV.APP.SVRCONN' \
    -e QUEUE='DEV.QUEUE.1' \
    mq-samples python src/get.py

# create keystore
export OPENSSL_PASSWORD=$(openssl rand -hex 8)
mkdir keys/qm1
openssl pkcs12 -export -out keys/qm1/app.p12 -inkey keys/qm1/app.key -in keys/qm1/app.pem -passout env:OPENSSL_PASSWORD
runmqakm -keydb -create -type cms -genpw -stash -db keys/qm1/key.kdb
runmqakm -cert -import -file keys/qm1/app.p12 -target keys/qm1/key.kdb -target_type pkcs12 -target_stashed -pw "$OPENSSL_PASSWORD"
runmqakm -cert -add -db keys/qm1/key.kdb -stashed -file keys/qm1/ca.pem
runmqakm -cert -list -db keys/qm1/key.kdb -stashed
```
