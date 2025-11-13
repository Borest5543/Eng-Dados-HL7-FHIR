from pyspark.sql import SparkSession
import requests
import json
from datetime import datetime
import sys

# 🌐 Endpoint FHIR local
FHIR_URL = "http://fhir-server:8080/fhir/Patient"

# ======================================================
# 🔧 Funções auxiliares
# ======================================================
def normalizar_genero(valor):
    """Converte valor textual em código FHIR."""
    if not valor:
        return "unknown"
    valor = valor.strip().lower()
    if valor.startswith("f"):
        return "female"
    elif valor.startswith("m"):
        return "male"
    return "unknown"


def formatar_data(data_str):
    """Converte data do formato dd/mm/yyyy → yyyy-mm-dd"""
    try:
        return datetime.strptime(data_str.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
    except Exception:
        return None
    
def formatar_pais(pais):
    """Converte valor textual em código ISO 3166-1. Só para o Brasil."""
    if not pais:
        return "unknown"
    pais = pais.strip().lower()
    if pais in ("basil", "brazil"):
        return "BRA"
    return "unknown"


# ======================================================
# 🧬 Montagem do recurso FHIR (perfil BR-INDIVIDUO)
# ======================================================
def criar_recurso_fhir(row):
    """Converte uma linha CSV em JSON no formato FHIR Patient."""
    
    paciente = {
    "resourceType": "Patient",
    "meta": {
        "profile": [
        "http://www.saude.gov.br/fhir/r4/StructureDefinition/BRIndividuo-1.0"
        ]
    },
    "extension": [
    {
        "url": "http://hl7.org/fhir/StructureDefinition/patient-birthPlace",
        "valueAddress": {
        "country": "Brasil"
        }
    }
    ],
    "identifier": [
        {
        "use": "official",
        "type": {
            "coding": [
            {
                "system": "http://www.saude.gov.br/fhir/r4/CodeSystem/BRTipoDocumentoIndividuo-1.0",
                "code": "TAX",
                "display": "Número de inscrição no cadastro de pessoa física"
            }
            ],
            "text": "CPF"
        },
        "system": "http://gov.br/cpf",
        "value": (row.get("CPF") or "").replace(".", "").replace("-", "").strip()
        }
    ],
    "name": [
        {
        "use": "official",
        "text": (row.get("Nome") or "").strip()
        }
    ],
    "text": [
        {
        "div": (row.get("Observação") or "").strip()
        }
    ],
    "telecom": [
        {
        "system": "phone",
        "value": (row.get("Telefone") or "").strip(),
        }
    ],
    "gender": normalizar_genero((row.get("G�nero") or "unknown")),
    "birthDate": formatar_data(row.get("Data de Nascimento", "")),
    }

    if observacao:
        paciente["note"]= [
            {
                "text": observacao
            }
        ]

    return paciente


# ======================================================
# 🚀 Envio para o servidor FHIR
# ======================================================
def enviar_para_fhir(paciente):
    """Faz o POST do recurso Patient no servidor FHIR."""
    headers = {"Content-Type": "application/fhir+json"}

    try:
        response = requests.post(FHIR_URL, headers=headers, data=json.dumps(paciente))

        if response.status_code in (200, 201):
            print(f"✅ Paciente enviado: {paciente['name'][0]['text']}")
        else:
            print(f"⚠️ Erro {response.status_code} ao enviar {paciente['name'][0]['text']}: {response.text[:200]}")

    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor FHIR.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


# ======================================================
# 🎯 Main
# ======================================================
def main(csv_path):
    spark = (
        SparkSession.builder
        .appName("Enviar pacientes FHIR")
        .getOrCreate()
    )

    df = (
        spark.read
        .option("header", True)
        .option("encoding", "utf-8")  # corrige CSV com acentos
        .csv(csv_path)
    )

    pacientes = df.collect()
    for row in pacientes:
        paciente = criar_recurso_fhir(row.asDict())
        enviar_para_fhir(paciente)

    spark.stop()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Informe o caminho do CSV.")
        sys.exit(1)
    main(sys.argv[1])
