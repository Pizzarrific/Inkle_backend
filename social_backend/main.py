from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# routers
from routes.users import router as users_router
from routes.posts import router as posts_router
from routes.follow import router as follow_router
from routes.likes import router as likes_router
from routes.comments import router as comments_router
from routes.block import router as block_router
from routes.activity import router as activity_router
from routes.notifications import router as notifications_router
from routes.admin import router as admin_router

# models initializer
from models import init_all_tables

# ai moderation helper
from ai import moderate_text

app = FastAPI(title="Inkle Backend Assignment")

# Create DB tables (idempotent)
init_all_tables()

# CORS (open during development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers with canonical prefixes (routes files use relative paths)
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(posts_router, prefix="/posts", tags=["Posts"])
app.include_router(follow_router, prefix="/follow", tags=["Follow"])
app.include_router(likes_router, prefix="/likes", tags=["Likes"])
app.include_router(comments_router, prefix="/comments", tags=["Comments"])
app.include_router(block_router, prefix="/block", tags=["Block"])
app.include_router(activity_router, prefix="/activity", tags=["Activity"])
app.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])


# OPTIONAL WebSocket chat (keeps moderation)
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
            if not moderate_text(data):
                await websocket.send_text("[Message Blocked: Toxic Content]")
                continue
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/")
def root():
    return {"message": "Inkle backend running"}
