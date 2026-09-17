from pydantic import BaseModel, Field
from typing import Optional, List
from src.core.modelos.bula import BulaSimplificada

# O Pydantic é o motor de validação de dados por trás do FastAPI.
# Ao definirmos classes herdando de BaseModel, o FastAPI automaticamente:
# 1. Converte a saída (Dicionários Python) em JSON.
# 2. Gera a documentação automática interativa do Swagger UI (http://localhost:8000/docs).
# 3. Garante (Type Hinting) que os dados que saem têm exatamente esse formato, falhando com segurança caso contrário.

class BulaSimplificadaResponse(BaseModel):
    """
    Representa a estrutura final do JSON que o aplicativo móvel (Flutter) 
    vai receber após a Bula passar pelo OCR e ser processada pelo Gemini.
    """
    
    medicamento: str = Field(description="Nome do medicamento extraído da bula")
    para_que_serve: str = Field(description="Para que este medicamento é indicado")
    como_usar: str = Field(description="Como o medicamento deve ser utilizado (posologia)")
    contraindicacoes: str = Field(description="Principais contraindicações")
    efeitos_colaterais: str = Field(description="Principais efeitos colaterais e alertas")
    
    # O uso de 'default=' em um Field permite injetar informações fixas em todas as respostas da API.
    # O Disclaimer Médico é vital para projetos de saúde com IA (Software as a Medical Device),
    # protegendo a aplicação contra responsabilidades clínicas diretas.
    disclaimer_medico: str = Field(
        default="ATENÇÃO: Este texto foi gerado por Inteligência Artificial para fins de simplificação "
                "e não substitui a avaliação de um profissional de saúde. Sempre consulte um médico ou farmacêutico.",
        description="Aviso legal sobre o uso da IA para fins médicos."
    )

class ErrorResponse(BaseModel):
    """
    Modelo genérico para padronizar as mensagens de erro retornadas pela API.
    """
    detail: str
