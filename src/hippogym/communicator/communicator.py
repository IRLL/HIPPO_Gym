import asyncio
from multiprocessing import Queue
import json
from logging import getLogger
import ssl
from typing import Dict, List, Optional

from websockets.server import serve

from hippogym.event.event_handler import EventHandler

LOGGER = getLogger(__name__)


class Communicator:
    def __init__(
        self,
        out_q: Queue,
        queues: Dict[str, Queue],
        address: Optional[str] = "localhost",
        port: int = 5000,
        use_ssl: bool = True,
        force_ssl: bool = False,
        fullchain_path: str = "fullchain.pem",
        privkey_path: str = "privkey.pem",
    ):
        self.out_q = out_q
        self.address = address
        self.port = port
        self.ssl = use_ssl
        self.force_ssl = force_ssl
        self.fullchain = fullchain_path
        self.privkey = privkey_path
        self.event_handler = EventHandler(queues)
        self.users: List[str] = []
        self.start()

    async def consumer_handler(self, websocket):
        self.event_handler.handle_user_id(self.users[0])
        LOGGER.info("Starting users: %s", str(self.users))
        async for message in websocket:
            try:
                message = json.loads(message)
                self.event_handler.parse(message)

            except Exception as e:
                print(e)

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
        user_id, project_id = self.event_handler.connect(json.loads(message))
        if user_id:
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
        self.event_handler.disconnect(user_id)

    def start(self) -> None:
        if not self.force_ssl:
            self.start_non_ssl_server()
        elif self.ssl:
            self.start_ssl_server()
        asyncio.get_event_loop().run_forever()

    def start_non_ssl_server(self) -> None:
        server = serve(self.handler, self.address, self.port)
        asyncio.get_event_loop().run_until_complete(server)
        LOGGER.info(
            "Non-SSL websocket started at %s on port %i",
            self.address,
            self.port,
        )

    def start_ssl_server(self) -> None:
        try:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(self.fullchain, keyfile=self.privkey)
            ssl_server = serve(self.handler, None, self.port, ssl=ssl_context)
            asyncio.get_event_loop().run_until_complete(ssl_server)
            LOGGER.info("SSL websocket started on port %i", self.port)
        except Exception as error:
            LOGGER.error("SSL failed with error: %s", error)
