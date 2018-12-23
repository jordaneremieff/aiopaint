import json
from typing import List
from dataclasses import dataclass, field

from starlette.endpoints import HTTPEndpoint, WebSocketEndpoint
from starlette.responses import TemplateResponse
from starlette.applications import Starlette


app = Starlette(template_directory="templates")


@dataclass
class Canvas:

    x_coordinates: List = field(default_factory=list)
    y_coordinates: List = field(default_factory=list)
    drag_states: List = field(default_factory=list)

    def add_x(self, x_pos: int) -> None:
        self.x_coordinates.append(x_pos)

    def add_y(self, y_pos: int) -> None:
        self.y_coordinates.append(y_pos)

    def add_state(self, drag_state: bool) -> None:
        self.drag_states.append(drag_state)

    @property
    def json(self) -> str:
        return json.dumps(
            {
                "x_coordinates": self.x_coordinates,
                "y_coordinates": self.y_coordinates,
                "drag_states": self.drag_states,
            }
        )


@app.route("/")
class CanvasHome(HTTPEndpoint):
    async def get(self, request) -> TemplateResponse:
        context = {"request": request, "WEBSOCKET_URL": "ws://localhost:8000/ws"}
        template = app.get_template("index.html")
        return TemplateResponse(template, context)


@app.websocket_route("/ws")
class CanvasWebSocket(WebSocketEndpoint):

    encoding = "json"
    canvas = None

    async def on_connect(self, websocket) -> None:
        await websocket.accept()
        self.canvas = Canvas()

    async def on_receive(self, websocket, message) -> None:
        x_pos = message["x_pos"]
        y_pos = message["y_pos"]
        self.canvas.add_x(x_pos)
        self.canvas.add_y(y_pos)
        is_dragging = message.get("is_dragging", False)
        self.canvas.add_state(is_dragging)

        await websocket.send_text(self.canvas.json)
