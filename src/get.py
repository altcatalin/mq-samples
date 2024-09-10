import os
import pathlib
import logging
import time
import pymqi
import random
from dotenv import dotenv_values
import argparse

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

config = {
    "connection": os.getenv("CONNECTION", "localhost(1414)"),
    "key_repository": os.getenv("KEY_REPOSITORY"),
    "cert_label": os.getenv("CERT_LABEL"),
    "qmgr": os.getenv("QMGR"),
    "channel": os.getenv("CHANNEL"),
    "queue": os.getenv("QUEUE"),
    "user": os.getenv("MQ_USER", "app"),
    "password": os.getenv("MQ_USER_PASSWORD", "passw0rd"),
}

parser = argparse.ArgumentParser()
parser.add_argument("--max_sleep", type=int, default=3, help="Maximum sleep time in seconds")
args = parser.parse_args()

logging.info(f"Connect to '{config['qmgr']}' queue manager from '{config['connection']}' via '{config['channel']}' channel")

config['mtls'] = config['key_repository'] and config['cert_label']
os.environ['MQAPPLNAME'] = pathlib.Path(__file__).stem

cd = pymqi.CD()
cd.ConnectionName = config['connection'].encode(encoding='UTF-8')
cd.ChannelName = config['channel'].encode(encoding='UTF-8')

sco = pymqi.SCO()

if config['mtls']:
    logging.info(f"Use TLS with 'TLS_RSA_WITH_AES_128_CBC_SHA256' cipher spec and '{config['key_repository']}' key store")
    logging.info(f"Use mTLS with '{config['cert_label']}' certificate")

    cd.SSLCipherSpec = 'TLS_RSA_WITH_AES_128_CBC_SHA256'.encode(encoding='UTF-8')
    cd.SSLClientAuth = pymqi.CMQXC.MQSCA_REQUIRED

    sco.KeyRepository = config['key_repository'].encode(encoding='UTF-8')
    sco.CertificateLabel = config['cert_label'].encode(encoding='UTF-8')

    config['user'] = None
    config['password'] = None

md = pymqi.MD()

gmo = pymqi.GMO()
gmo.Options = pymqi.CMQC.MQGMO_WAIT | pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING
gmo.WaitInterval = 5000

opts = pymqi.CMQC.MQCNO_RECONNECT_Q_MGR

qmgr = pymqi.QueueManager(None)
qmgr.connect_with_options(config['qmgr'], user=config['user'], password=config['password'], cd=cd, sco=sco, opts=opts)
queue = pymqi.Queue(qmgr, config['queue'])

while True:
    try:
        message = queue.get(None, md, gmo)
        logging.info(f"GET -> {config['qmgr']}:{config['queue']} -> {message} ({md.MsgId.hex()})")

        md.MsgId = pymqi.CMQC.MQMI_NONE
        md.CorrelId = pymqi.CMQC.MQCI_NONE
        md.GroupId = pymqi.CMQC.MQGI_NONE

        sleep = random.randint(1, args.max_sleep)
        logging.info(f"Sleep for {sleep} second")
        time.sleep(sleep)

    except pymqi.MQMIError as e:
        if e.comp == pymqi.CMQC.MQCC_FAILED and e.reason == pymqi.CMQC.MQRC_NO_MSG_AVAILABLE:
            logging.info(f"No messages in '{config['qmgr']}:{config['queue']}' queue")

            sleep = random.randint(1, args.max_sleep)
            logging.info(f"Sleep for {sleep} seconds")
            time.sleep(sleep)

            pass
        else:
            raise

queue.close()
qmgr.disconnect()
