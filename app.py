import json
from starlette import HTMLResponse
from starlette.routing import Router, Path
from jinja2 import Environment, FileSystemLoader

from helpers import WebSocketConsumer


env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("index.html").render()


class PaintApp:

    x_pos = []
    y_pos = []
    mouse_pos = []

    def on_draw(self, data):
        self.x_pos.append(data["x"])
        self.y_pos.append(data["y"])
        mouse_pos = data.get("mousePos", False)
        self.mouse_pos.append(mouse_pos)

    @property
    def as_json(self):
        data = {"xPos": self.x_pos, "yPos": self.y_pos, "mousePos": self.mouse_pos}
        return json.dumps(data)


class HTMLApp:
    def __init__(self, scope):
        self.scope = scope

    async def __call__(self, receive, send):
        response = HTMLResponse(template)
        await response(receive, send)


class WebSocketApp(WebSocketConsumer):

    paint = PaintApp()

    async def websocket_connect(self, message):
        await self.send({"type": "websocket.accept"})

    async def websocket_receive(self, message):
        data = json.loads(message["text"])
        self.paint.on_draw(data)
        await self.send({"type": "websocket.send", "text": self.paint.as_json})


app = Router([Path("/", app=HTMLApp), Path("/ws", app=WebSocketApp)])
