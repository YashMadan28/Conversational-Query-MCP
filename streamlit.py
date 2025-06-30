import streamlit as st
import requests

st.set_page_config(page_title="Conversational Query MCP", layout="centered")
st.title("Conversational Query MCP")

# Form layout
with st.form("query_form"):
    nl_query = st.text_input("Natural Language Query", placeholder="e.g. Show margin by region")
    dialect = st.selectbox("Select SQL Dialect", ["Druid", "MySQL", "PostgreSQL", "MSSQL"])
    submitted = st.form_submit_button("Submit")

# MCP Payload Builder
if submitted and nl_query:
    if "merge" in nl_query.lower():
        payload = {
            "agent": "mdm_agent",
            "intent": "match_and_merge",
            "payload": {
                "entity_type": "customer",
                "survivorship": {"address": "most_recent"}
            }
        }
    elif "workflow" in nl_query.lower():
        payload = {
            "agent": "workflow_agent",
            "intent": "create_workflow",
            "payload": {
                "workflow_name": "Supplier Validation",
                "steps": [
                    {"step": "validate_field", "field": "region"},
                    {"step": "route_to_team", "team": "ops"}
                ]
            }
        }
    else:
        payload = {
            "agent": "query_agent",
            "intent": "generate_sql",
            "payload": {"dialect": dialect.lower()}
        }

    # Send to MCP server
    try:
        response = requests.post("http://localhost:8000/mcp", json=payload)
        response.raise_for_status()
        result = response.json()
        if "sql" in result.get("result", {}):
            st.subheader("Generated SQL")
            st.code(result["result"]["sql"], language="sql")
        else:
            st.subheader("Response")
            st.json(result)
    except Exception as e:
        st.error(f"Error: {e}")
