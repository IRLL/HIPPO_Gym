import json
import websockets
import asyncio

class Websocket:
    def __init__(self, connection_url): 
        self.connection_url = connection_url
        self.websocket = None

    async def connectClient(self):
        retries = 0
        while retries < 5:
            try:
                self.websocket = await websockets.connect(self.connection_url)
                print("[INFO] Connected to WebSocket address")
                break
            except Exception as e:
                print(f"Failed to connect: {e}")
                retries += 1
                await asyncio.sleep(1)  # wait a bit before retrying


    async def sendData(self, routeKey, data):
        if self.websocket is not None:
            action_data = {"action": routeKey}
            action_data.update(data)
            await self.websocket.send(json.dumps(action_data))
            
    async def receive_data(self):
        if self.websocket is not None:
            message = await self.websocket.recv()
        try:
            message = json.loads(message)
            print("[INFO] Message from websocket reads: ", message)
        except:
            message = {'error': 'unable to parse message from websocket'}

        return message

async def main():
    trial = Websocket('wss://x4v1m0bphh.execute-api.ca-central-1.amazonaws.com/production?connection_type=backend')
    await trial.connectClient()


asyncio.run(main())
