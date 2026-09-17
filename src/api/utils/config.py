import os
import json

class Settings:
    """
    Classe central de configurações do projeto.
    Utilizamos variáveis de ambiente (os.environ) para garantir que segredos 
    (como senhas, chaves de API e IPs de banco) nunca fiquem expostos no código-fonte.
    """
    
    # Busca a variável CORS_ORIGINS no ambiente. 
    # O CORS (Cross-Origin Resource Sharing) dita quais sites externos podem fazer chamadas para esta API.
    # Exemplo seguro para produção: '["https://meuappflutter.com", "http://localhost:3000"]'
    _cors_env = os.environ.get("CORS_ORIGINS", '["*"]')
    
    try:
        # Tenta transformar a string em uma lista Python válida
        cors_origins = json.loads(_cors_env)
    except Exception:
        # Se falhar (ex: string mal formatada), libera o acesso para todo mundo ("*") para não quebrar a API em Dev
        cors_origins = ["*"]
        
    # Limite máximo de tamanho das imagens de bulas recebidas pela API (evita ataques de negação de serviço - DDoS).
    max_upload_size_mb = int(os.environ.get("MAX_UPLOAD_SIZE_MB", "5"))

# Instancia o objeto globalmente para ser importado de forma simples em qualquer lugar do projeto
settings = Settings()
