import asyncio
import json
import ssl
from logging import getLogger
from multiprocessing import Queue
from typing import TYPE_CHECKING, Callable, Optional, Tuple, Union

from websockets.server import WebSocketServerProtocol, serve

if TYPE_CHECKING:
    from hippogym.hippogym import HippoGym


LOGGER = getLogger(__name__)


class WebSocketCommunicator:
    """A websocket communicator handling connexions to a HippoGym experiment."""

    def __init__(
        self,
        hippo: "HippoGym",
        host: Optional[str] = "localhost",
        port: int = 5000,
        ssl_certificate: Optional["SSLCertificate"] = None,
    ):
        """A websocket communicator handling connexions to a HippoGym experiment.

        Args:
            hippo (HippoGym): HippoGym experiment.
            host (Optional[str], optional): Host of the websocket server. Defaults to "localhost".
            port (int, optional): Port of the websocket server. Defaults to 5000.
            ssl_certificate (SSLCertificate, optional): SLL certificate of the websocket
                server host. Defaults to None.
        """
        self.hippo = hippo
        self.host = host
        self.port = port
        self.ssl_certificate = ssl_certificate

    async def start(self):
        """Start the communicator serverside."""
        servers = []
        non_ssl_port = self.port
        if self.ssl_certificate is not None:
            non_ssl_port += 1
            ssl_server = start_ssl_server(self.handler, self.ssl_certificate, self.port)
            servers.append(ssl_server)
        non_ssl_server = start_non_ssl_server(self.handler, self.host, non_ssl_port)
        servers.append(non_ssl_server)
        servers_tasks = [asyncio.create_task(server) for server in servers]
        _, pending = await asyncio.wait(
            servers_tasks, return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:  # Shutdown all servers if any is shutdown
            task.cancel()

    async def user_handler(self, server: WebSocketServerProtocol) -> Tuple[str, str]:
        """Handle the first message of the websocket which should contain user data.

        Args:
            server (WebSocketServerProtocol): WebSocket server side connexion.

        Raises:
            ValueError: If user_id could not be found in the first message.

        Returns:
            Tuple[str, str]: User unique id and project id.
        """
        message = await server.recv()
        message_dict: dict = json.loads(message)

        project_id = message_dict.get("projectId", None)
        user_id = message_dict.get("userId", None)

        if user_id is None:
            raise ValueError("user_id not found")
        LOGGER.info("User %s connected on project %s", user_id, project_id)
        return user_id, project_id

    async def handler(self, server: WebSocketServerProtocol, _path: str) -> None:
        """Main function being run on a new websocket connexion.

        Args:
            server (WebSocketServerProtocol): WebSocket server side connexion.
            _path (str): WebSocket connexion path, usually root (/).
        """
        user_id, _project_id = await self.user_handler(server)
        in_q, out_q = self.hippo.start_trial(user_id)

        producer_coroutine = self.producer_handler(server, out_q)
        producer_task = asyncio.create_task(producer_coroutine)

        consumer_coroutine = self.consumer_handler(server, in_q)
        consumer_task = asyncio.create_task(consumer_coroutine)

        _done, pending = await asyncio.wait(
            [producer_task, consumer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()
        await server.close()
        LOGGER.info("User Disconnected")
        self.hippo.stop_trial(user_id)

    async def consumer_handler(
        self,
        server: WebSocketServerProtocol,
        in_q: Queue,
    ) -> None:
        """Handle incomming messages from client side of the WebSocket connexion.

        Args:
            server (WebSocketServerProtocol): WebSocket server side connexion.
            event_handler (EventHandler): Handler to transcribe messages into HippoGym events.
        """
        async for message in server:
            message = json.loads(message)  # Messages should be json deserialisable.
            in_q.put_nowait(message)
            await asyncio.sleep(0.01)

    async def producer_handler(
        self,
        server: WebSocketServerProtocol,
        out_q: Queue,
    ) -> None:
        """Handle messages to send to the client side of the WebSocket connexion.

        Args:
            server (WebSocketServerProtocol): WebSocket server side connexion.
            event_handler (EventHandler): Handler to transcribe messages into HippoGym events.
        """
        done = False
        while not done:
            message = await self.producer(out_q)
            if message == "done":
                message = {"done": True}
                done = True
            await server.send(json.dumps(message))

    async def producer(self, out_q: Queue) -> Optional[Union[dict, str]]:
        """Produce messages to send to the client side of the WebSocket connexion.

        Args:
            event_handler (EventHandler): Handler to transcribe messages into HippoGym events.
        """
        while out_q.empty():
            await asyncio.sleep(0.01)
        return out_q.get()


async def start_non_ssl_server(handler: Callable, host: str, port: int) -> None:
    """Start a non-ssl WebSocket server.

    Args:
        handler (Callable): Function to serve on the websocket.
        host (str): Host of the websocket server.
        port (int): Port of the websocket server.
    """
    async with serve(handler, host, port) as websocket:
        LOGGER.info("Non-SSL websocket started at %s:%i", host, port)
        await websocket.serve_forever()


class SSLCertificate:
    certfile: str = "fullchain.pem"
    privkey: str = "privkey.pem"


async def start_ssl_server(
    handler: Callable,
    ssl_certificate: SSLCertificate,
    port: int,
) -> None:
    """Start a ssl WebSocket server.

    Args:
        handler (Callable): Function to serve on the websocket.
        ssl_certificate (SSLCertificate): SLL certificate of the websocket server host.
        port (int): Port of the websocket server.
    """
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(
        ssl_certificate.certfile, keyfile=ssl_certificate.privkey
    )
    async with serve(handler, None, port, ssl=ssl_context) as websocket:
        LOGGER.info("SSL websocket started on port %i", port)
        await websocket.serve_forever()
