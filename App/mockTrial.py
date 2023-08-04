import numpy, json, shortuuid, time, base64, yaml, logging, os, xml.etree.ElementTree as ET, errno
from websocket import Websocket
import asyncio
import json
import os

TAG = "\033[1;35m[HIPPOGYM]\033[0m" 


class MockTrial():
    def __init__(self, connection_url):
        self.websocket = Websocket(connection_url)

    async def connect(self):
        await self.websocket.connectClient()
        if self.websocket.websocket is not None:
            await self.run()


    async def run(self):
        '''
        This is the main event controlling function for a Trial.
        It handles the render-step loop
        '''

        print(f'{TAG} Running trial...')
        systemMessage = await self.websocket.recieveData()
        modality = systemMessage['modality']
        feedback = systemMessage['feedback']
        if modality and feedback:
            print(f'{TAG} Modality selected:  {modality}\n')
            print(f'{TAG} Feedback from {modality} is: \n{feedback}')

        # Example usage of iterating through feedback from demonstrationModality
        if modality == 'demonstrationModality':
            for time_step in feedback:
                '''
                In this example, if the learning algorithm expects paramaters of the x_pos and y_pos
                of the lunar lander aircraft, then we can access it as follows and feed it in
                '''
                x_pos = time_step['x_pos']
                y_pos = time_step['y_pos']
                '''
                Now that we have a reference to the given x_pos and y_pos, we can
                feed into algorithm as follows:
                e.g
                class LearningAlgorithm():
                    def __init__(self):
                        omitted code....

                    def feedToAlgorithm(self, x_pos, y_pos):
                        # do something with x_pos, y_pos

                So in this code we can feed in as follows
                LearningALgorithm.feedToAlgorithm(x_pos, y_pos)
                '''

                print(f"{TAG} Modality Data:\n x_pos: {x_pos}, y_pos: {y_pos}")
        
        if modality == 'feedback':
            pass



        '''
        Now we have a reference to the feedback evaluation from the user, and now can use it
        to feed in the learning algorithm such as
        someRandomAlgorithm(feedback -> param for learning)
        
        '''



async def main():
    mockTrial = MockTrial('wss://x4v1m0bphh.execute-api.ca-central-1.amazonaws.com/production?connection_type=backend')
    await mockTrial.connect()


if __name__ == '__main__':
    asyncio.run(main())