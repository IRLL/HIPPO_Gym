import asyncio, websockets, json, sys, pathlib, ssl
from trial import Trial
from multiprocessing import Process, Pipe
from s3upload import Uploader
import logging

ADDRESS = "localhost" # set desired IP for development 
PORT = 5005 # if port is changed here it must also be changed in Dockerfile
devEnv = False

logging.basicConfig(filename='server.log', level=logging.INFO)

def main():
    '''
    Check for command line arguement setting development environment.
    Start Websocket server at appropriate IP ADDRESS and PORT.
    '''
    global ADDRESS
    global PORT
    global devEnv
    if len(sys.argv) > 1 and sys.argv[1] == 'dev':
        start_server = websockets.serve(handler, ADDRESS, PORT)
        devEnv = True
    else:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain('fullchain.pem', keyfile='privkey.pem')
        start_server = websockets.serve(handler, None, PORT, ssl=ssl_context)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

async def handler(websocket, path):
    '''
    On websocket connection, starts a new userTrial in a new Process.
    Then starts async listeners for sending and recieving messages.
    '''
    upPipe, downPipe = Pipe()
    userTrial = Process(target=Trial, args=(downPipe,))
    userTrial.start()
    consumerTask = asyncio.ensure_future(consumer_handler(websocket, upPipe))
    producerTask = asyncio.ensure_future(producer_handler(websocket, upPipe))
    done, pending = await asyncio.wait(
        [consumerTask, producerTask],
        return_when = asyncio.FIRST_COMPLETED
    )
    for task in pending:
        task.cancel()
    await websocket.close()
    return

async def consumer_handler(websocket, pipe):
    '''
    Listener that passes messages directly to userTrial process via Pipe
    '''
    async for message in websocket:
        pipe.send(message)

async def producer_handler(websocket, pipe):
    '''
    Loop to call producer for messages to send from userTrial process.
    Note that asyncio.sleep() is required to make this non-blocking
    default sleep time is (0.01) which creates a maximum framerate of 
    just under 100 frames/s. For faster framerates decrease sleep time
    however be aware that this will affect the ability of the
    consumer_handler function to keep up with messages from the websocket
    and may cause poor performance if the web-client is sending a high volume
    of messages.
    '''
    done = False
    while True:
        done = await producer(websocket, pipe)
        await asyncio.sleep(0.01)
    return

async def producer(websocket, pipe):
    '''
    Check userTrial process pipe for messages to send to websocket.
    If userTrial is done, send final message to websocket and return
    True to tell calling functions that userTrial is complete.
    '''
    if pipe.poll():
        message = pipe.recv()
        if message == 'done':
            await websocket.send('done')
            return True
        elif 'upload' in message:
            await upload_to_s3(message)
        else:
            await websocket.send(message)
    return False

async def upload_to_s3(message):
    global devEnv
    logging.info(devEnv)
    if devEnv:
        logging.info('Dev set... Not uploading to s3.')
        return
    file = message['upload']['file']
    path = message['upload']['path']
    projectId = message['upload']['projectId']
    userId = message['upload']['userId']
    bucket = message['upload']['bucket']
    Process(target=Uploader, args=(projectId, userId, file, path, bucket)).start()

if __name__ == "__main__":
    main()
