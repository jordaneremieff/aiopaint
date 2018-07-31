import json
from starlette.types import Scope, Receive, Send
from starlette.routing import Router, Path
from starlette.staticfiles import StaticFile


class WebSocketDisconnect(Exception):
    """Raised when disconnecting the websocket consumer"""


class PaintApp:
    def __init__(self, scope: Scope) -> None:
        self.scope = scope
        self.x_coordinates = []
        self.y_coordinates = []
        self.drag_states = []

    async def __call__(self, receive: Receive, send: Send) -> None:
        self.send = send

        try:
            while True:
                message = await receive()
                await self.handle(message)
        except WebSocketDisconnect:
            return

    async def handle(self, message: dict) -> None:
        message_type = message["type"].replace(".", "_")
        handler = getattr(self, message_type)
        await handler(message)

    async def websocket_connect(self, message: dict) -> None:
        await self.send({"type": "websocket.accept"})

    async def websocket_receive(self, message: dict) -> None:
        input_data = json.loads(message["text"])
        self.x_coordinates.append(input_data["x_pos"])
        self.y_coordinates.append(input_data["y_pos"])
        self.drag_states.append(input_data.get("is_dragging", False))
        output_data = json.dumps(
            {
                "x_coordinates": self.x_coordinates,
                "y_coordinates": self.y_coordinates,
                "drag_states": self.drag_states,
            }
        )
        await self.send({"type": "websocket.send", "text": output_data})

    async def websocket_disconnect(self, message: dict) -> None:
        await self.send({"type": "websocket.close"})
        raise WebSocketDisconnect()


app = Router([Path("/", app=StaticFile(path="index.html")), Path("/ws/", app=PaintApp)])
