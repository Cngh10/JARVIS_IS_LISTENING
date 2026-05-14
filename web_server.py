"""
🌐 JARVIS WEB SERVER (Iron Man Level)

FastAPI server for web interface communication.
Features:
- WebSocket for real-time voice/audio streaming
- REST API for text-based interaction
- System command execution
- Voice authentication
- State management
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import asyncio
import os

from voice import speak, stop_speaking, get_is_speaking
from commands import execute, is_system_command
from claude_integration import claude_engine, ask_ai_async, wait_for_ai_response, add_to_history
from auth import verify_voice, VOICE_VERIFICATION_AVAILABLE
from memory import remember, recall
from state_machine import JarvisState

# 🚀 FASTAPI APP
app = FastAPI(
    title="JARVIS AI Assistant",
    version="2.0.0",
    description="Iron Man level voice AI assistant"
)

# 🌐 CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📡 ACTIVE CONNECTIONS
active_connections: List[WebSocket] = []

# 📊 REQUEST MODELS
class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class CommandRequest(BaseModel):
    command: str
    params: Optional[Dict[str, Any]] = None

class MemoryRequest(BaseModel):
    key: str
    value: str

class VoiceVerifyRequest(BaseModel):
    audio_data: Optional[str] = None

# ═══════════════════════════════════════════════════════════════
# 🏠 ROOT ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "JARVIS",
        "status": "online",
        "version": "2.0.0",
        "features": [
            "Voice recognition",
            "Text-to-speech",
            "Claude AI integration",
            "System commands",
            "Memory system",
            "Voice authentication"
        ],
        "claude_available": claude_engine.is_available(),
        "voice_auth_available": VOICE_VERIFICATION_AVAILABLE
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "claude": claude_engine.is_available(),
        "voice_auth": VOICE_VERIFICATION_AVAILABLE
    }

@app.get("/status")
async def status():
    """Get current JARVIS status"""
    return {
        "is_speaking": get_is_speaking(),
        "is_ai_busy": claude_engine.is_busy(),
        "claude_available": claude_engine.is_available(),
        "history_length": len(claude_engine.get_history())
    }

# ═══════════════════════════════════════════════════════════════
# 💬 CHAT ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint for text-based interaction

    Handles both system commands and AI queries.
    """
    try:
        user_input = request.message.strip()

        if not user_input:
            return {
                "success": False,
                "error": "Empty message"
            }

        # Check if this is a system command
        if is_system_command(user_input):
            result = execute(user_input)
            return {
                "success": True,
                "response": result,
                "is_command": True,
                "type": "command"
            }

        # Send to Claude AI
        ask_ai_async(user_input)

        # Wait for response with timeout
        ai_response = wait_for_ai_response(timeout=15)

        if not ai_response:
            ai_response = "I'm having trouble thinking right now. Please try again."

        # Add to history
        add_to_history(user_input, ai_response)

        return {
            "success": True,
            "response": ai_response,
            "is_command": False,
            "type": "ai"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/command")
async def execute_command(request: CommandRequest):
    """Execute a system command"""
    try:
        result = execute(request.command)
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ═══════════════════════════════════════════════════════════════
# 🧠 MEMORY ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.post("/memory/remember")
async def remember_endpoint(request: MemoryRequest):
    """Remember a key-value pair"""
    try:
        remember(request.key, request.value)
        return {
            "success": True,
            "message": f"Remembered: {request.key} = {request.value}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/memory/recall/{key}")
async def recall_endpoint(key: str):
    """Recall a value by key"""
    try:
        value = recall(key)
        return {
            "success": True,
            "key": key,
            "value": value
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ═══════════════════════════════════════════════════════════════
# 🔐 VOICE AUTHENTICATION
# ═══════════════════════════════════════════════════════════════

@app.post("/auth/verify")
async def verify_voice_endpoint(request: VoiceVerifyRequest):
    """Verify voice authentication"""
    try:
        success = verify_voice()
        return {
            "success": success,
            "verified": success,
            "message": "Voice verified" if success else "Voice verification failed"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ═══════════════════════════════════════════════════════════════
🔊 SPEECH CONTROL
# ═══════════════════════════════════════════════════════════════

@app.post("/speech/speak")
async def speak_endpoint(request: ChatRequest):
    """Speak text"""
    try:
        speak(request.message)
        return {
            "success": True,
            "message": "Speaking"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/speech/stop")
async def stop_speech_endpoint():
    """Stop speaking"""
    try:
        stop_speaking()
        return {
            "success": True,
            "message": "Speech stopped"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ═══════════════════════════════════════════════════════════════
# 📡 WEBSOCKET ENDPOINT
# ═══════════════════════════════════════════════════════════════

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication

    Message types:
    - text: User text input
    - audio: Audio data (base64)
    - interrupt: Interrupt current speech
    - status: Get current status
    """
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)

            message_type = message.get("type")

            if message_type == "text":
                # Handle text input
                user_input = message.get("text", "").strip()

                if not user_input:
                    continue

                # Check for interrupt
                if get_is_speaking():
                    stop_speaking()
                    await websocket.send_json({
                        "type": "interrupted",
                        "message": "Speech interrupted"
                    })

                # Check if system command
                if is_system_command(user_input):
                    result = execute(user_input)
                    await websocket.send_json({
                        "type": "response",
                        "text": result,
                        "is_command": True
                    })
                else:
                    # Send to Claude
                    ask_ai_async(user_input)
                    ai_response = wait_for_ai_response(timeout=15)

                    if not ai_response:
                        ai_response = "I'm having trouble thinking right now."

                    add_to_history(user_input, ai_response)

                    await websocket.send_json({
                        "type": "response",
                        "text": ai_response,
                        "is_command": False
                    })

            elif message_type == "interrupt":
                # Handle interrupt
                if get_is_speaking():
                    stop_speaking()
                    await websocket.send_json({
                        "type": "interrupted",
                        "message": "Speech interrupted"
                    })

            elif message_type == "status":
                # Get current status
                await websocket.send_json({
                    "type": "status",
                    "is_speaking": get_is_speaking(),
                    "is_ai_busy": claude_engine.is_busy(),
                    "claude_available": claude_engine.is_available()
                })

            elif message_type == "speak":
                # Speak text
                text = message.get("text", "")
                if text:
                    speak(text)
                    await websocket.send_json({
                        "type": "speaking",
                        "text": text
                    })

            elif message_type == "stop":
                # Stop speaking
                stop_speaking()
                await websocket.send_json({
                    "type": "stopped"
                })

    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })

# ═══════════════════════════════════════════════════════════════
# 🚀 MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    print("=" * 70)
    print("🚀 JARVIS WEB SERVER")
    print("=" * 70)
    print(f"Claude Available: {claude_engine.is_available()}")
    print(f"Voice Auth Available: {VOICE_VERIFICATION_AVAILABLE}")
    print("=" * 70)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
