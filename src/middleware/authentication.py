#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Middleware de autenticação para o servidor MCP.
"""

import os
import logging
import time
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Configurar logging
logger = logging.getLogger(__name__)

# Configurar segurança
security = HTTPBearer()

# Carregar configurações
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "seu_segredo_superseguro_para_desenvolvimento")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

def create_access_token(data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
    """
    Cria um token JWT para autenticação.
    
    Args:
        data: Dados a serem codificados no token
        expires_delta: Tempo de expiração em minutos (opcional)
        
    Returns:
        Token JWT assinado
    """
    to_encode = data.copy()
    if expires_delta:
        expire = time.time() + expires_delta * 60
    else:
        expire = time.time() + TOKEN_EXPIRE_MINUTES * 60
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodifica e valida um token JWT.
    
    Args:
        token: Token JWT a ser decodificado
        
    Returns:
        Conteúdo decodificado do token
        
    Raises:
        HTTPException: Se o token for inválido ou expirado
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"Token inválido: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verifica e valida o token de autenticação.
    
    Args:
        credentials: Credenciais de autorização HTTP
        
    Returns:
        Token decodificado
        
    Raises:
        HTTPException: Se a autenticação falhar
    """
    # Para desenvolvimento/teste, você pode desabilitar a verificação real
    if os.getenv("MCP_ENV") == "development" and os.getenv("DISABLE_AUTH") == "true":
        logger.warning("Autenticação desabilitada em ambiente de desenvolvimento")
        return "development_token"
    
    token = credentials.credentials
    token_data = decode_token(token)
    
    return token_data