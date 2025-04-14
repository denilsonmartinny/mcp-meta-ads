#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Testes para o servidor MCP.
"""

import os
import pytest
from fastapi.testclient import TestClient

# Configurar variáveis de ambiente para teste
os.environ["MCP_ENV"] = "testing"
os.environ["DISABLE_AUTH"] = "true"

# Importar depois de configurar variáveis de ambiente
from src.server import app

client = TestClient(app)

def test_health_check():