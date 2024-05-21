FROM python:3.9

ENV MQ_VERSION=9.3.0.0
ENV MQ_HOME=/opt/mqm
ENV PATH=${PATH}:${MQ_HOME}/bin

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    unzip && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir ${MQ_HOME}

RUN curl -LO https://public.dhe.ibm.com/ibmdl/export/pub/software/websphere/messaging/mqdev/redist/${MQ_VERSION}-IBM-MQC-Redist-LinuxX64.tar.gz && \
    tar -zxvf ${MQ_VERSION}-IBM-MQC-Redist-LinuxX64.tar.gz -C ${MQ_HOME} && \
    rm ${MQ_VERSION}-IBM-MQC-Redist-LinuxX64.tar.gz

ENV LD_LIBRARY_PATH=${MQ_HOME}/lib64
ENV MQSAMP=${MQ_HOME}/samp

WORKDIR /opt/mq-samples
COPY src src/
COPY requirements.txt ./
RUN pip install -r requirements.txt
