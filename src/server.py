#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Servidor MCP principal que gerencia conexões com modelos de IA e redireciona
solicitações para manipuladores específicos.
"""

import os
import logging
from typing import Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from .routes import router
from .utils.logging import setup_logging
from .middleware.authentication import verify_token

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="MCP Server para Meta Ads",
    description="Um servidor Model Context Protocol para integração com Meta Ads",
    version="0.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Substituir por origens específicas em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(router)

@app.get("/health")
async def health_check():
    """Endpoint para verificação de saúde do servidor."""
    return {"status": "ok", "message": "MCP Server está funcionando"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Manipulador global de exceções."""
    logger.error(f"Erro não tratado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Erro interno do servidor"},
    )

def start():
    """Inicia o servidor MCP."""
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Iniciando servidor MCP em {host}:{port}")
    uvicorn.run("src.server:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    start()