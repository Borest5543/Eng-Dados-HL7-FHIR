# **Engenheiro de Dados — Especialista em HL7 FHIR**

Este projeto é referente ao teste técnico disponível em:
https://github.com/wandersondsm/teste_fhir?tab=readme-ov-file

---

## Stack em Docker

- **HAPI FHIR JPA Server (R4)** persistido em **PostgreSQL**
- **Airflow** para orquestração da ingestão
- **Spark** para processar o CSV e gerar recursos FHIR

---

## Arquitetura

- **PostgreSQL**
  - Banco `fhir` (persistência do HAPI FHIR JPA Server)
  - Banco `airflow` (metadados do Airflow)

- **HAPI FHIR JPA Server (R4)**
  - Base URL: http://localhost:8583/fhir/ 
  - Swagger UI: http://localhost:8583/fhir/swagger-ui/?page=Patient#/Patient/get_Patient

- **Airflow**
  - DAG: `dag_patient_ingest_spark`
  - UI (Webserver): http://localhost:8581
  - Usuário: `admin`
  - Senha: `admin`

- **Spark**
  - Executa `spark_app/patient_ingest.py`
  - Lê `data/patients.csv`
  - Constrói recursos **FHIR Patient** (perfil `BRIndividuo`) e envia ao servidor

  ![Imagem do WhatsApp de 2025-11-13 à(s) 09 41 25_99aa7379](https://github.com/user-attachments/assets/ca93fcf2-75a3-4a0e-93ca-a4d90cd9b2df)


---

## Fluxo de Dados

1. Sobe o **PostgreSQL**.
2. O **HAPI FHIR JPA Server** inicia apontando para o banco `fhir`.
3. O **Airflow** inicia e disponibiliza a DAG `dag_patient_ingest_spark`.
4. Ao acionar a DAG:
   - O `SparkSubmitOperator` executa `spark_app/patient_ingest.py`.
   - O script lê o CSV, monta os recursos FHIR e envia ao HAPI:

---

## Pré-requisitos

- **Docker** e **Docker Compose**
- Portas livres:
  - `8581` (Airflow)
  - `8583` (HAPI FHIR)

---

## Como executar

1. **Subir os serviços**
      ```
      docker compose up -d --build
      ```


2. **Executar a DAG**
    - Acessar o Airflow (http://localhost:8581) e executar a dag.


3. **Conferir ETL**
    - HAPI
      - Acessar o HAPI FHIR (http://localhost:8583/fhir/swagger-ui/?page=Patient#/Patient/get_Patient) e executar a requisição GET


    - Banco de dados
      - Conecte à um banco de dados.
        - Host: `localhost`
        - Porta: `5111`
        - Banco: `fhir`
        - User: `fhir_user`
        - Pass: `fhir_pass`

      - Executar a seguinte querie:
        ```sql
        WITH
        NOME AS (
          SELECT DISTINCT res_id, sp_value_exact
          FROM hfj_spidx_string
        ),
        GENERO AS (
          SELECT res_id, sp_value
          FROM hfj_spidx_token
          WHERE sp_name = 'gender'
        ),
        PHONE AS (
          SELECT DISTINCT res_id, sp_value
          FROM hfj_spidx_token
          WHERE sp_name = 'telecom'
            AND sp_system = 'phone'
            AND res_type  = 'Patient'
        ),
        DATA_NAS AS (
          SELECT res_id, sp_value_high
          FROM hfj_spidx_date
          WHERE sp_name = 'birthdate'
        ),
        PAIS_NASCIMENTO AS (
          SELECT
            v.res_id,
            ext_elem->'valueCodeableConcept'->'coding'->0->>'display' AS pais_nascimento
          FROM hfj_resource r
          JOIN hfj_res_ver v
            ON v.res_id = r.res_id
          JOIN LATERAL jsonb_array_elements(v.res_text_vc::jsonb->'extension') AS ext_elem
            ON TRUE
          WHERE r.res_type = 'Patient'
            AND ext_elem->>'url' = 'http://www.saude.gov.br/fhir/r4/StructureDefinition/BRIndividuo-1.0#birthCountry'
        )
        SELECT
          NOME.res_id                         AS Id,
          NOME.sp_value_exact                 AS Nome,
          GENERO.sp_value                     AS Genero,
          DATA_NAS.sp_value_high              AS Data_Nascimento,
          PHONE.sp_value                      AS Telefone,
          PAIS_NASCIMENTO.pais_nascimento     AS Pais_Nascimento
        FROM NOME
        INNER JOIN GENERO         ON NOME.res_id = GENERO.res_id
        INNER JOIN PHONE          ON NOME.res_id = PHONE.res_id
        INNER JOIN DATA_NAS       ON NOME.res_id = DATA_NAS.res_id
        LEFT  JOIN PAIS_NASCIMENTO ON NOME.res_id = PAIS_NASCIMENTO.res_id;
        ```

        ![Imagem do WhatsApp de 2025-11-13 à(s) 09 42 35_a5e4c8a2](https://github.com/user-attachments/assets/1bc48e1b-f846-4241-b39c-87bdcff2ae18)
