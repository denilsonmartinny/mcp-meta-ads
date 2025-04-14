#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configurações de autenticação para o servidor MCP.
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from jose import jwt
from pydantic import BaseModel

# Modelos de usuário
class User(BaseModel):
    """Modelo de usuário para autenticação."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: bool = False
    scopes: List[str] = []

class TokenData(BaseModel):
    """Modelo para dados de token."""
    username: str
    scopes: List[str] = []
    exp: Optional[int] = None

# Configurações de JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "seu_segredo_superseguro_para_desenvolvimento")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "1440"))  # 24 horas

# Usuários fictícios para desenvolvimento/teste
# Em produção, isso seria substituído por um banco de dados ou serviço de autenticação
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Administrador",
        "email": "admin@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "disabled": False,
        "scopes": ["admin", "read", "write"]
    },
    "user": {
        "username": "user",
        "full_name": "Usuário Normal",
        "email": "user@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "disabled": False,
        "scopes": ["read"]
    }
}

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT para autenticação.
    
    Args:
        data: Dados a serem codificados no token
        expires_delta: Tempo de expiração (opcional)
        
    Returns:
        Token JWT assinado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return encoded_jwt

def get_user(username: str) -> Optional[User]:
    """
    Obtém um usuário pelo nome de usuário.
    
    Args:
        username: Nome de usuário
        
    Returns:
        Objeto de usuário ou None se não encontrado
    """
    if username in fake_users_db:
        user_data = fake_users_db[username]
        return User(**user_data)
    return None

def verify_scope(required_scopes: List[str], token_scopes: List[str]) -> bool:
    """
    Verifica se o token tem os escopos necessários.
    
    Args:
        required_scopes: Escopos necessários
        token_scopes: Escopos do token
        
    Returns:
        True se o token tiver todos os escopos necessários, False caso contrário
    """
    # Se "admin" estiver nos escopos do token, conceder acesso total
    if "admin" in token_scopes:
        return True
    
    # Verificar se todos os escopos necessários estão presentes
    return all(scope in token_scopes for scope in required_scopes)