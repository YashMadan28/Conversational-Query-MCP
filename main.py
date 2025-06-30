from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import sqlite3
import time
import logging
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize app
app = FastAPI(
    title="Conversational Query MCP",
    description="A Model Context Protocol server for handling agent requests",
    version="1.0.0"
)

# CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": time.time()}

# SQLite log DB
def get_db_connection():
    return sqlite3.connect(":memory:", check_same_thread=False)

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent TEXT,
    intent TEXT,
    payload TEXT,
    result TEXT,
    duration REAL
)
""")
conn.commit()

# Request/response schemas
class MCPRequest(BaseModel):
    agent: str
    intent: str
    payload: Dict

class MCPResponse(BaseModel):
    status: str
    result: Dict

# Agent functions
def query_builder_tool(payload):
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary")
    dialect = payload.get("dialect", "druid").lower()
    if dialect == "druid":
        query = ("SELECT region, AVG(margin) "
                 "FROM product_data "
                 "WHERE __time >= CURRENT_TIMESTAMP - INTERVAL '3' MONTH "
                 "GROUP BY region;")
    elif dialect == "mysql":
        query = ("SELECT region, AVG(margin) "
                 "FROM product_data "
                 "WHERE __time >= NOW() - INTERVAL 3 MONTH "
                 "GROUP BY region;")
    elif dialect == "postgresql":
        query = ("SELECT region, AVG(margin) "
                 "FROM product_data "
                 "WHERE __time >= NOW() - INTERVAL '3 months' "
                 "GROUP BY region;")
    elif dialect == "mssql":
        query = ("SELECT region, AVG(margin) "
                 "FROM product_data "
                 "WHERE __time >= DATEADD(MONTH, -3, GETDATE()) "
                 "GROUP BY region;")
    else:
        raise ValueError(f"Unsupported SQL dialect: {dialect}")
    return {"sql": query}

def mdm_tool(payload):
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary")
    entity = payload.get("entity_type", "unknown")
    rule = payload.get("survivorship", {})
    return {"message": f"Merged duplicates for entity {entity} using rules: {rule}"}

def workflow_tool(payload):
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary")
    return {
        "workflow_name": payload.get("workflow_name", "Unnamed"),
        "steps": payload.get("steps", [])
    }

# Tool registry
TOOL_REGISTRY = {
    "query_agent": query_builder_tool,
    "mdm_agent": mdm_tool,
    "workflow_agent": workflow_tool
}

@app.post("/mcp", response_model=MCPResponse)
def mcp_route(request: MCPRequest):
    start = time.time()
    agent_func = TOOL_REGISTRY.get(request.agent)
    if not agent_func:
        raise HTTPException(status_code=400, detail="Unknown agent")
    try:
        result = agent_func(request.payload)
        duration = round(time.time() - start, 3)
        try:
            cursor.execute(
                "INSERT INTO logs (agent, intent, payload, result, duration) VALUES (?, ?, ?, ?, ?)",
                (request.agent, request.intent, str(request.payload), str(result), duration)
            )
            conn.commit()
        except sqlite3.Error as db_error:
            logger.error(f"Database error: {db_error}")
        return MCPResponse(status="success", result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
