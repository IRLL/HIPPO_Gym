import json
import websockets
import asyncio
import os

TAG = "\033[1;35m[HIPPOGYM]\033[0m" 

class Websocket:
    
    def __init__(self, connection_url = None):
        if connection_url is None:
            connection_url = 'wss://x4v1m0bphh.execute-api.ca-central-1.amazonaws.com/production?connection_type=backend'
        self.connection_url = connection_url
        self.websocket = None
        self.userID = None

    def setID(self, userID):
        self.userID = userID

    async def connectClient(self):
        retries = 0
        while retries < 5:
            try:
                self.websocket = await websockets.connect(self.connection_url)
                print(TAG, "Connected to WebSocket address")
                break
            except Exception as e:
                print(f"Failed to connect: {e}")
                retries += 1
                await asyncio.sleep(1)  # wait a bit before retrying


    async def sendData(self, routeKey, data):
        if self.websocket is not None:
            action_data = {"action": routeKey, "userId": self.userID, "sendTo" : "frontend" } 
            action_data.update(data)
            print(TAG, "Sending to websocket...", action_data)
            await self.websocket.send(json.dumps(action_data))
            
    async def recieveData(self):
        if self.websocket is not None:
            message = await self.websocket.recv()
        try:
            message = json.loads(message)
            print(TAG, "Message from websocket reads: ", message)
        except:
            message = {'error': 'unable to parse message from websocket'}
        return message
    
    async def saveData(self, fileName, data, fileExt=None):

        if not os.path.exists('Trials'):
            os.makedirs('Trials')
        if fileExt is None:
            fileExt = '.json'
        fileName = fileName + "." + fileExt

        file_path = os.path.join('Trials', fileName)
        with open(file_path, "w") as outfile:
            json.dump(data, outfile, indent=2)

        


    async def disconnectClient(self):
        if self.websocket is not None:
            print(f"{TAG} Disconnecting from WebSocket...")
            await self.websocket.close()
    