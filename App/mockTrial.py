import numpy, json, shortuuid, time, base64, yaml, logging, os, xml.etree.ElementTree as ET, errno
from websocket import Websocket
import asyncio
import json
import os

TAG = "\033[1;35m[HIPPOGYM]\033[0m" 


class MockTrial():
    def __init__(self):
        self.websocket = Websocket()

    async def connect(self):
        await self.websocket.connectClient()
        if self.websocket.websocket is not None:
            await self.run()


    async def run(self):
        '''
        This is the main event controlling function for a Trial.
        It handles the render-step loop
        '''

        print(f'{TAG} Running Mock Trial...')
        print(f'{TAG} Lunar Lander experiment running...')
        '''
        Data from systemMessages comes in as:
        {
            'modality': 'demonstrationModality',
            'feedback': 
                [
                    {'x_pos': -0.3334961009832318, 'y_pos': 0.14425029292053648, 'x_vel': -0.03599388826892596, 'y_vel': 0.04228283072549631, 'angle': 0.07178081327470964, 'ang_vel': 0.031344930098219106, 'left_leg': 0, 'right_leg': 1}, 
                    {'x_pos': 0.18168127228942654, 'y_pos': -0.08991994618813282, 'x_vel': -0.015507494265744715, 'y_vel': -0.04493734540625748, 'angle': 0.022568375803750595, 'ang_vel': 0.030291540688396887, 'left_leg': 1, 'right_leg': 0}, 
                    {'x_pos': -0.5836754504513535, 'y_pos': 0.8628106033437015, 'x_vel': -0.04895845267484808, 'y_vel': -0.033963480704240503, 'angle': 0.06552900608809187, 'ang_vel': -0.010396571732503489, 'left_leg': 1, 'right_leg': 0}
                ]
        } 
        
        '''
        systemMessage = await self.websocket.recieveData() 
        modality = systemMessage['modality'] # access the modality
        feedback = systemMessage['feedback'] # access the data sent from the front-end
        if modality and feedback:
            print(f'{TAG} Modality selected:  {modality}')
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



            '''
                Example usage of saving data provided from websocket -> json
                await self.websocket.saveData(FileName, data, fileExt)
            '''
            print(TAG, "Saving data to /trials/MockFile")
            await self.websocket.saveData("MockFile",feedback)
            print(TAG, "Saving data to /trials/MockFileCSV")
            await self.websocket.saveData("MockFileCSV", feedback ,"csv")

        
        if modality == 'feedback':
            pass





async def main():
    mockTrial = MockTrial()
    await mockTrial.connect()


if __name__ == '__main__':
    asyncio.run(main())