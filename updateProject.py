import json, yaml, boto3, os, logging, sys, subprocess
from dotenv import load_dotenv

load_dotenv()

def load_config():
    logging.info('Loading Config...')
    with open('config.yml','r') as infile:
        try:
            config = yaml.load(infile, Loader=yaml.FullLoader)
        except:
            config = yaml.load(infile) #shim for older versions of pyYaml
    projectConfig = config.get('project')
    if projectConfig.get('useAWS'):
        projectId = projectConfig.get('id')
        projectConfig['awsSetup']['containerName'] = projectId
        projectConfig['awsSetup']['repository'] = projectId
        projectConfig['ecsTask'] = projectId
        projectConfig['bucket'] = projectConfig.get('awsSetup').get('bucket')
        logging.info('Config Loaded')
    return projectConfig, config.get('trial')

def check_steps(projectConfig):
    logging.info('Checking StepFiles...')
    stepFiles = os.listdir('StepFiles')
    steps = projectConfig.get('steps').values()
    for step in steps:
        if step and step != 'game':
            assert step in stepFiles, f'File not found Error: File "{step}" Not Found in ./StepFiles'
    logging.info('StepFiles found.')
    return steps

def upload_file(file, bucket, projectId):
    logging.info(f'Uploading {file}...')
    s3 = boto3.resource('s3')
    object = s3.Object(bucket, f'{projectId}/{file}')
    with open(f'StepFiles/{file}', 'r') as infile:
        body = infile.read().encode('utf-8')
    response = object.put(
        ACL='private',
        Body=body,
        ContentEncoding='utf-8',
        StorageClass='STANDARD',
    )
    logging.info(f'{file} uploaded.')
    logging.debug(f'{file} upload response: {response}')

def upload_step_files(steps, projectConfig):
    logging.info('Uploading StepFiles...')
    for file in steps:
        if file and file != 'game':
            upload_file(file, projectConfig.get('awsSetup').get('bucket'), projectConfig.get('id'))
    logging.info('StepFiles Uploaded')

def update_project_master_list(projectConfig):
    logging.info('Updating Project Master List...')
    client = boto3.client('lambda', region_name='ca-central-1')
    response = client.invoke(
        FunctionName='HIPPO_Gym_update_project_master_list',
        InvocationType='RequestResponse',
        LogType='Tail',
        Payload=json.dumps(projectConfig)
    )
    payload = json.loads(response.get('Payload').read())
    assert payload.get('statusCode') == 200, f'Error From Lambda: {payload.get("body")}'
    logging.info('Project Master List Updated.')
    logging.debug(f'Update response: {response}')

def check_task_definition(projectConfig):
    logging.info('Checking Task Definition...')
    client = boto3.client('ecs', region_name=projectConfig.get('awsSetup').get('region'))
    response = client.list_task_definitions(familyPrefix=projectConfig.get('ecsTask'))
    logging.debug(response)
    if response.get('taskDefinitionArns'):
        logging.info(f'Task Definition {projectConfig.get("ecsTask")} Found.')
        return True
    logging.info(f'Task Definition {projectConfig.get("ecsTask")} Not Found.')
    return False

def register_task_definition(projectConfig):
    logging.info('Registering Task Definition...')
    client = boto3.client('ecs', region_name=projectConfig.get('awsSetup').get('region'))
    cpuConfig = projectConfig.get('awsSetup').get('cpu') or 2
    memConfig = projectConfig.get('awsSetup').get('memory') or 10
    response = client.register_task_definition(
        family = projectConfig.get('ecsTask'),
        executionRoleArn='arn:aws:iam::237796709103:role/ecsTaskExecutionRole',
        networkMode = 'awsvpc',
        containerDefinitions = [
            {
                'name': projectConfig.get('awsSetup').get('containerName'),
                'image': projectConfig.get('awsSetup').get('repositoryUri'),
                'portMappings': [
                    {
                        'containerPort': 5000,
                        'protocol': 'tcp'
                    }
                ],
            }
        ],
        requiresCompatibilities = ['FARGATE'],
        cpu = f'{cpuConfig} vCPU',
        memory = f'{memConfig} GB',
    )
    logging.debug(response)
    logging.info('Task Definition Registered.')

def check_repository(projectConfig):
    logging.info('Checking Repository...')
    client = boto3.client('ecr', region_name=projectConfig.get('awsSetup').get('region'))
    response = client.describe_repositories()
    logging.debug(response)
    repositories = response.get('repositories')
    repoExists = False
    for repo in repositories:
        if repo.get('repositoryName') == projectConfig.get('awsSetup').get('repository'):
            projectConfig['awsSetup']['repositoryUri'] = repo.get('repositoryUri')
            repoExists = True
            logging.info('Repository Found.')
    return repoExists, projectConfig

def create_repository(projectConfig):
    logging.info('Creating Repository...')
    client = boto3.client('ecr', region_name=projectConfig.get('awsSetup').get('region'))
    response = client.create_repository(
        repositoryName = projectConfig.get('awsSetup').get('repository')
    )
    projectConfig['awsSetup']['repositoryUri'] = response.get('repository').get('repositoryUri')
    logging.debug(response)
    logging.info('Repository Created')
    return projectConfig

def check_image(projectConfig):
    logging.info('Checking Docker Image...')
    client = boto3.client('ecr', region_name=projectConfig.get('awsSetup').get('region'))
    response = client.list_images(
        repositoryName = projectConfig.get('awsSetup').get('repository'),
        maxResults = 1
    )
    logging.debug(response)
    if response.get('imageIds'):
        logging.info('Image Found.')
        return True
    return False

def push_image(projectConfig, imageExists):
    if imageExists:
        push = input('Do you want to deploy docker now? [y/n]').strip().lower()
        if push not in ('y','yes'):
            return
    with open('App/xvfb.sh', 'r') as infile:
        instructions = infile.read()
        if "python3 communicator.py dev" in instructions:
            confirm = input('dev flag set in App/xvfb.sh file, ssl and s3uploading dissabled. Do you want to continue? [y/n]').strip().lower()
            if confirm not in ('y','yes'):
                sys.exit(1)
    imageAddress = projectConfig.get('awsSetup').get('repositoryUri')
    repository = projectConfig.get('awsSetup').get('repository')
    end = len(imageAddress) - len(repository) - 1
    repoAddress = imageAddress[:end]
    logging.info(repoAddress)
    output = os.system(f'aws ecr get-login-password --region ca-central-1 | docker login --username AWS --password-stdin {repoAddress}')
    logging.info(output)
    output = os.system(f'docker build -t {repository} .')
    logging.info(output)
    output = os.system(f'docker tag {repository}:latest {imageAddress}:latest')
    logging.info(output)
    output = os.system(f'docker push {imageAddress}:latest')
    logging.info(output)

def check_dependencies():
    dependencies = ['docker', 'aws']
    for depend in dependencies:
        output = subprocess.run(['which',f'{depend}'], stdout=subprocess.PIPE).stdout
        assert output, f'{depend} not found. Please install {depend} before continuing.' 
    return

def get_ssl_cert(projectConfig):
    logging.info('Checking for SSL Cert...')
    sslBucket = projectConfig.get('ssl').get('sslBucket')
    fullchain = projectConfig.get('ssl').get('fullchain')
    privkey = projectConfig.get('ssl').get('privkey')
    if sslBucket and fullchain and privkey:
        try:
            s3 = boto3.resource('s3')
            object = s3.Object(sslBucket, fullchain)
            object.download_file('App/fullchain.pem')
            object = s3.Object(sslBucket, privkey)
            object.download_file('App/privkey.pem')
            logging.info('SSL Cert files downloaded.')
            return
        except Exception as error:
            logging.info(error)
    os.system('chmod 600 App/privkey.pem')
    logging.info(f'Config entry for SSL Cert files not found')
    logging.info('SSL Cert files NOT downloaded.')
    return

def set_trial_config(trialConfig, projectConfig):
    logging.info('Setting Trial Config...')
    trialConfig['projectId'] = projectConfig.get('id')
    trialConfig['bucket'] = projectConfig.get('awsSetup').get('bucket')
    defaultUI = {'left':True,'right':True,'up':True,'down':True,'start':True,'pause':True}
    ui = list()
    uiConfig = trialConfig.get('ui', dict()) or defaultUI
    for key in uiConfig:
        if uiConfig.get(key):
            ui.append(key)
    trialConfig['ui'] = ui
    with open('App/.trialConfig.yml', 'w') as outfile:
        yaml.dump({'trial':trialConfig}, outfile)
    logging.info('trialConfig.yml Created')
    return trialConfig

def set_dotenv():
    logging.info('Copying .env to App...')
    os.system('cp .env App/.env')
    logging.info('.env Copied.')

def main():
    #logging.basicConfig(filename='Logs/updateProject.log', level=logging.INFO)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    projectConfig, trialConfig = load_config()
    trialConfig = set_trial_config(trialConfig, projectConfig)
    if projectConfig.get('useAWS'):
        check_dependencies()
        steps = check_steps(projectConfig)
        upload_step_files(steps, projectConfig)
        update_project_master_list(projectConfig)
        repoExists, projectConfig = check_repository(projectConfig)
        if not repoExists:
            projectConfig = create_repository(projectConfig)
        imageExists = check_image(projectConfig)
        get_ssl_cert(projectConfig)
        set_dotenv()
        push_image(projectConfig, imageExists)
        if not check_task_definition(projectConfig):
            register_task_definition(projectConfig)
    with open('.projectConfig.yml','w') as outfile:
        yaml.dump({'project':projectConfig,'trial':trialConfig}, outfile)

if __name__ == '__main__':
    main()
