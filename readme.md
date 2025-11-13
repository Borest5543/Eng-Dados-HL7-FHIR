# **Engenheiro de Dados - Especialista em HL7 FHIR**

Este projeto é referente a um teste técnico disponível em: https://github.com/wandersondsm/teste_fhir?tab=readme-ov-file

---

## Este projeto conta com ambiente completo em Docker para:

- Hospedar um servidor **HAPI FHIR** conectado a **PostgreSQL**  
- Orquestrar um pipeline de ingestão com **Airflow**  
- Processar um arquivo CSV de pacientes com **Spark**, gerando recursos **FHIR Patient** (perfil `BRIndividuo`) e enviando-os ao servidor FHIR

---

## Arquitetura (resumo)

- **PostgreSQL**
  - Banco de dados `fhir` para persistência do HAPI FHIR
  - Banco de dados `airflow` para metadados do Airflow

- **HAPI FHIR**
  - Servidor FHIR R4 configurado para usar o PostgreSQL
  - Endpoint principal: http://localhost:8583/fhir

- **Airflow**
  - Orquestração da DAG `dag_patient_ingest_spark`
  - UI: http://localhost:8581

- **Spark**
  - Executa o script `spark_app/patient_ingest.py`
  - Lê o arquivo `data/patients.csv`
  - Constrói JSON FHIR Patient a partir de cada linha e faz `POST` no servidor FHIR

![alt text](image.png)
---

## Fluxo de Dados

1. O **container Postgres** é iniciado.
2. O **HAPI FHIR** sobe apontando para o banco `fhir` no Postgres.
3. O **Airflow** inicia e carrega a DAG `dag_patient_ingest_spark`.
4. Ao executar a DAG:
   - O Airflow chama um **SparkSubmitOperator**, que executa `patient_ingest.py`.
   - O script:
     - Lê cada linha do `patients.csv`.
     - Monta um recurso **FHIR Patient** compatível com o perfil `BRIndividuo`.
     - Envia um `POST /fhir/Patient` para o servidor HAPI FHIR.
---

## Pré-requisitos

- **Docker** e **Docker Compose** instalados
- Portas livres:
  - `8581` (Airflow)
  - `8583` (HAPI FHIR)

---

## Como executar

1. **Subir os serviços**

   ```bash
   docker compose up -d --build
   ```

2. **Acessar o Airflow**

	- URL: http://localhost:8581
	- Usuário padrão: admin
	- Senha padrão: admin

3. **Executar a DAG**

	- No menu do Airflow, localize a DAG: dag_patient_ingest_spark
	- Clique em Trigger DAG para iniciar a execução

4. **Conferir os pacientes no servidor FHIR**

	- Via Swagger/Swagger UI:

		http://localhost:8583/fhir/swagger-ui/?page=Patient#/Patient/get_Patient

	- Via curl:
		```bash
		curl -H "Accept: application/fhir+json"http://localhost:8583/fhir/Patient?_count=5&_pretty=tru
		```

---

## **Observações**
	
1. Como a fonte de dados é única nesse teste, não houve a necessidade de utilizar o Kafka. Porém em um cenário onde existem diversas fontes de dados interagindo dimultaneamente, o Kafka seria crucial para organizar as filas de interações.