ARG BASE_CONTAINER=jupyter/scipy-notebook
FROM $BASE_CONTAINER


# Fix DL4006
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

USER root

RUN apt-get -y update && \
    apt-get -y install gnupg && \
    apt-get -y install curl

RUN wget https://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public -O public.key && \
	gpg --no-default-keyring --keyring ./adoptopenjdk-keyring.gpg --import ./public.key && \
	gpg --no-default-keyring --keyring ./adoptopenjdk-keyring.gpg --export --output adoptopenjdk-archive-keyring.gpg && \
	rm public.key && \
	rm adoptopenjdk-keyring.gpg && \
	mv adoptopenjdk-archive-keyring.gpg /usr/share/keyrings && \
	echo "deb [signed-by=/usr/share/keyrings/adoptopenjdk-archive-keyring.gpg] https://adoptopenjdk.jfrog.io/adoptopenjdk/deb bullseye main" | tee /etc/apt/sources.list.d/adoptopenjdk.list && \
	apt-get update && \
	apt-get install -y adoptopenjdk-8-hotspot zip vim
	
# Amazon Glue3 packages (captured from live running job : /opt/amazon folder)
RUN curl -SsL https://aws-glue-etl-artifacts.s3.amazonaws.com/glue-common/apache-maven-3.6.0-bin.tar.gz | tar -C /opt --warning=no-unknown-keyword -xzf -
RUN curl -SsL https://aws-glue-etl-artifacts.s3.amazonaws.com/glue-3.0/spark-3.1.1-amzn-0-bin-3.2.1-amzn-3.tgz | tar -C /opt --warning=no-unknown-keyword -xvf -

ADD ./glue3-opt-amazon.tgz /

# Env variables
ENV HOME=/home/jovyan
ENV M2_HOME=/opt/apache-maven-3.6.0
ENV JAVA_HOME=/usr/lib/jvm/adoptopenjdk-8-hotspot-amd64
ENV SPARK_HOME=/opt/spark-3.1.1-amzn-0-bin-3.2.1-amzn-3
ENV GLUE_HOME=/opt/amazon
ENV PATH=${M2_HOME}/bin:${GLUE_HOME}/bin:$PATH
ENV PYTHONPATH=${GLUE_HOME}/spark/jars/spark-core_2.12-3.1.1-amzn-0.jar:${GLUE_HOME}/spark/python/lib/pyspark.zip:${GLUE_HOME}/spark/python/lib/py4j-0.10.9-src.zip:${GLUE_HOME}/lib/python3.6/site-packages
ENV LD_LIBRARY_PATH=${GLUE_HOME}/lib/hadoop-lzo-native:${GLUE_HOME}/lib/hadoop-native/:${GLUE_HOME}/lib/glue-native
ENV SPARK_CONF_DIR=${GLUE_HOME}/conf


# to run spark in local mode, and enable s3a filesystem instead of EMR
RUN sed -i 's/spark.master jes/spark.master local/g' /opt/amazon/conf/spark-defaults.conf
RUN sed -i 's/spark.hadoop.fs.s3.impl com.amazon.ws.emr.hadoop.fs.EmrFileSystem/# spark.hadoop.fs.s3.impl com.amazon.ws.emr.hadoop.fs.EmrFileSystem/g' /opt/amazon/conf/spark-defaults.conf
RUN sed -i 's/# spark.hadoop.fs.s3.impl org.apache.hadoop.fs.s3a.S3AFileSystem/spark.hadoop.fs.s3.impl org.apache.hadoop.fs.s3a.S3AFileSystem/g' /opt/amazon/conf/spark-defaults.conf
RUN echo 'fs.s3a.aws.credentials.provider com.amazonaws.auth.DefaultAWSCredentialsProviderChain' >> /opt/amazon/conf/spark-defaults.conf

WORKDIR /usr/local
RUN ln -s "spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}" spark


#Kernel Sparks3
RUN mkdir -p $HOME/.local/share/jupyter/kernels/spark3
RUN chmod -R a+rw $HOME
COPY kernel.json $HOME/.local/share/jupyter/kernels/spark3/kernel.json

USER $NB_UID

# Clean-up some tmp files
RUN find /opt -name "._*" -type f -delete

WORKDIR $HOME
