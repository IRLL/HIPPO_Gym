# HippoGym
## Human Input Parsing Platform for Openai Gym

### Table of Contents
1. [Purpose](#Purpose)
2. [System Overview](#System-Overview)
    - [WebSockets](#Websockets)
    - [System Architecture](#System-Architecture)
    - [RouteKeys](#RouteKeys)
    - [AWS Lambda Middleware](#AWS-Lambda-Middleware)
3. [Setting Up](#Setting-Up)
    - [Frontend Setup](#Frontend-Setup)
    - [Backend Setup](#Backend-Setup)
4. [Contributors](#Contributors)
5. [Additional Resources](#Additional-Resources)

## Purpose
HippoGym is a Python library designed for researchers and students focusing on human-AI interaction over the web. It simplifies the setup, execution, and management of experiments by providing an easy-to-use interface for [OpenAI Gym](https://gym.openai.com/) and supports custom built enviorments.



## System Overview
### Websockets
The [Websocket API](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api.html) by [Amazon Web Services](https://aws.amazon.com/) (AWS) provides the backbone for real-time, bi-directional communication between the client and the server in HippoGym. Specifically, it facilitates seamless interaction between the front-end, written in React, and the back-end `trial.py` logic. The `WebSocket` class, part of the back-end architecture, abstracts away the complexity of Websocket communications, allowing users to focus on human-AI interaction research.

In HippoGym, Websocket API enables:
- Real-time updates: For example, rendering frames in OpenAI Gym environments.
- Data Exchange: Messages containing experiment data are exchanged between the front-end and back-end.
- Data saving: Enabling the ability to save step/trial data in live time to allow to be fed into an external learning algorithm use.

With Websockets, you can easily send messages from the front-end to the back-end and vice versa without worrying about the underlying communication protocols.


### System Architecture
The architecture operates in the following sequence:
1. **Front-end Deployment**: Projects are deployed using React, then it can be accessed on the web for a user to connect to.
2. **Backend Connection**: Users run their custom `trial.py` after reading through the step files and before you enter the game page. 
3. **AWS Lambda**: The backendConnectionID is held in AWS Lambda server awaiting for the frontend to map to the backend.
4. **Front-end Launch**: On game launch, the frontend connects to the WebSocket server, sends a unique userID and sends the request to map the user with the backend.
5. **UserID Storage**: AWS Lambda stores the userID in a DynamoDB table for unique mapping.

This architecture ensures unique mapping and seamless communication between frontend and backend.
See below to get a brief overview of the current system design for connecting a client. 

![System Architecture](./images/system-design.png)

An example of how users appear on DynamoDB is shown 

![DynamoDB](./images/dynamodb-output.png)

Sometimes, clashes arise - please see [The Concurrent Connection Clash Problem](#aws-lambda-middleware) in the Lambda section to learn how to avoid this problem.

## RouteKeys
Route Keys serve as a routing mechanism in AWS Websocket API. A message must specify a Route Key to route it to the correct Lambda function. 

Example data:
```json
{
  "routeKey": "save",
  "data": 
    {
        'timestep': 0,
        'state': 1,
        'action': 'left'
    }
  
}
```

*Note routeKeys are case senesitive* 

Here are the current routeKeys we have avaliable:

![Route Keys](./images/route-keys.png)

When sending a message from either front-end or back-end, we must specify a Route Key from this list, along with any type of data we wish to send over. For more on sending and receiving messages, see [Setting Up](#setting-up).


## AWS Lambda Middleware
We use AWS Lambda as middleware for routing our websocket messages to the relevant service. Lambda detects which user is sending a message, and where its intended destination is, that be frontend or backend. The displayed Route Keys above route to our lambda websocket handler in which the lambda reads the route key and the "sendTo" message as part of our function definition for sending messages.
We use AWS Lambda as middleware for routing our websocket messages to the relevant component. Lambda detects which user is sending a message, and where its intended destination is, that be frontend or backend. The displayed Route Keys above route to our lambda websocket handler in which the lambda reads the route key and the "sendTo" message to determine where to send the message. For our example of starting the trial, the frontend sends a start message to the lambda handler that is then routed to the backend for further handling the start of the trial.

### The Concurrent Connection Collision Problem (CCC)
The Concurrent Connection Clash (CCC) Problem can can arise from the manner in which AWS Lambda handles connections. The CCC Problem emerges when users initiate backend and frontend connections in rapid succession. If a subsequent user's frontend connection occurs before the previous user's frontend connection, unintended session merging can happen.

For example, in a scenario where two users consecutively connect their backend and frontend components, the system might inadvertently merge their sessions. This leads to undesired outcomes such as loading issues and communication disruptions.

This behavior is attributed to AWS Lambda, which holds backend connections until the corresponding frontend connects. If a newer backend connection arrives before the intended frontend, the Lambda prioritizes the most recent backend connection, causing unexpected results.

To prevent the CCC Problem, it's advised that users connect their backend and frontend components in quick succession. By ensuring the backend connection precedes the frontend connection, the likelihood of timing-related clashes is minimized. This approach ensures smooth communication and maintains an uninterrupted user experience.

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
Supported by the Alberta Machine Intelligence Institute [(AMII)](https://amii.ca)

## Additional Resources
(Link to repositories and any other material)
