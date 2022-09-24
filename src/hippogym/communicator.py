import asyncio
import json
import ssl
from logging import getLogger
from typing import TYPE_CHECKING, Callable, Optional, Tuple, Union, final

from websockets.server import serve, WebSocketServerProtocol

from hippogym.event_handler import EventHandler


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
        non_ssl_server = start_non_ssl_server(self.handler, self.host, self.port + 1)
        servers = [non_ssl_server]
        if self.ssl_certificate is not None:
            ssl_server = start_ssl_server(self.handler, self.ssl_certificate, self.port)
            servers.append(ssl_server)
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

    async def handler(self, server: WebSocketServerProtocol, _path: str):
        """Main function being run on a new websocket connexion.

        Args:
            server (WebSocketServerProtocol): WebSocket server side connexion.
            _path (str): WebSocket connexion path, usually root (/).
        """
        user_id, _project_id = await self.user_handler(server)
        trial = self.hippo.start_trial(user_id)
        event_handler = EventHandler(trial.queues)
        _done, pending = await asyncio.wait(
            [
                asyncio.create_task(self.producer_handler(server, event_handler)),
                asyncio.create_task(self.consumer_handler(server, event_handler)),
            ],
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
        event_handler: EventHandler,
    ):
        """Handle incomming messages from client side of the WebSocket connexion.

        Args:
            server (WebSocketServerProtocol): WebSocket server side connexion.
            event_handler (EventHandler): Handler to transcribe messages into HippoGym events.
        """
        async for message in server:
            message = json.loads(message)  # Messages should be json deserialisable.
            event_handler.parse(message)
            await asyncio.sleep(0.01)

    async def producer_handler(
        self,
        server: WebSocketServerProtocol,
        event_handler: EventHandler,
    ):
        """Handle messages to send to the client side of the WebSocket connexion.

        Args:
            server (WebSocketServerProtocol): WebSocket server side connexion.
            event_handler (EventHandler): Handler to transcribe messages into HippoGym events.
        """
        done = False
        while not done:
            message = await self.producer(event_handler)
            if message == "done":
                message = {"done": True}
                done = True
            await server.send(json.dumps(message))

    async def producer(self, event_handler: EventHandler) -> Optional[Union[dict, str]]:
        """Produce messages to send to the client side of the WebSocket connexion.

        Args:
            event_handler (EventHandler): Handler to transcribe messages into HippoGym events.
        """
        while event_handler.out_q.empty():
            await asyncio.sleep(0.01)
        return event_handler.out_q.get()


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
