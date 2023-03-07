# HIPPO Gym

##### Human Input Parsing Platform for Openai Gym

[hippogym.irll.net](https://hippogym.irll.net)

Written by [Nick Nissen](https://nicknissen.com), Payas Singh, Nadeen Mohammed, and Yuan Wang
Supervised by [Matt Taylor](https://drmatttaylor.net) and Neda Navi
For the Intelligent Robot Learning Laboratory [(IRLL)](https://irll.ca) at the University of Alberta [(UofA)](https://ualberta.ca)
Supported by the Alberta Machine Intelligence Institute [(AMII)](https://amii.ca)

For questions or support contact us at [hippogym.irll@gmail.com](mailto:hippogym.irll@gmail.com)

The HIPPO Gym Project contains 4 repositories:

1.  The main framework: [HIPPO_Gym](https://github.com/IRLL/HIPPO_Gym)

2.  The AWS code and instructions: [HIPPO_Gym_AWS](https://github.com/IRLL/HIPPO_Gym_AWS)

3.  The React Front End: [HIPPO_Gym_React_FrontEnd](https://github.com/IRLL/HIPPO_Gym_FrontEnd_React)

4.  The SSL Certificate Getter: [HIPPO_Gym_SSL](https://github.com/IRLL/HIPPO_Gym_SSL)

For members of the IRLL or anyone whose organization has already setup the AWS infrastructure, the only repo required is #1.

Anyone is welcome to use the front-end deployed to [irll.net](https://irll.net)

## Purpose:

HIPPO Gym is a framework for simplifying human-ai interaction research over the web.
The platform provides a communicator that opens a websocket to pass environment information to a browser-based front-end and recieve commands and actions from the front end. 

Built in Python, the framework is designed as a bring-your-own agent system where the framework provides an easy to impliment middle layer between a researcher's existing agent and a human interacting over the web. The framework is naive in that it makes no assumptions about how human input will be used, it simply provides the mechanism to pass along and record this information.

## Dependencies:

**System:** Linux, MacOs, WSL for Windows

**Packages:** Docker, AWS CLI

**Python** Python3.6+ required. Python3.7 recommended for Docker. Python3.8 used in AWS Lambda.

Note: At the time of writing OpenAI Gym supports up to Python3.7 

**PIP:** PyYaml, boto3, python-dotenv, gym, atari-py, shortuuid, asyncio, websockets, numpy, Pillow

Note: requirements.txt contains pip dependencies for building the Docker Image.

## Use:

communicator.py contains the main program. 
To run in development mode call:
    python3 communicator.py dev
To run in poduction on a server, the call can be done with nohup:
    nohup python3 communicator.py &
Note: fullchain.pem and privkey.pem files must be located in the running directory or the program will fail to run in production. These files provide the SSL certificate for secure communication and are mandatory for production.
ADDRESS and PORT constants are set in communicator.py change as required.
Defaults for development are:
ADDRESS = 'localhost'
PORT = 5000

To run in Docker in development mode add 'dev' to the end of line 3 in src/hippogym_app/xvfb.sh to be:

```bash
xvfb-run -s "-screen 0 1400x900x24" python3 communicator.py dev
```

Then to run the container locally run in the project root directory:

```bash
python3 updateProject.py # select 'n' when asked if you want to deploy the container
docker build -t hippo .
docker run --publish 5000:5000 --rm --name hippo hippo
```

You will now be able to connect to the websocket server at localhost:5000

To stop the docker container run:

```bash
docker stop hippo
```

## Instructions:

HIPPO Gym is designed to be run with distributed services provided by AWS. For instructions on setting up the AWS Services from scratch see AWS_README.md

Once AWS setup is complete, HIPPO Gym can be deployed by completing the config.yml file and then in a terminal running:

```bash
python3 updateProject.py
```

### Integrating the Agent:

The first step in setting up a research project is integrating the desired Agent with the HIPPO Gym framework. Due to requirements of human interaction it is important that the Trial class drives the initial calls to OpenAI gym functions. However, these calls can be intercepted and manipulated as desired for research. There are 5 key functions that must be provided to the Trial class. Examples can be seen in src/hippogym_app/agent.py

#### start(game:str)

Calls the gym.make() function and requires the environment to be returned.

#### step(env, action:int)

Calls the env.step(action) function. The Trial class will pass the human input with this call. This can be intercepted as required for the research. 

The return should be whatever needs to be recorded by the framework in dictionary format. The full return from this call will be saved in memory and then written to file either at the end of the episode or the end of the trial depending on the config.yml settings.

#### render(env)

Calls the env.render('rgb_array') function. 'rgb_array' must be set in order to pass an image to the browser. This function expects an npArray as a return. 

#### reset(env)

Calls env.reset() function which resets to a new episode.

#### close(env)

Calls env.close() which ends a trial. Once the Trial class has called the close() function, then the websocket will be closed and the participant will be moved on to the next step.

### Step Files:

For each step listed in config.yml there must be a file with matching name located in StepFiles/ This file must be an html file. The stepFiles are uploaded to S3 and then delivered by to the website when required for a project. Answers to questions are recorded along with other user information in the S3 bucket /projectId/users/userId

### Config.yml:

The config.yml file contains 2 root elements: project and trial.
Configuration files for the various components of HIPPO Gym are generated by updateProject.py and can be found at src/hippogym_app/.trialConfig.ym and ./projectConfig.yml

config.yml contains comments to guide input, the following is a detailed list of config items:

#### project config:

##### awsSetup:

Contains values specific to AWS

###### bucket:

This is the working bucket in S3 where your project_master_list.json is located. This is also where project folders will be located for storing of stepFiles, user data and trial data.

###### region:

This is the default reqion where your AWS services are hosted.

###### rootDomain:

This is the Domain name that is hosted in Route53 which will serve as the base domain for building the required subdomains for secure websocket servers. This does not need to be a true Root domain, it can be a subdomain, however all further subdomains will be built off of this entry. Domain name only, no https&#x3A;//

###### cpu:

The number of vCpu resources to be allocated via ECS FARGATE to each instance of the HIPPO Gym Docker container. Valid values are 1,2,4.

Depending on the multi-threading of the agent, 2 is generally sufficient.

**pricing: (USD at the time of writing)** (<https://aws.amazon.com/fargate/pricing/>)

FARGATE: per vCPU per hour: $0.04456
SPOT: per vCPU per hour: $0.013368

Note: HIPPO Gym by default tries to always use SPOT instances when possible.

###### memory:

The amount of memory to be allocated via ECS FARGATE to each instance of the HIPPO Gym Docker containre. Valid vales are tied to vCPU and are in 1GB increments:

1vCPU: 2-8
2vCPU: 4-16
4vCPU: 8-30

Memory requirements vary depending on the agent and what iformation about the observation is being stored. To limit memory use, episode-level dataFile settings will write memory to a pickle file after every episode completes and then purge memory. Recording full observations can get very large very fast. It is recommended to test your setup locally while running 'top' to determine memory use, then choosing this setting accordingly.

**pricing: (USD at the time of writing)** (<https://aws.amazon.com/fargate/pricing/>)

FARGATE: per GB per hour: $0.004865
SPOT: per GB per hour: $0.0014595

Note: HIPPO Gym by default tries to always use SPOT instances when possible.

##### events:

Define the steps at which the signal to start or stop server infrastructure will be sent. Typically startServerStep will be 1, however, if there are several steps prior to the participant reaching the game page then this could be done further into the steps. Note that it takes 3-5 minutes for all of the infrastruction to propagate. An example of a reason to delay the startServeStep would be participants needing to watch a 30 minute video prior to moving on. The stop server process happens almost instantly upon the step being reached.

###### startServerStep:

Integer relating to the step number on which to asyncronously start the server.

###### stopServerStep:

Integer relating to the step number on which to asyncronously stop the server.

##### id:

The projectId that will define this project within your organization. Must be unique to your organization. Can only contian Letters, Numbers, and Dashes (-). This value is used for most infrastructure setup, and files/folders related to this project will be found in bucket/projectId/ in S3.

##### live:

True or False. If True then infrastructure will be started and stepFiles delivered when requested from the webiste. If False then nothing will happen, it will be as if the project does not exist.

##### maxRuntime:

Integer value representing the number of minutes that the servers should run before being shut down. This provides a safety in terms of cost by ensuring that infrastructure is shutdown even if the participant does not make it to the stopServerStep. 

Note: The AWS setup does provide for a limit to this value, it is recommended to confirm with your organization's AWS Admin that this limit is long enough for your research.

##### name:

This can be any name that you would like to assign to the project. This value is not currently used other than as a label in the project_master_list.json file. There are no restrictions to the value.

##### researcher:

The primary researcher for this project. Currently only used in project_master_list.json for easy referencing of projects.

##### teamMembers:

The team members for this project. Currently only used in project_master_list.json for easy referencing of projects.

##### ssl:

SSL certificates are required for secure websocket communication. Browsers are moving towards requiring wss:// when accessing a websocker from a page with https&#x3A;// This requires a copy of the fullchain.pem and privkey.pem files to be located in the deployed docker image. To keep things simple and limit the number of requests sent to LetsEncrypt (which can lead to bans if excessive), HIPPO Gym assumes that recent certificate files will be placed in an S3 bucket. Certificates are valid for 90 days, therefore long running research projects may require rebuilding and redeployment of the docker image in order to maintain valid certificates.

For instructions on generating certificates see the SSL_README.md file.

###### sslBucket:

This is the bucket where your SSL files are stored. For security and/or convenience reasons this may be the same or different from the bucket listed under awsSetup.

###### fullchain:

The path to the fullchain.pem file withing the sslBucket. Note that the S3 api assumes the bucket/ portion of the path so you only need folderName/filename ie. SSL/fullchain.pem

###### privkey.pem:

The path to the privkey.pem file withing the sslBucket. Note that the S3 api assumes the bucket/ portion of the path so you only need folderName/filename ie. SSL/privkey.pem

##### step:

A dictionary of steps. The keys should be numbers, 1 indexed with values being the stepFile file name. For the game-play step make the value 'game'.

The 'finalStep' key is required, it can have the same value as the last numbered step.

#### trial:

##### actionBufferLifespan:

Integer. Open AI gym does not take the action value on every call to step(). Instead, the action value will be ignored based on a random number (for MsPacman the number is between 2-5). This makes playing as a human quite frustrating, as inputs are blatantly ignored up to 4/5 of the time. To manage this HIPPO Gym provides an optional actionBuffer that will store Human input for up to the actionBufferLifespan number of steps, or until a new Human input is recieved. This makes playing as a Human much more manageable, but may not be the desired approach for research. Set this value to 1 to have no action buffer and 5 to guarantee human input is taken. Note that different environments have different values.

##### maxEpisodes:

Integer. The number of episodes that will be played during the trial. After the last episode, the participant will be moved to the next step.

##### game:

The OpenAI gym game name to be played.

##### dataFile:

Valid Values: 'episode' or 'trial'. This determines whether the memory will be written to file after each episode or only after the trial is completed. If your memory requirement is low (ie deltas are used rather than full observations) then trial is ok. However, if memory requirments are high (ie full observations are saved for every step) then episode level storage is recommended. 

##### s3upload:

True of False. If True then episode/trial pickle files will be uploaded to S3 for future access. If False then no files will be uploaded. If set to False then data files will only reside in the filesystem of the machine running the code. If using AWS ECS, then this data will be lost when the container is shutdown.

Note that the 'dev' flag when running:

```bash
python3 communication.py dev
```

Will disable s3upload. Allowing for local testing without worrying about changing the config.

##### actionSpace:

List of strings. This is the ordered list of actions available for the desired environment. This is effectively used to generate the ENUM that will match actions provided by the UI via json to their numerical value required by OpenAI Gym step(). Note that the actionSpace is different for each game and needs to be verified by the researcher.

##### allowFramRateChange:

True or False. If True then the participant will be able to change the frame rate via UI input. If False then any frame rate change requests will be ignored. 

Note: If False then all other frame rate values are optional

##### frameRateStepSize:

Integer. The number of frames/second that the 'up' or 'down' buttons will adjust the frame rate.

##### minFrameRate:

The minimum value for frames/second.

##### maxFrameRate:

The maximum value for frames/second. There is an artificial limit of ~90 frames/second based on the async.sleep(0.01) setting in communicator.py should a higher framerate be desired then this value needs to be changed as well. However, OpenAI gym is nearly unplayable at 90 frames/second and framerates this high are not recommended.

##### startingFrameRate:

The frame rate at which a trial will start. Default is 30, which is both playable and not too slow for OpenAI Gym.

##### ui:

A dictionary of ui components (controls) that should be included or excluded in the game page. This allows a researcher to choose the ui components without having to write any code. Keys with values of True will be shown and keys with values of False will not be shown to participants.

Valid keys are:

-   left
-   right
-   up
-   down
-   start
-   stop
-   pause
-   reset
-   trainOffline
-   trainOnline
-   good
-   bad
-   fpsSet
-   fpsUp
-   fpsDown
