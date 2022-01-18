FROM python:3.7.12-bullseye

# JDK 1.8 installation
RUN wget https://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public -O public.key && \
	gpg --no-default-keyring --keyring ./adoptopenjdk-keyring.gpg --import ./public.key && \
	gpg --no-default-keyring --keyring ./adoptopenjdk-keyring.gpg --export --output adoptopenjdk-archive-keyring.gpg && \
	rm public.key && \
	rm adoptopenjdk-keyring.gpg && \
	mv adoptopenjdk-archive-keyring.gpg /usr/share/keyrings && \
	echo "deb [signed-by=/usr/share/keyrings/adoptopenjdk-archive-keyring.gpg] https://adoptopenjdk.jfrog.io/adoptopenjdk/deb bullseye main" | tee /etc/apt/sources.list.d/adoptopenjdk.list && \
	apt-get update && \
	apt-get install -y adoptopenjdk-8-hotspot zip vim
	
# Spark / maven (still required?) / Amazon Glue3 packages (captured from live running job : /opt/amazon folder) and Zeppelin
RUN curl -SsL https://aws-glue-etl-artifacts.s3.amazonaws.com/glue-common/apache-maven-3.6.0-bin.tar.gz | tar -C /opt --warning=no-unknown-keyword -xzf -
RUN curl -SsL https://aws-glue-etl-artifacts.s3.amazonaws.com/glue-3.0/spark-3.1.1-amzn-0-bin-3.2.1-amzn-3.tgz | tar -C /opt --warning=no-unknown-keyword -xvf -
RUN curl -SsL https://mirror.checkdomain.de/apache/zeppelin/zeppelin-0.10.0/zeppelin-0.10.0-bin-all.tgz | tar -C /opt --warning=no-unknown-keyword -xzf -

ADD ./glue3-opt-amazon.tgz /

# Env variables
ENV M2_HOME=/opt/apache-maven-3.6.0
ENV JAVA_HOME=/usr/lib/jvm/adoptopenjdk-8-hotspot-amd64
ENV SPARK_HOME=/opt/spark-3.1.1-amzn-0-bin-3.2.1-amzn-3
ENV GLUE_HOME=/opt/amazon
ENV PATH=${M2_HOME}/bin:${GLUE_HOME}/bin:$PATH
ENV PYTHONPATH=${GLUE_HOME}/spark/jars/spark-core_2.12-3.1.1-amzn-0.jar:${GLUE_HOME}/spark/python/lib/pyspark.zip:${GLUE_HOME}/spark/python/lib/py4j-0.10.9-src.zip:${GLUE_HOME}/lib/python3.6/site-packages
ENV LD_LIBRARY_PATH=${GLUE_HOME}/lib/hadoop-lzo-native:${GLUE_HOME}/lib/hadoop-native/:${GLUE_HOME}/lib/glue-native
ENV SPARK_CONF_DIR=${GLUE_HOME}/conf
ENV ZEPPELIN_PORT 9001
ENV ZEPPELIN_ADDR 0.0.0.0

# additional python lib/bin
RUN pip install awscli pyspark==3.1.1 pytest boto3 delta-spark==1.0.0
RUN ln -s /usr/local/bin/pyspark ${SPARK_HOME}/bin/pyspark

# to run spark in local mode, and enable s3a filesystem instead of EMR
RUN sed -i 's/spark.master jes/spark.master local/g' /opt/amazon/conf/spark-defaults.conf
RUN sed -i 's/spark.hadoop.fs.s3.impl com.amazon.ws.emr.hadoop.fs.EmrFileSystem/# spark.hadoop.fs.s3.impl com.amazon.ws.emr.hadoop.fs.EmrFileSystem/g' /opt/amazon/conf/spark-defaults.conf
RUN sed -i 's/# spark.hadoop.fs.s3.impl org.apache.hadoop.fs.s3a.S3AFileSystem/spark.hadoop.fs.s3.impl org.apache.hadoop.fs.s3a.S3AFileSystem/g' /opt/amazon/conf/spark-defaults.conf

# Apply Spark interpreter config
ADD ./interpreter-0.10.0.json /opt/zeppelin-0.10.0-bin-all/conf/interpreter.json

# run scripts
RUN echo '#!/usr/bin/env bash \n\n ${SPARK_HOME}/bin/spark-submit --packages io.delta:delta-core_2.12:1.0.0 --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" $@' > $GLUE_HOME/bin/gluesparksubmit
RUN echo '#!/usr/bin/env bash \n\n ${SPARK_HOME}/bin/pyspark --packages io.delta:delta-core_2.12:1.0.0 --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" $@' > $GLUE_HOME/bin/gluepyspark
RUN echo '#!/usr/bin/env bash \n\n exec pytest "$@"' > $GLUE_HOME/bin/gluepytest
RUN chmod +x $GLUE_HOME/bin/gluesparksubmit && \
	chmod +x $GLUE_HOME/bin/gluepyspark && \
	chmod +x $GLUE_HOME/bin/gluepytest && \
	mkdir -p /opt/work

# Clean-up some tmp files
RUN find /opt -name "._*" -type f -delete

WORKDIR /opt/work
CMD ["/opt/zeppelin-0.10.0-bin-all/bin/zeppelin.sh"]

