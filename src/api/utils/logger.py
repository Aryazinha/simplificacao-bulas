import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Cria e configura um Logger padronizado.
    
    Por que usar logging em vez de print()?
    1. O print() se perde facilmente e não tem níveis de severidade.
    2. O logging permite filtrar por ERROR, WARNING, INFO ou DEBUG.
    3. Sistemas em produção (como Datadog, AWS CloudWatch) capturam esses logs automaticamente
       devido à formatação padronizada definida abaixo.
    """
    
    # logging.getLogger() utiliza o padrão Singleton: se você chamar `get_logger("API")` 
    # em arquivos diferentes, ele vai te devolver a exata mesma instância do logger.
    logger = logging.getLogger(name)
    
    # if not logger.handlers evita que a mesma linha seja impressa várias vezes 
    # (duplicação) se chamarmos esta função mais de uma vez.
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # StreamHandler(sys.stdout) direciona as mensagens para a saída padrão do console/terminal.
        handler = logging.StreamHandler(sys.stdout)
        
        # Formatter dita o desenho da mensagem. 
        # %(asctime)s: Timestamp exato.
        # %(name)s: Nome do módulo que gerou o log.
        # %(levelname)s: Severidade (ex: INFO, ERROR).
        # %(message)s: O texto do log.
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger
