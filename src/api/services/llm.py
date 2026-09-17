import json
import os
# pyrefly: ignore [missing-import]
from fastapi import HTTPException
# pyrefly: ignore [missing-import]
from fastapi.concurrency import run_in_threadpool
from google import genai
from google.genai import types

from src.api.utils.logger import get_logger
from src.core.llm.prompts import montar_prompt_simplificacao
from src.core.modelos.bula import BulaSimplificada

logger = get_logger("LLM_Service")

async def simplificar_texto(texto_ocr: str, modelo: str = "gemini-2.5-flash") -> dict:
    """
    Recebe o texto bruto extraído da imagem pelo OCR e utiliza o modelo Gemini 
    para simplificar e estruturar os dados.
    """
    # os.environ.get() busca a variável de ambiente. Se não existir, retorna a string vazia ("").
    chave_api = os.environ.get("GEMINI_API_KEY", "").strip()
    if not chave_api:
        logger.error("GEMINI_API_KEY não configurada.")
        # HTTPException interrompe o fluxo e retorna um erro HTTP específico para o cliente (ex: 500 Internal Server Error)
        raise HTTPException(status_code=500, detail="Chave de API do LLM não configurada no servidor.")

    logger.info(f"Enviando texto OCR para o modelo Gemini ({modelo})...")
    
    try:
        # Instancia o cliente da API do Google GenAI utilizando a chave fornecida
        client = genai.Client(api_key=chave_api)
        
        # Como o cliente do Gemini faz requisições de rede síncronas que podem demorar, 
        # nós encapsulamos essa chamada em uma função separada.
        def call_gemini():
            return client.models.generate_content(
                model=modelo,
                contents=montar_prompt_simplificacao(texto_ocr),
                # GenerateContentConfig força o modelo a seguir instruções específicas.
                # Aqui obrigamos que a resposta seja no formato JSON e siga o esquema Pydantic "BulaSimplificada".
                # A temperatura baixa (0.1) faz o modelo ser mais determinístico e menos "criativo", ideal para dados médicos.
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=BulaSimplificada,
                    temperature=0.1,
                ),
            )
            
        # run_in_threadpool envia a função "call_gemini" para rodar em uma thread separada (background worker).
        # Isso impede que o FastAPI (que roda em um único loop de eventos "event loop") fique travado
        # esperando a resposta do Google, permitindo que a API continue atendendo outros usuários.
        resposta = await run_in_threadpool(call_gemini)
        
    except Exception as e:
        logger.error(f"Erro na comunicação com o Gemini: {e}")
        # 502 Bad Gateway indica que a nossa API tentou contatar a API do Google, mas algo deu errado lá.
        raise HTTPException(status_code=502, detail="Falha ao se comunicar com o serviço de Inteligência Artificial.")

    texto_resposta = (resposta.text or "").strip()
    if not texto_resposta:
        logger.error("Gemini retornou resposta vazia.")
        raise HTTPException(status_code=502, detail="O serviço de IA retornou uma resposta vazia.")

    try:
        # json.loads() converte a string JSON retornada pelo Gemini em um Dicionário Python.
        json_obj = json.loads(texto_resposta)
        return json_obj
    except json.JSONDecodeError:
        logger.error("Gemini retornou um JSON inválido.")
        raise HTTPException(status_code=502, detail="O serviço de IA não retornou os dados no formato esperado.")
