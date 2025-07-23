from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import uuid
import os
import json
from typing import Dict, List, Optional

# Assuming these are your custom modules
from app.query_llm import ask_llm_ollama
from app.sql_utils import run_query

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Store all chat sessions
chat_sessions: Dict[str, List[Dict]] = {}
# Store chat metadata (title, creation time)
chat_metadata: Dict[str, Dict] = {}

def generate_chat_title(question: str) -> str:
    """Generate a title from the first question"""
    return question[:30] + ("..." if len(question) > 30 else "")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Prepare chat history for sidebar
    chats = [
        (session_id, {
            "title": metadata["title"],
            "created_at": metadata["created_at"]
        })
        for session_id, metadata in chat_metadata.items()
    ]
    # Sort by creation time (newest first)
    sorted_chats = sorted(chats, key=lambda x: x[1]["created_at"], reverse=True)
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "chats": sorted_chats,
        "current_session": None,  # No active chat on home page
        "history": [],
        "chat_title": ""
    })

@app.get("/chat/new", response_class=RedirectResponse)
async def new_chat(request: Request):
    """Create a new chat session"""
    session_id = str(uuid.uuid4())
    chat_sessions[session_id] = []
    chat_metadata[session_id] = {
        "title": "New Chat",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    return RedirectResponse(url=f"/chat/{session_id}", status_code=303)

@app.get("/chat/{session_id}", response_class=HTMLResponse)
async def view_chat(request: Request, session_id: str):
    """View an existing chat session"""
    if session_id not in chat_sessions:
        return RedirectResponse(url="/")
    
    # Prepare chat history for sidebar
    chats = [
        (id, {
            "title": metadata["title"],
            "created_at": metadata["created_at"]
        })
        for id, metadata in chat_metadata.items()
    ]
    # Sort by creation time (newest first)
    sorted_chats = sorted(chats, key=lambda x: x[1]["created_at"], reverse=True)
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "chats": sorted_chats,
        "current_session": session_id,
        "history": chat_sessions[session_id],
        "chat_title": chat_metadata[session_id]["title"]
    })

@app.post("/chat/{session_id}/ask", response_class=RedirectResponse)
async def ask_question(
    session_id: str,
    question: str = Form(...)
):
    """Process question and redirect back to chat"""
    if session_id not in chat_sessions:
        return RedirectResponse(url="/")
    
    timestamp = datetime.now().strftime("%H:%M")
    


    try:
        history = chat_sessions.get(session_id, [])  # Get current chat history
        llm_output = ask_llm_ollama(question, history)
        sql = llm_output.get("sql", "")
        explanation = llm_output.get("explanation", "")
        result = run_query(sql)
    except Exception as e:
        sql = ""
        explanation = f"Error: {str(e)}"
        result = [{"error": str(e)}]

    # Chart logic
    chart_data = None
    chart_type = "bar"
    if isinstance(result, list) and result and isinstance(result[0], dict):
        keys = list(result[0].keys())
        if len(keys) == 2:
            x_vals = [str(row[keys[0]]) for row in result]
            y_vals = [row[keys[1]] for row in result]
            if all(isinstance(y, (int, float)) for y in y_vals):
                chart_data = {
                    "labels": x_vals,
                    "values": y_vals,
                    "label": keys[1]
                }
                if len(set(x_vals)) <= 10:
                    chart_type = "pie"
                else:
                    chart_type = "bar"

    # Save to chat history
    chat_sessions[session_id].append({
        "question": question,
        "sql": sql,
        "explanation": explanation,
        "result": result,
        "time": timestamp,
        "chart_data": chart_data,
        "chart_type": chart_type
    })

    # First time metadata
    if len(chat_sessions[session_id]) == 1:
        chat_metadata[session_id]["title"] = generate_chat_title(question)
        chat_metadata[session_id]["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    return RedirectResponse(url=f"/chat/{session_id}", status_code=303)

@app.post("/chat/{session_id}/ask_json")
async def ask_question_json(
    session_id: str,
    request: Request
):
    """JSON API: Process question and return only JSON (no reload)"""
    if session_id not in chat_sessions:
        return JSONResponse(status_code=404, content={"error": "Session not found"})

    body = await request.json()
    question = body.get("question", "")
    timestamp = datetime.now().strftime("%H:%M")

    try:
        history_dicts = chat_sessions.get(session_id, [])
        history = [item["question"] for item in history_dicts if "question" in item]

        llm_output = ask_llm_ollama(question, history) 
        sql = llm_output.get("sql", "")
        explanation = llm_output.get("explanation", "")
        result = run_query(sql)
    except Exception as e:
        sql = ""
        explanation = f"Error: {str(e)}"
        result = [{"error": str(e)}]

    # Chart logic
    chart_data = None
    chart_type = "bar"
    if isinstance(result, list) and result and isinstance(result[0], dict):
        keys = list(result[0].keys())
        if len(keys) == 2:
            x_vals = [str(row[keys[0]]) for row in result]
            y_vals = [row[keys[1]] for row in result]
            if all(isinstance(y, (int, float)) for y in y_vals):
                chart_data = {
                    "labels": x_vals,
                    "values": y_vals,
                    "label": keys[1]
                }
                if len(set(x_vals)) <= 10:
                    chart_type = "pie"

    # Save to chat history
    chat_sessions[session_id].append({
        "question": question,
        "sql": sql,
        "explanation": explanation,
        "result": result,
        "time": timestamp,
        "chart_data": chart_data,
        "chart_type": chart_type
    })

    # First time metadata
    if len(chat_sessions[session_id]) == 1:
        chat_metadata[session_id]["title"] = generate_chat_title(question)
        chat_metadata[session_id]["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    return JSONResponse({
        "sql": sql,
        "explanation": explanation,
        "result": result,
        "chart_data": chart_data,
        "chart_type": chart_type,
        "time": timestamp
    })

@app.post("/chat/{session_id}/clear")
async def clear_chat(session_id: str):
    """Clear a chat session"""
    if session_id in chat_sessions:
        chat_sessions[session_id] = []
    return RedirectResponse(url=f"/chat/{session_id}", status_code=303)

@app.post("/chat/{session_id}/delete")
async def delete_chat(session_id: str):
    """Delete a chat session"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    if session_id in chat_metadata:
        del chat_metadata[session_id]
    return RedirectResponse(url="/", status_code=303)

@app.get("/chat/{session_id}/export")
async def export_chat(session_id: str):
    """Export a chat session to JSON"""
    if session_id not in chat_sessions:
        return {"error": "Chat session not found"}
    
    session_data = chat_sessions[session_id]
    if not session_data:
        return {"error": "No chat history found."}

    export_data = {
        "metadata": chat_metadata.get(session_id, {}),
        "messages": session_data
    }

    # Create exports directory if it doesn't exist
    os.makedirs("exports", exist_ok=True)
    file_path = f"exports/{session_id}.json"
    
    with open(file_path, "w") as f:
        json.dump(export_data, f, indent=2)

    return FileResponse(
        file_path,
        media_type="application/json",
        filename=f"chat_export_{session_id}.json"
    )