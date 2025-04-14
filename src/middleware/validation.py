#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Middleware de validação para o servidor MCP.
"""

import logging
from typing import Dict, Any, Callable, Awaitable, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from pydantic import ValidationError

# Configurar logging
logger = logging.getLogger(__name__)

class ValidationMiddleware:
    """
    Middleware para validação de solicitações.
    
    Este middleware verifica se as solicitações estão bem formadas
    e contêm todos os campos necessários.
    """
    
    def __init__(
        self,
        app: Any,
    ):
        """
        Inicializa o middleware de validação.
        
        Args:
            app: Aplicação FastAPI
        """
        self.app = app
    
    async def __call__(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Processa a solicitação.
        
        Args:
            request: Solicitação HTTP
            call_next: Função para chamar o próximo middleware
            
        Returns:
            Resposta HTTP
        """
        # Verificar operações de API específicas
        if request.url.path.startswith("/api/v1/"):
            try:
                # Para solicitações POST/PUT, validar o corpo
                if request.method in ["POST", "PUT", "PATCH"]:
                    # Tentar ler o corpo da solicitação
                    body = await request.json()
                    
                    # Verificar campos obrigatórios para solicitações MCP
                    if "operation" not in body:
                        logger.warning("Solicitação MCP inválida: campo 'operation' ausente")
                        return JSONResponse(
                            status_code=400,
                            content={"detail": "Campo obrigatório 'operation' ausente no corpo da solicitação"}
                        )
                    
                    # Verificações específicas para diferentes tipos de solicitações
                    if request.url.path.endswith("/meta-ads"):
                        await self._validate_meta_ads_request(body)
                
            except ValidationError as e:
                logger.warning(f"Erro de validação de esquema: {e}")
                return JSONResponse(
                    status_code=400,
                    content={"detail": str(e)}
                )
            except Exception as e:
                logger.error(f"Erro ao validar solicitação: {e}", exc_info=True)
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Erro ao processar o corpo da solicitação"}
                )
        
        # Se a validação passar, continuar com a solicitação
        response = await call_next(request)
        return response
    
    async def _validate_meta_ads_request(self, body: Dict[str, Any]) -> None:
        """
        Valida uma solicitação específica do Meta Ads.
        
        Args:
            body: Corpo da solicitação
            
        Raises:
            ValueError: Se a solicitação for inválida
        """
        operation = body.get("operation")
        parameters = body.get("parameters", {})
        
        # Validações específicas para cada operação
        if operation == "create_campaign":
            required_fields = ["name", "objective", "status"]
            for field in required_fields:
                if field not in parameters:
                    raise ValueError(f"Campo obrigatório '{field}' ausente para operação create_campaign")
        
        elif operation == "get_insights":
            if "object_id" not in parameters or "object_type" not in parameters:
                raise ValueError("Campos 'object_id' e 'object_type' são obrigatórios para operação get_insights")