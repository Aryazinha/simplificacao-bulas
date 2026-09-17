# pyrefly: ignore [missing-import]
from fastapi import APIRouter, UploadFile, File, Request, HTTPException
from src.api.services.ocr import extrair_texto_da_imagem
from src.api.services.llm import simplificar_texto
from src.api.schemas.bula import BulaSimplificadaResponse
from pydantic import BaseModel
from src.api.utils.logger import get_logger

logger = get_logger("Router_Bula")
router = APIRouter(prefix="/api/v1/bula", tags=["Bula"])

class ExtrairResponse(BaseModel):
    texto: str

@router.post("/extrair", response_model=ExtrairResponse)
async def extrair_texto(request: Request, file: UploadFile = File(...)):
    """Endpoint de debug para testar apenas a fase de extração OCR."""
    reader = getattr(request.app.state, "ocr_reader", None)
    if reader is None:
        raise HTTPException(status_code=503, detail="Serviço de OCR não está inicializado.")
        
    texto = await extrair_texto_da_imagem(file, reader)
    return {"texto": texto}

@router.post("/simplificar", response_model=BulaSimplificadaResponse)
async def simplificar_bula(request: Request, file: UploadFile = File(...)):
    """Endpoint principal da Fase 2. Realiza o OCR e simplifica com LLM."""
    reader = getattr(request.app.state, "ocr_reader", None)
    if reader is None:
        raise HTTPException(status_code=503, detail="Serviço de OCR não está inicializado.")
        
    logger.info("Iniciando requisição de simplificação de bula...")
    
    # Etapa 1: Extrair texto da imagem
    texto_ocr = await extrair_texto_da_imagem(file, reader)
    logger.info(f"OCR finalizado. Tamanho do texto extraído: {len(texto_ocr)} caracteres.")
    
    if len(texto_ocr) < 50:
        logger.warning("Texto muito curto extraído pelo OCR.")
        raise HTTPException(status_code=422, detail="Texto extraído é muito curto. Tem certeza de que enviou uma foto legível de uma bula?")
        
    # Etapa 2: Simplificar usando o LLM
    logger.info("Enviando texto OCR para o LLM...")
    json_bula = await simplificar_texto(texto_ocr)
    
    # Etapa 3: Construir a resposta
    try:
        # Passar os dados dinâmicos (disclaimer_medico será preenchido pelo default)
        resposta_final = BulaSimplificadaResponse(**json_bula)
    except Exception as e:
        logger.error(f"Erro de validação do Pydantic no retorno do LLM: {e}")
        raise HTTPException(status_code=502, detail="A resposta da IA não está no formato esperado.")
        
    logger.info("Simplificação concluída com sucesso!")
    return resposta_final
