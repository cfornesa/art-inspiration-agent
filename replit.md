# AI Art Ideation Agent

## Overview
A FastAPI-based Python agent that provides advice about art ideation using the DeepSeek API. The agent uses the GAIL Framework (Goals, Actions, Information, Language) to structure its responses.

## Project Structure
- `main.py` - FastAPI application with the /chat endpoint
- `pyproject.toml` - Python dependencies

## API Endpoints
- `POST /chat` - Send a message and chat history, receive AI response
  - Request body: `{ "message": "string", "history": [{"role": "user/assistant", "content": "..."}] }`
  - Response: `{ "reply": "string" }`

## Configuration
- Requires `DEEPSEEK_API_KEY` secret to be set
- CORS is configured to allow all origins (update for production)

## Running
- Development: `uvicorn main:app --host 0.0.0.0 --port 5000`
- Production: Deployed via Replit's autoscale deployment

## Recent Changes
- December 18, 2025: Initial setup with FastAPI and DeepSeek integration
