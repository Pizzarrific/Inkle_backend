# main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Routers (they should export "router" without setting prefix inside them)
from routes.users import router as users_router
from routes.posts import router as posts_router
from routes.follow import router as follow_router
from routes.likes import router as likes_router
from routes.comments import router as comments_router
from routes.block import router as block_router
from routes.activity import router as activity_router
from routes.notifications import router as notifications_router
from routes.admin import router as admin_router
# ... add more routers as needed

# models init
from models import init_all_tables

# AI helpers
from ai import moderate_text

app = FastAPI(title="Inkle Backend Assignment")

# initialize DB tables on startup
init_all_tables()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers and give them a single canonical prefix here:
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(posts_router, prefix="/posts", tags=["Posts"])
app.include_router(follow_router, prefix="/follow", tags=["Follow"])
app.include_router(likes_router, prefix="/likes", tags=["Likes"])
app.include_router(comments_router, prefix="/comments", tags=["Comments"])
app.include_router(block_router, prefix="/block", tags=["Block"])
app.include_router(activity_router, prefix="/activity", tags=["Activity"])
app.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])

# static (optional; you removed frontend)
# app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# WebSocket chat
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for conn in self.active_connections:
            await conn.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # moderate
            if not moderate_text(data):
                await websocket.send_text("[Message Blocked: Toxic Content]")
                continue
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# AI chat endpoint example
@app.post("/api/chat")
async def chat_api(payload: dict):
    message = payload.get("message", "")
    from ai import moderate_text, analyze_sentiment

    if not moderate_text(message):
        return {"reply": "[Message Blocked: Toxic Content]"}

    sentiment = analyze_sentiment(message)
    reply = f"AI Reply [{sentiment.get('sentiment','neutral')}]: {message}"
    return {"reply": reply}
