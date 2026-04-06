from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sqlite3
import json
import asyncio
from datetime import datetime
from collections import defaultdict


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(presence_broadcaster())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connections: list[WebSocket] = []
user_sockets: dict[str, list[WebSocket]] = defaultdict(list)
last_seen:    dict[str, float] = {}

conn   = sqlite3.connect("chat.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    sender    TEXT,
    receiver  TEXT,
    message   TEXT,
    timestamp TEXT
)
""")
conn.commit()


def presence_status(elapsed: float) -> str:
    if elapsed < 15:
        return "online"
    if elapsed < 60:
        return "away"
    return "offline"


async def broadcast(payload: dict):
    text = json.dumps(payload)
    for ws in list(connections):
        try:
            await ws.send_text(text)
        except Exception:
            pass


async def broadcast_presence(username: str, status: str):
    await broadcast({"type": "presence", "username": username, "status": status})


async def presence_broadcaster():
    while True:
        await asyncio.sleep(10)
        now = asyncio.get_running_loop().time()
        for uname, t in list(last_seen.items()):
            status = presence_status(now - t)
            await broadcast_presence(uname, status)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    sender_name: str | None = None

    try:
        while True:
            raw  = await websocket.receive_text()
            data = json.loads(raw)

            uname = data.get("username")
            if uname:
                sender_name = uname
                last_seen[uname] = asyncio.get_running_loop().time()
                if websocket not in user_sockets[uname]:
                    user_sockets[uname].append(websocket)

            event_type = data.get("type", "message")

            if event_type == "hello":
                await broadcast_presence(uname, "online")
                continue

            if event_type == "typing":
                await broadcast(data)
                continue

            sender    = data["username"]
            receiver  = data["to"]
            message   = data["message"]
            timestamp = datetime.now().strftime("%I:%M %p")

            cursor.execute(
                "INSERT INTO messages (sender, receiver, message, timestamp) VALUES (?, ?, ?, ?)",
                (sender, receiver, message, timestamp),
            )
            conn.commit()

            await broadcast({
                "type":      "message",
                "username":  sender,
                "to":        receiver,
                "message":   message,
                "timestamp": timestamp,
            })

    except Exception:
        if websocket in connections:
            connections.remove(websocket)

        if sender_name:
            socks = user_sockets[sender_name]
            if websocket in socks:
                socks.remove(websocket)

            if not socks:
                last_seen[sender_name] = 0
                await broadcast_presence(sender_name, "offline")


@app.get("/messages")
def get_messages(user1: str, user2: str):
    cursor.execute(
        """
        SELECT sender, receiver, message, timestamp
        FROM messages
        WHERE (sender = ? AND receiver = ?)
           OR (sender = ? AND receiver = ?)
        ORDER BY id ASC
        """,
        (user1, user2, user2, user1),
    )
    rows = cursor.fetchall()
    return [
        {
            "type":      "message",
            "username":  r[0],
            "to":        r[1],
            "message":   r[2],
            "timestamp": r[3],
        }
        for r in rows
    ]