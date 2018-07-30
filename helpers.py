class WebSocketConsumer:
    def __init__(self, scope):
        self.scope = scope

    async def __call__(self, receive, send):
        self.send = send

        while True:
            message = await receive()
            await self.handle(message)

    async def handle(self, message):
        message_type = message["type"].replace(".", "_")
        handler = getattr(self, message_type)
        await handler(message)
