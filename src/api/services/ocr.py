import tempfile
import os
import shutil
from fastapi import UploadFile, HTTPException
from fastapi.concurrency import run_in_threadpool
import easyocr
from pathlib import Path

from src.api.utils.logger import get_logger
from src.ocr.bula import escanear_bula
from src.api.utils.config import settings

logger = get_logger("OCR_Service")

async def extrair_texto_da_imagem(file: UploadFile, reader: easyocr.Reader) -> str:
    # Validação de mime-type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="O arquivo enviado não é uma imagem válida. Envie JPEG ou PNG.")
        
    # Verificar o tamanho do arquivo lendo tudo (já que precisamos gravar)
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(status_code=413, detail=f"Arquivo excede o limite de {settings.max_upload_size_mb}MB.")
    
    # Criar um arquivo temporário
    temp_fd, temp_path = tempfile.mkstemp(suffix=".jpg")
    try:
        with os.fdopen(temp_fd, "wb") as f:
            shutil.copyfileobj(file.file, f)
            
        logger.info(f"Iniciando OCR no arquivo temporário: {temp_path}")
        
        texto = await run_in_threadpool(
            escanear_bula,
            caminho_imagem=temp_path,
            colunas=2,
            salvar_debug=False,
            reader=reader
        )
        
        if not texto or not texto.strip():
            raise HTTPException(status_code=422, detail="Nenhum texto pôde ser extraído da imagem fornecida.")
            
        return texto.strip()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no processamento do OCR: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a imagem com OCR.")
    finally:
        try:
            os.remove(temp_path)
            logger.info(f"Arquivo temporário {temp_path} removido.")
        except Exception as e:
            logger.error(f"Falha ao remover arquivo temporário {temp_path}: {e}")
