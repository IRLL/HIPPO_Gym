import asyncio
import json
import ssl
from logging import getLogger
from typing import TYPE_CHECKING, Callable, Dict, Optional

from websockets.server import serve, WebSocketServerProtocol


if TYPE_CHECKING:
    from hippogym.hippogym import HippoGym

from hippogym.event_handler import EventHandler

LOGGER = getLogger(__name__)


class WebSocketCommunicator:
    def __init__(
        self,
        hippo: "HippoGym",
        host: Optional[str] = "localhost",
        port: int = 5000,
        ssl_certificate: Optional["SSLCertificate"] = None,
    ):
        self.hippo = hippo
        self.host = host
        self.port = port
        self.ssl_certificate = ssl_certificate

    async def start(self):
        """Start the communicator serverside."""
        non_ssl_server = start_non_ssl_server(self.handler, self.host, self.port + 1)
        servers = [non_ssl_server]
        if self.ssl_certificate is not None:
            ssl_server = start_ssl_server(self.handler, self.ssl_certificate, self.port)
            servers.append(ssl_server)
        await asyncio.gather(*servers)

    async def user_handler(self, websocket: WebSocketServerProtocol):
        message = await websocket.recv()
        message_dict: dict = json.loads(message)

        project_id = message_dict.get("projectId", None)
        user_id = message_dict.get("userId", None)

        if user_id is None:
            raise ValueError("user_id not found")
        LOGGER.info("User %s connected on project %s", user_id, project_id)
        return user_id, project_id

    async def handler(self, websocket: WebSocketServerProtocol, _path: str):
        try:
            user_id, _project_id = await self.user_handler(websocket)
            trial = self.hippo.start_trial(user_id)
            event_handler = EventHandler(trial.queues)
            consumer_task = asyncio.create_task(
                self.consumer_handler(websocket, event_handler)
            )
            producer_task = asyncio.create_task(
                self.producer_handler(websocket, event_handler)
            )
            _done, pending = await asyncio.wait(
                [consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()
        finally:
            LOGGER.info("User Disconnected")
            self.hippo.stop_trial(user_id)

    async def consumer_handler(
        self,
        websocket: WebSocketServerProtocol,
        event_handler: EventHandler,
    ):
        async for message in websocket:
            try:
                message = json.loads(message)
                event_handler.parse(message)
            except Exception as error:
                LOGGER.error(repr(error))

    async def producer_handler(
        self,
        websocket: WebSocketServerProtocol,
        event_handler: EventHandler,
    ):
        done = False
        while not done:
            message = await self.producer(event_handler)
            if message:
                if message == "done":
                    message = {"done": True}
                    done = True
                await websocket.send(json.dumps(message))

    async def producer(self, event_handler: EventHandler):
        message = None
        if not event_handler.out_q.empty():
            message = event_handler.out_q.get()
        return message


async def start_non_ssl_server(handler: Callable, address: str, port: int) -> None:
    async with serve(handler, address, port) as websocket:
        LOGGER.info("Non-SSL websocket started at %s:%i", address, port)
        await websocket.serve_forever()


class SSLCertificate:
    certfile: str = "fullchain.pem"
    privkey: str = "privkey.pem"


async def start_ssl_server(
    handler: Callable,
    ssl_certificate: SSLCertificate,
    port: int,
) -> None:
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(
        ssl_certificate.certfile, keyfile=ssl_certificate.privkey
    )
    async with serve(handler, None, port, ssl=ssl_context) as websocket:
        LOGGER.info("SSL websocket started on port %i", port)
        await websocket.serve_forever()
