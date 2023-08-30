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
[Websocket API](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api.html) is a powerful tool from [Amazon Web Services](https://aws.amazon.com/) API Gateway that facilitates the bi-directional communication between a server and its corresponding client. In the case of HIPPO Gym, Websocket API is used to send communications between the frontend server hosting our react code for deploying experiments/projects and the backend server trial.py, which serves as the control logic for running and managing trials, sending/receiving WebSocket communications, and optionally storing trial data. The Websocket class, located in the backend websocket.py, uses methods to allow for seamless integration of websocket communications to ensure students/researchers will not need to go into the hidden layer of the websocket/trial logic used in HippoGym. 

### System Architecture
Here is our current system architecture, we first deploy the given trial/project in the front-end using React, and define the setup/configuration of our experiment and what is the data we wish to actually send and receive. We then connect to our websocket server, and send the lambda handler your uniquely generated userID. This userID get’s passed to the backend server and the backend connects to the websocket with this userID, the userID gets stored in a DynamoDB to uniquely map each user individually based on their own backend connectionID and frontend connectionID.  See below to get a brief overview of the current system design.   

![System Architecture](./images/system-design.png)

## RouteKeys
(Explain what a RouteKey is and how to use it. You can show a screenshot here as well.)

## AWS Lambda Middleware
(Your Lambda explanation goes here)


## Setting Up
### Frontend Setup

Let’s dive into our React code to get a brief overview of how you want to set up your frontend. You enter the [HIPPO_Gym_FrontEnd_React repo](https://github.com/IRLL/HIPPO_Gym_FrontEnd_React) and clone it as usual. You cd into the repository and run `npm install` to install the dependencies required for the frontend to work. Once you are in there, navigate to the `game.js` file found in HIPPO_Gym_FrontEnd_React/src/components/Game/game.js. For those curious you can always do a stack trace from main.js to explore all components of the frontend. Once you visit the game.js, most if not all of the code is under the main class of Game, here we define our initial states, components, props and more of what React has to offer. You may notice how one of the methods inside this Game class defines how we send messages to our websocket. The exact code can be viewed here. 
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
If you aren’t familiar with hashmaps, don’t worry about how this works; but rather understand that everytime we reference this function inside our game.js, we reference it as `this.sendMessage(“routeKey”, {data: wishToSend}` and example usage for this can be shown here, where we send a message under the “start” routeKey to trigger the userID dynamoDB update process. We first define our routekey = “start”, and then use a hashmap to send whatever form of data we want (we chose userID and projectID here). This part is standard in all experiments and will be done for you in the boilerplate code. We typically run this code after we make a connection to our websocket server.
```javascript
this.sendMessage("start",{
             userId: USER_ID,
             projectId: PROJECT_ID,
         });

```

### Backend Setup
(Explain trial.py, WebSocket class, etc...)


## Contributors
(Contributors and supervisors from existing README)

## Additional Resources
(Link to repositories and any other material)
