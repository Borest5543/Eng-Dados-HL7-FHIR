# ===============================
# 🧩 Base universal (Airflow + Spark + Kafka client)
# ===============================
FROM python:3.12-slim-bookworm

LABEL maintainer="Tulio Augusto"
LABEL description="Imagem universal com Airflow, Spark e Kafka para pipelines HL7/FHIR"

# ===============================
# 🧰 Dependências do sistema
# ===============================
USER root
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk \
    wget \
    curl \
    procps \
    postgresql-client \
    bash \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ===============================
# ⚡ Instala Apache Spark
# ===============================
ENV SPARK_VERSION=3.5.2
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$PATH:$SPARK_HOME/bin:$JAVA_HOME/bin

RUN mkdir -p ${SPARK_HOME} && \
    wget -q https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz -O /tmp/spark.tgz && \
    tar -xzf /tmp/spark.tgz -C /opt && \
    mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}/* ${SPARK_HOME}/ && \
    rm -rf /tmp/spark.tgz

# ===============================
# 🧩 Dependências Python
# ===============================
COPY requirements.txt /tmp/requirements.txt

# 🚀 Instala dependências Python compatíveis com Python 3.12
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# ===============================
# 🏗️ Configura diretórios padrão
# ===============================
WORKDIR /opt/app
ENV PYTHONUNBUFFERED=1

CMD ["bash"]
