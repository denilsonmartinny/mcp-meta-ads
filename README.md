# Servidor MCP para Meta Ads

Este projeto implementa um servidor MCP (Model Context Protocol) que permite a modelos de IA interagirem com a API do Meta Ads (Facebook Ads).

## Funcionalidades

- Interface padronizada para que modelos de IA acessem dados do Meta Ads
- Autenticação segura com a API do Meta
- Operações comuns de gerenciamento de campanhas publicitárias
- Relatórios e análises de desempenho

## Requisitos

- Python 3.9+
- Uma conta Meta Business
- Acesso à API do Meta Ads (token de acesso)

## Instalação

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/mcp-meta-ads.git
   cd mcp-meta-ads
   ```

2. Crie um ambiente virtual:
   ```
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   ```
   cp .env.example .env
   # Edite o arquivo .env com suas credenciais
   ```

## Uso

1. Inicie o servidor:
   ```
   python -m src.server
   ```

2. O servidor estará disponível em `http://localhost:8000`

3. Conecte seu modelo de IA ao servidor MCP usando o endpoint adequado

## Documentação da API

Após iniciar o servidor, acesse a documentação interativa em `http://localhost:8000/docs`.

## Testes

Execute os testes com:
```
pytest
```

## Licença

MIT
