import asyncio
import logging
import ssl
import websockets
import json
from multiprocessing import Process, Pipe

from hippo_gym import HippoGym


class Comunicator:

    def __init__(self, address=None, port=5000, use_ssl=True, force_ssl=False, fullchain_path='SSL/fullchain.pem',
                 privkey_path='SSL/privkey.pem'):
        self.entry = 'entry'
        self.address = address
        self.port = port
        self.ssl = use_ssl
        self.force_ssl = force_ssl
        self.fullchain = fullchain_path
        self.privkey = privkey_path

    @staticmethod
    async def producer(websocket, pipe):
        if pipe.poll():
            message = json.dumps(pipe.recv())
            if message == 'done':
                await websocket.send('done')
                return True
            else:
                await websocket.send(message)
        return False

    @staticmethod
    async def consumer_handler(websocket, pipe):
        async for message in websocket:
            try:
                message = json.loads(message)
                pipe.send(message)
            except Exception as e:
                print(e)

    async def producer_handler(self, websocket, pipe):
        done = False
        while not done:
            done = await self.producer(websocket, pipe)
            await asyncio.sleep(0.01)
        return

    async def handler(self, websocket, path):
        up_pipe, down_pipe = Pipe()
        user_session = Process(target=HippoGym, args=(down_pipe,))
        user_session.start()
        consumer_task = asyncio.ensure_future(self.consumer_handler(websocket, up_pipe))
        producer_task = asyncio.ensure_future(self.producer_handler(websocket, up_pipe))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()
        await websocket.close()
        return

    def start(self):
        if not self.force_ssl:
            self.start_non_ssl_server()
        if self.ssl or self.force_ssl:
            self.start_ssl_server()

    def start_non_ssl_server(self):
        server = websockets.serve(self.handler, self.address, self.port)
        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_forever()
        logging.info('Non-SSL websocket started')

    def start_ssl_server(self):
        try:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(self.fullchain, keyfile=self.privkey)
            ssl_server = websockets.serve(self.handler, None, self.port, ssl=ssl_context)
            asyncio.get_event_loop().run_until_complete(ssl_server)
            asyncio.get_event_loop().run_forever()
            logging.info('SSL websocket started')
        except Exception as e:
            logging.info('SSL failed to initialize')
            logging.error(f'SSL failed with error: {e}')


def runner():
    com = Comunicator()
    com.start()


runner()
