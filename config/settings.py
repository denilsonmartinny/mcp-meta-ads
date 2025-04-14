#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configurações do servidor MCP.
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações da aplicação
APP_NAME = "MCP Server para Meta Ads"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "Um servidor Model Context Protocol para integração com Meta Ads"

# Configurações do servidor
SERVER_HOST = os.getenv("HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("PORT", "8000"))
SERVER_RELOAD = os.getenv("RELOAD", "True").lower() == "true"

# Configurações de ambiente
ENV = os.getenv("MCP_ENV", "development")
DEBUG = ENV == "development"

# Configurações de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOGS_DIR = os.getenv("LOGS_DIR", "logs")

# Configurações de autenticação
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "seu_segredo_superseguro_para_desenvolvimento")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "1440"))  # 24 horas
DISABLE_AUTH = os.getenv("DISABLE_AUTH", "False").lower() == "true"

# Configurações do Meta Ads
META_APP_ID = os.getenv("META_APP_ID", "")
META_APP_SECRET = os.getenv("META_APP_SECRET", "")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
META_ACCOUNT_ID = os.getenv("META_ACCOUNT_ID", "")

# Configurações CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
if CORS_ORIGINS == ["*"]:
    CORS_ORIGINS = ["*"]
else:
    CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS]

# Configurações de rate limiting
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # segundos

# Outras configurações
MAX_REQUEST_SIZE = int(os.getenv("MAX_REQUEST_SIZE", "10")) * 1024 * 1024  # 10MB

# Mapeamento de campos permitidos em relatórios
ALLOWED_INSIGHT_FIELDS = [
    "impressions",
    "clicks",
    "spend",
    "cpc",
    "ctr",
    "reach",
    "actions",
    "cost_per_action_type",
    "conversions",
    "conversion_values",
    "unique_clicks",
    "frequency",
    "unique_impressions",
    "engagement_rate_ranking",
    "quality_ranking",
]

# Limites de solicitação
REQUEST_LIMITS = {
    "get_campaigns": 100,
    "get_ad_sets": 200,
    "get_ads": 300,
    "get_insights": 50,
}

# Configuração do cache
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True").lower() == "true"
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutos

def get_all_settings() -> Dict[str, Any]:
    """
    Retorna todas as configurações definidas neste módulo.
    
    Returns:
        Dicionário de configurações
    """
    return {k: v for k, v in globals().items() if not k.startswith("_") and k.isupper()}