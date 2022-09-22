import asyncio
import json
import ssl
from logging import getLogger
from multiprocessing import Queue
from typing import Callable, Dict, List, Optional

from websockets.server import serve

from hippogym.event_handler import EventHandler, EventsQueues

LOGGER = getLogger(__name__)


class SSLCertificate:
    certfile: str = "fullchain.pem"
    privkey: str = "privkey.pem"


class Communicator:
    def __init__(
        self,
        queues: Dict[str, Queue],
        address: Optional[str] = "localhost",
        port: int = 5000,
        ssl_certificate: Optional[SSLCertificate] = None,
    ):
        self.out_q = queues[EventsQueues.OUTPUT]
        self.address = address
        self.port = port
        self.ssl_certificate = ssl_certificate

        self.event_handler = EventHandler(queues)
        self.users: List[str] = []
        self.start()

    async def consumer_handler(self, websocket):
        async for message in websocket:
            try:
                message = json.loads(message)
                self.event_handler.parse(message)

            except Exception as error:
                LOGGER.error(repr(error))

    async def producer_handler(self, websocket):
        done = False
        while not done:
            message = await self.producer()
            if message:
                if message == "done":
                    message = {"done": True}
                    done = True
                await websocket.send(json.dumps(message))
            await asyncio.sleep(0.01)

    async def producer(self):
        message = None
        if not self.out_q.empty():
            message = self.out_q.get()
        return message

    async def handler(self, websocket, path):
        message = await websocket.recv()
        message_dict: dict = json.loads(message)

        project_id = message_dict.get("projectId", None)
        user_id = message_dict.get("userId", None)

        if user_id is not None:
            LOGGER.info("Project %s got new user: %s", project_id, user_id)
            self.event_handler.connect(user_id, project_id)
            self.users.append((user_id, project_id))
        else:
            await websocket.send(json.dumps({"Request": ("USER", None)}))
        while self.users[0] != (user_id, project_id):
            await websocket.send(json.dumps({"Request": ("STANDBY", None)}))
            await asyncio.sleep(1)

        consumer_task = asyncio.ensure_future(self.consumer_handler(websocket))
        producer_task = asyncio.ensure_future(self.producer_handler(websocket))
        _, pending = await asyncio.wait(
            [consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()
        await websocket.close()
        LOGGER.info("User Disconnected")
        self.users.remove((user_id, project_id))
        self.event_handler.disconnect(user_id, project_id)

    def start(self) -> None:
        if self.ssl_certificate:
            start_ssl_server(self.handler, self.ssl_certificate, self.port)
        start_non_ssl_server(self.handler, self.address, self.port + 1)
        asyncio.get_event_loop().run_forever()


def start_non_ssl_server(
    handler: Callable[[None], None],
    address: str,
    port: int,
) -> None:
    server = serve(handler, address, port)
    asyncio.get_event_loop().run_until_complete(server)
    LOGGER.info("Non-SSL websocket started at %s:%i", address, port)


def start_ssl_server(
    handler: Callable[[None], None],
    ssl_certificate: SSLCertificate,
    port: int,
) -> None:
    try:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(
            ssl_certificate.certfile, keyfile=ssl_certificate.privkey
        )
        ssl_server = serve(handler, None, port, ssl=ssl_context)
        asyncio.get_event_loop().run_until_complete(ssl_server)
        LOGGER.info("SSL websocket started on port %i", port)
    except Exception as error:
        LOGGER.info("SSL websocket could not start: %s", error)
