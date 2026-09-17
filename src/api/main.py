# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
# pyrefly: ignore [missing-import]
import easyocr

from src.api.utils.config import settings
from src.api.routers import bula
from src.api.utils.logger import get_logger

logger = get_logger("API")

# O asynccontextmanager cria um "Lifespan" (ciclo de vida) para a aplicação FastAPI.
# O código ANTES do `yield` é executado na inicialização do servidor.
# O código DEPOIS do `yield` é executado no desligamento (Ctrl+C).
# Isso é perfeito para carregar modelos de Machine Learning super pesados na memória uma vez só.
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Inicializando o modelo do EasyOCR (pode demorar na primeira vez)...")
    # Salva o modelo na memória global `state` do FastAPI para uso nas requisições.
    app.state.ocr_reader = easyocr.Reader(['pt'])
    logger.info("EasyOCR carregado com sucesso.")
    
    yield # O servidor inicia aqui, aceitando requisições.
    
    logger.info("Desligando e limpando recursos do OCR...")
    # Limpeza de memória no desligamento.
    app.state.ocr_reader = None

# Instancia a aplicação principal FastAPI
app = FastAPI(
    title="API - Simplificação de Bulas",
    description="Fase 2 do projeto de OCR e LLM para simplificação de bulas de medicamentos",
    version="1.0.0",
    lifespan=lifespan # Injeta a função de ciclo de vida criada acima
)

# CORS (Cross-Origin Resource Sharing) 
# É o middleware de segurança que decide quais origens (outros domínios/apps) 
# têm permissão para consumir esta API (evita invasões e scripts de terceiros não autorizados).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Acopla as rotas específicas da Bula no sistema central da API
app.include_router(bula.router)

# Rota simples para balanceadores de carga e orquestradores (como Docker) saberem 
# que o sistema ligou com sucesso e está operante.
@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    # hasattr verifica se "ocr_reader" existe no objeto `app.state`.
    ocr_loaded = hasattr(app.state, "ocr_reader") and app.state.ocr_reader is not None
    return {"status": "ok", "ocr_loaded": ocr_loaded}
