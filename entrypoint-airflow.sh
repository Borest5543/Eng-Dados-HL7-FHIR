#!/bin/bash
set -e  # encerra o script se ocorrer qualquer erro

echo "⏳ [Airflow] Aguardando Postgres..."
# espera até o banco responder
timeout 60 bash -c 'until pg_isready -h postgres -p 5432 -U fhir_user; do sleep 2; done'

echo "🚀 [Airflow] Inicializando banco..."
airflow db check || airflow db init
airflow db migrate

echo "👤 [Airflow] Criando usuário admin (se não existir)..."
# o || true impede o script de quebrar se o usuário já existir
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin || true

echo '🔌 Recriando conexão Spark...';
airflow connections delete spark_default || true;
airflow connections add spark_default \
  --conn-type spark \
  --conn-host spark://spark-master:7077 \
  --conn-extra '{"deploy_mode": "client", "spark_home": "/opt/spark"}' || true;


echo "✅ [Airflow] Inicialização concluída, iniciando serviços..."
# inicia o scheduler em background e o webserver em primeiro plano
airflow scheduler &
exec airflow webserver
