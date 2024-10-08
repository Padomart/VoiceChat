from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from typing import List

from fastapi.templating import Jinja2Templates

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        if len(self.active_connections) < 5:
            await websocket.accept()
            self.active_connections.append(websocket)
        else:
            await websocket.close()

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str, sender: WebSocket):
        for connection in self.active_connections:
            if connection != sender:
                await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A user has disconnected.", websocket)


templates = Jinja2Templates(directory="templates")

@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
