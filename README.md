# HippoGym
## Human Input Parsing Platform for Openai Gym

### Table of Contents
1. [Purpose](#Purpose)
2. [System Overview](#System-Overview)
    - [Websockets](#Websockets)
    - [System Architecture](#System-Architecture)
    - [RouteKeys](#RouteKeys)
    - [AWS Lambda Middleware](#AWS-Lambda-Middleware)
3. [Setting Up](#Setting-Up)
    - [Frontend Setup](#Frontend-Setup)
    - [Backend Setup](#Backend-Setup)
4. [Contributors](#Contributors)
5. [Additional Resources](#Additional-Resources)

## Purpose
HippoGym is a python library for simplifying human-ai interaction research over the web...

## System Overview
### Websockets
[Websocket API](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api.html) is a powerful tool from [Amazon Web Services](https://aws.amazon.com/) API Gateway that facilitates the bi-directional communication between a server and its corresponding client. In the case of HIPPO Gym, Websocket API is used to send communications between the frontend server hosting our react code for deploying experiments/projects and the backend server trial.py, which serves as the control logic for running and managing trials, sending/receiving WebSocket communications, and optionally receiving/storing trial data for a computer agent. The Websocket class, located in the backend websocket.py, uses methods to allow for seamless integration of websocket communications to ensure students/researchers will not need to go into the hidden layer of the websocket/trial logic used in HippoGym. 

### System Architecture
Our current system architechture for connecting a client is as follows:
We first deploy the given project in our front-end using React where we define the setup for the experiment and define the data we wish to send and receive. Note that AWS credentials are required to make any changes to the front-end component of HIPPO Gym, if you wish for front-end changes to be deployed, please refer to [Additional Resources](#Additional-Resources). To run the project, users must first connect their back-end component (more information on how in [backend setup](#backend-setup)), where their connectionID will be held in the [AWS Lambda server](#aws-lambda-middleware) awaiting for the frontend connection. At the launch of the frontend (after the final step page), the frontend connects to our websocket server, and sends the Lambda handler our uniquely generated userID. This userID get’s passed to the backend server to store and use for future connections to the experiment. Lambda stores the userID in a DynamoDB table to uniquely map each user individually based on their own backend connectionID and frontend connectionID to avoid clashes between systems in our experiment. 

An example of how users appear on DynamoDB is shown 
![DynamoDB](./images/dynamodb-output.png)

 Sometimes, clashes arise - please see [The Concurrent Connection Clash Problem](#aws-lambda-middleware) in the Lambda section to learn how to avoid this problem. See below to get a brief overview of the current system design for connecting a client. 

![System Architecture](./images/system-design.png)

## RouteKeys
In AWS Websocket API, Route Keys are a mechanisim for routing our websocket messages to the appropriate Lambda function to handle a message. If an unknown Route Key is passed, Websocket API will not handle the websocket message recieved. Here is a list of the current Route Keys we have in our Websocket API:

![Route Keys](./images/route-keys.png)

When sending a message from either front-end or back-end, we must specify a Route Key from this list, along with any type of data we wish to send over. For more on sending and reciving messages, see [Setting Up](#setting-up).


## AWS Lambda Middleware
We use AWS Lambda as middleware for routing our websocket messages to the relevant service. Lambda detects which user is sending a message, and where its intended destination is, that be frontend or backend. The displayed Route Keys above route to our lambda websocket handler in which the lambda reads the route key and the "sendTo" message as part of our function definition for sending messages.

## Setting Up
### Frontend Setup

Let’s dive into our React code to get a brief overview of we setup the frontend. In this usecase, we will be providing code snippets used for the [Mountain Car](https://www.gymlibrary.dev/environments/classic_control/mountain_car/) enviorment from OpenAI Gym. 

If you wish to make adjustments to the frontend, you may enter the [HIPPO_Gym_FrontEnd_React repo](https://github.com/IRLL/HIPPO_Gym_FrontEnd_React) and clone it as usual. You cd into the repository and run `npm install` to install the dependencies required for the frontend to work. Once you are in there, navigate to the `game.js` file found in HIPPO_Gym_FrontEnd_React/src/components/Game/game.js. For those curious you can always do a stack trace from main.js to explore all components of the frontend. Once you visit the game.js, most if not all of the code is under the main class of Game, here we define our initial states, components, props and more of what React has to offer. You may notice how one of the methods inside this Game class defines how we send messages to our websocket. The exact code can be viewed here. 
```javascript
   // Send data to websocket server in JSON format
   sendMessage = (routeKey, data) => {
       // action is added to indicate the routeKey for the backend.
       if (this.state.isConnection){
           this.websocket.send(JSON.stringify({
               action: routeKey,
               userId: USER_ID,
               sendTo: "backend",
               ...data
               }));
       }
   };

```
If you aren’t familiar with hashmaps, don’t worry about how this works; but rather understand that everytime we reference this function inside our game.js, we reference it as `this.sendMessage(“routeKey”, {data: wishToSend}` and example usage for this can be shown here, where we send a message under the “start” routeKey to trigger the userID dynamoDB update process. We first define our routekey = “start”, and then use a hashmap to send whatever form of data we want (we chose userID and projectID here). This part is standard in all experiments and will be done for you in the boilerplate code. We typically run this code after we establish a valid connection to our websocket server.
```javascript
this.sendMessage("start",{
             userId: USER_ID,
             projectId: PROJECT_ID,
         });

```

After we run the code above, the expected output we recieve is as follows: ```{'userId': <userID>, 'projectId': <projectID>}``` and that raw json gets parsed through our lambda handler and notifies the backend what our userID and projectID is for the given experiment.


Now you have gotten an example of how to send messages to our websocket, let's look at how we can recieve expected messages from our websocket. With every experiment, we want to render our UI for the frontend to able to visual a dynamic page. Usually our backend handles rendering the frames/displaying some sort of UI. Whether that is passing in componets for button data, or full scale enviorment npArray render frames provided from OpenAI Gym. See the example code below:

```javascript
this.websocket.onmessage = (message) => {
          if (message.data === "done") {
            //"done" means the game has ended
            this.setState({
              isEnd: true,
              gameEndVisible: true,
            });
          } else {
            //parse the data from the websocket server
            let parsedData = JSON.parse(message.data);
                        //Check if frame related information in response
            if (parsedData.env.frame && parsedData.env.frameId) {
              console.log("New frame detected.")
              let frame = parsedData.env.frame;
              let frameId = parsedData.env.frameId;
              // set new border color
              if ("borderColor" in parsedData) {
                this.setState({
                  borderColor: parsedData.borderColor,
                });
              }
                this.setState((prevState) => ({
                  // Set new frame ID
                  frameSrc: "data:image/jpeg;base64, " + frame,
                  frameCount: prevState.frameCount + 1,
                  frameId: frameId,
                }));

```

In the code above, we listen to any incoming websocket messages and parse the data from the message. If the websocket message sent from our backend contains the data:
```python
{'routeKey' = 'UI',
    {'env':
        {'frame': <frameData>,
         'frameId': <frameId>
        }
    }
}
```
then this code will be executed, notice how we use the routeKey here as UI, and then the data we send can be anything, or in this case; a nested dictionary. You may have also noticed how we check the websocket to see if the websocket message has the keyword done, that is the logic to end the game. 

We will explore more on how the backend sends this env frame data to the frontend. We have now fully gone over how the frontend sends and recieves data from a backend client now.


### Backend Setup
(Explain trial.py, WebSocket class, etc...)


## Contributors
Originally written by [Nick Nissen](https://nicknissen.com) and Yuan Wang

System upgrades and redesign by [Mohamed Al-Nassirat](https://www.linkedin.com/in/mohamed-al-nassirat-6893b9203/?originalSubdomain=ca) and [Vera Maoued](https://github.com/vmaoued)

Supervised by [Matt Taylor](https://drmatttaylor.net)
For the Intelligent Robot Learning Laboratory [(IRLL)](https://irll.ca) at the University of Alberta [(UofA)](https://ualberta.ca)

Supported by the Alberta Machine Intelligence Institure [(AMII)](https://amii.ca)

## Additional Resources
(Link to repositories and any other material)
