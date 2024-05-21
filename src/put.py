import os
import base64
import pathlib
import logging
import time
import pymqi
from dotenv import dotenv_values

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

config = {
    "connection": os.getenv("CONNECTION", "localhost(1414)"),
    "key_repository": os.getenv("KEY_REPOSITORY"),
    "cert_label": os.getenv("CERT_LABEL"),
    "qmgr": os.getenv("QMGR"),
    "channel": os.getenv("CHANNEL"),
    "queue": os.getenv("QUEUE")
}

logging.info(f"Connect to '{config['qmgr']}' queue manager from '{config['connection']}' via '{config['channel']}' channel")
logging.info(f"Use TLS with 'TLS_RSA_WITH_AES_128_CBC_SHA256' cipher spec and '{config['key_repository']}' key store")
logging.info(f"Use mTLS with '{config['cert_label']}' certificate")

os.environ['MQAPPLNAME'] = pathlib.Path(__file__).stem

cd = pymqi.CD()
cd.ConnectionName = config['connection'].encode(encoding='UTF-8')
cd.ChannelName = config['channel'].encode(encoding='UTF-8')
cd.SSLCipherSpec = 'TLS_RSA_WITH_AES_128_CBC_SHA256'.encode(encoding='UTF-8')
cd.SSLClientAuth = pymqi.CMQXC.MQSCA_REQUIRED

sco = pymqi.SCO()
sco.KeyRepository = config['key_repository'].encode(encoding='UTF-8')
sco.CertificateLabel = config['cert_label'].encode(encoding='UTF-8')

opts = pymqi.CMQC.MQCNO_RECONNECT_Q_MGR

qmgr = pymqi.QueueManager(None)
qmgr.connect_with_options(config['qmgr'], cd=cd, sco=sco, opts=opts)
queue = pymqi.Queue(qmgr, config['queue'])

while True:
    message = f"Hello {base64.urlsafe_b64encode(os.urandom(32)).decode()}!"
    logging.info(f"Put message '{message}' in '{config['queue']}' queue")
    queue.put(message)
    time.sleep(2)

queue.close()
qmgr.disconnect()
