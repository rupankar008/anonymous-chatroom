from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, List
import random
import string

app = FastAPI()
rooms: Dict[str, List[WebSocket]] = {}
users: Dict[WebSocket, str] = {}

def generate_invite_code():
    """Generate a random invite code"""
    return ''.join(random.choices(string.ascii_uppercase, k=6))

@app.websocket("/ws/{room_code}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_code: str, username: str):
    await websocket.accept()
    if room_code not in rooms:
        rooms[room_code] = []
    rooms[room_code].append(websocket)
    users[websocket] = username
    await broadcast(room_code, f"{username} has joined the chat.")
    
    try:
        while True:
            data = await websocket.receive_text()
            await broadcast(room_code, f"{username}: {data}")
    except WebSocketDisconnect:
        rooms[room_code].remove(websocket)
        del users[websocket]
        await broadcast(room_code, f"{username} has left the chat.")
        if not rooms[room_code]:
            del rooms[room_code]

async def broadcast(room_code: str, message: str):
    """Send message to all users in the room"""
    for client in rooms.get(room_code, []):
        try:
            await client.send_text(message)
        except:
            rooms[room_code].remove(client)

@app.get("/create-room")
async def create_room():
    room_code = generate_invite_code()
    rooms[room_code] = []
    return {"room_code": room_code}

@app.get("/active-rooms")
async def active_rooms():
    return {"active_rooms": list(rooms.keys())}
@app.get("/")
async def root():
    return {"message": "Welcome to Anonymous Chatroom! Use /create-room to start."}
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# Serve the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Route for serving index.html
@app.get("/")
async def serve_homepage():
    return FileResponse("static/index.html")

