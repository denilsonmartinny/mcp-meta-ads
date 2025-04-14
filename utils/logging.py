#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuração de logging para o servidor MCP.
"""

import os
import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging():
    """
    Configura o sistema de logging para a aplicação.
    
    - Configura o formato dos logs
    - Define níveis de log com base no ambiente
    - Configura handlers para console e arquivo
    """
    # Determinar o nível de log com base no ambiente
    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    # Configurar o formato do log
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configurar formatter
    formatter = logging.Formatter(log_format, date_format)
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Limpar handlers existentes
    root_logger.handlers = []
    
    # Configurar console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Configurar arquivo de log
    logs_dir = os.getenv("LOGS_DIR", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, "mcp_server.log")
    
    # Adicionar rotating file handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Configurar níveis de log específicos para bibliotecas externas
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    
    # Log de inicialização
    logging.info("Sistema de logging configurado")