# Aevah MCP Server

A Model Context Protocol (MCP) server built with FastAPI for handling agent requests.

## Features

- FastAPI-based REST API
- SQLite in-memory logging
- Support for multiple agent types (query, MDM, workflow)
- Health check endpoint
- CORS support
- Comprehensive error handling

## Installation

1. Create a virtual environment (if not already done):
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

## API Endpoints

### Health Check
- **GET** `/health` - Check server status

### MCP Endpoint
- **POST** `/mcp` - Handle agent requests

### API Documentation
- **GET** `/docs` - Interactive API documentation (Swagger UI)
- **GET** `/redoc` - Alternative API documentation

## Request Format

```json
{
  "agent": "query_agent|mdm_agent|workflow_agent",
  "intent": "string",
  "payload": {
    // Agent-specific payload data
  }
}
```

## Response Format

```json
{
  "status": "success|error",
  "result": {
    // Agent-specific result data
  }
}
```

## Supported Agents

1. **query_agent** - SQL query builder
2. **mdm_agent** - Master Data Management operations
3. **workflow_agent** - Workflow management

## Error Handling

The server includes comprehensive error handling for:
- Invalid agent types
- Database errors
- Input validation errors
- General exceptions

All errors are logged and appropriate HTTP status codes are returned. 