import json
import yaml
import os
import logging
import sys
import subprocess
import boto3
from typing import Any, Dict, List, Union
from dotenv import load_dotenv

ConfigType = Dict[str, Union[dict, Any]]


def handle_config(
    config_path: str,
    stepfiles_path: str,
    project_config_path: str = ".project_config.yml",
    trial_config_path: str = ".trial_config.yml",
):
    # logging.basicConfig(filename='Logs/updateProject.log', level=logging.INFO)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    load_dotenv()
    project_config, trial_config = load_config(config_path)
    trial_config = set_trial_config(trial_config, project_config, trial_config_path)
    if project_config.get("useAWS"):
        check_dependencies()
        steps = check_steps(project_config)
        upload_step_files(steps, project_config, stepfiles_path)
        update_project_master_list(project_config)
        repoExists, project_config = check_repository(project_config)
        if not repoExists:
            project_config = create_repository(project_config)
        imageExists = check_image(project_config)
        get_ssl_cert(project_config)
        set_dotenv()
        push_image(project_config, imageExists)
        if not check_task_definition(project_config):
            register_task_definition(project_config)
    set_project_config(project_config, trial_config, project_config_path)


def load_config(config_path):
    with open(config_path, "r", encoding="utf-8") as infile:
        config: ConfigType = yaml.load(infile, Loader=yaml.FullLoader)
    logging.info("General config loaded from %s", config_path)

    project_config: ConfigType = config.get("project")
    if project_config.get("useAWS"):
        projectId = project_config.get("id")
        project_config["awsSetup"]["containerName"] = projectId
        project_config["awsSetup"]["repository"] = projectId
        project_config["ecsTask"] = projectId
        project_config["bucket"] = project_config.get("awsSetup").get("bucket")
        prettyconfig = json.dumps(project_config, indent=2)
        logging.info("Project config loaded:\n%s", prettyconfig)
    return project_config, config.get("trial")


def check_steps(project_config: ConfigType, stepfiles_path: str = "StepFiles"):
    step_files = os.listdir(stepfiles_path)
    steps = project_config.get("steps").values()
    for step in steps:
        if step and step != "game":
            assert (
                step in step_files
            ), f'File not found Error: File "{step}" Not Found in ./StepFiles'
    logging.info("StepFiles found in %s", stepfiles_path)
    return steps


def upload_step_files(
    steps: List[str],
    project_config: ConfigType,
    stepfiles_path: str,
):
    def upload_stepfile(s3object, stepfile: str, stepfiles_path: str):
        stepfile_path = os.path.join((stepfiles_path, stepfile))
        with open(stepfile_path, "r", encoding="utf-8") as infile:
            body = infile.read()
        response = s3object.put(
            ACL="private",
            Body=body,
            ContentEncoding="utf-8",
            StorageClass="STANDARD",
        )
        logging.info("Stepfile uploaded : %s", stepfile)
        logging.debug("Stepfile %s upload response: %s", stepfile, str(response))

    bucket = project_config.get("awsSetup").get("bucket")
    project_id = project_config.get("id")
    for stepfile in steps:
        if stepfile and stepfile != "game":
            s3object = boto3.resource("s3").Object(bucket, f"{project_id}/{stepfile}")
            upload_stepfile(
                s3object,
                stepfile,
                stepfiles_path,
            )
    logging.info("All Stepfiles Uploaded")


def update_project_master_list(project_config: ConfigType):
    logging.info("Updating Project Master List...")
    client = boto3.client("lambda", region_name="ca-central-1")
    response = client.invoke(
        FunctionName="HIPPO_Gym_update_project_master_list",
        InvocationType="RequestResponse",
        LogType="Tail",
        Payload=json.dumps(project_config),
    )
    payload = json.loads(response.get("Payload").read())
    assert payload.get("statusCode") == 200, f'Error From Lambda: {payload.get("body")}'
    logging.info("Project Master List Updated.")
    logging.debug(f"Update response: {response}")


def check_task_definition(project_config: ConfigType):
    logging.info("Checking Task Definition...")
    client = boto3.client(
        "ecs", region_name=project_config.get("awsSetup").get("region")
    )
    response = client.list_task_definitions(familyPrefix=project_config.get("ecsTask"))
    logging.debug(response)
    if response.get("taskDefinitionArns"):
        logging.info(f'Task Definition {project_config.get("ecsTask")} Found.')
        return True
    logging.info(f'Task Definition {project_config.get("ecsTask")} Not Found.')
    return False


def register_task_definition(project_config: ConfigType):
    logging.info("Registering Task Definition...")
    client = boto3.client(
        "ecs", region_name=project_config.get("awsSetup").get("region")
    )
    cpuConfig = project_config.get("awsSetup").get("cpu") or 2
    memConfig = project_config.get("awsSetup").get("memory") or 10
    response = client.register_task_definition(
        family=project_config.get("ecsTask"),
        executionRoleArn="arn:aws:iam::237796709103:role/ecsTaskExecutionRole",
        networkMode="awsvpc",
        containerDefinitions=[
            {
                "name": project_config.get("awsSetup").get("containerName"),
                "image": project_config.get("awsSetup").get("repositoryUri"),
                "portMappings": [{"containerPort": 5000, "protocol": "tcp"}],
            }
        ],
        requiresCompatibilities=["FARGATE"],
        cpu=f"{cpuConfig} vCPU",
        memory=f"{memConfig} GB",
    )
    logging.debug(response)
    logging.info("Task Definition Registered.")


def check_repository(project_config: ConfigType):
    logging.info("Checking Repository...")
    client = boto3.client(
        "ecr", region_name=project_config.get("awsSetup").get("region")
    )
    response = client.describe_repositories()
    logging.debug(response)
    repositories = response.get("repositories")
    repoExists = False
    for repo in repositories:
        if repo.get("repositoryName") == project_config.get("awsSetup").get(
            "repository"
        ):
            project_config["awsSetup"]["repositoryUri"] = repo.get("repositoryUri")
            repoExists = True
            logging.info("Repository Found.")
    return repoExists, project_config


def create_repository(project_config: ConfigType):
    client = boto3.client(
        "ecr", region_name=project_config.get("awsSetup").get("region")
    )
    response = client.create_repository(
        repositoryName=project_config.get("awsSetup").get("repository")
    )
    project_config["awsSetup"]["repositoryUri"] = response.get("repository").get(
        "repositoryUri"
    )
    logging.info("AWS repository Created : %s", response)
    return project_config


def check_image(project_config: ConfigType):
    logging.info("Checking Docker Image...")
    client = boto3.client(
        "ecr", region_name=project_config.get("awsSetup").get("region")
    )
    response = client.list_images(
        repositoryName=project_config.get("awsSetup").get("repository"), maxResults=1
    )
    logging.debug(response)
    if response.get("imageIds"):
        logging.info("Image Found.")
        return True
    return False


def push_image(project_config: ConfigType, imageExists: bool):
    if imageExists:
        push = input("Do you want to deploy docker now? [y/n]").strip().lower()
        if push not in ("y", "yes"):
            return
    with open("src/hippogym_app/xvfb.sh", "r") as infile:
        instructions = infile.read()
        if "python3 communicator.py dev" in instructions:
            confirm = (
                input(
                    "dev flag set in src/hippogym_app/xvfb.sh file, ssl and s3uploading dissabled. Do you want to continue? [y/n]"
                )
                .strip()
                .lower()
            )
            if confirm not in ("y", "yes"):
                sys.exit(1)
    image_address = project_config.get("awsSetup").get("repositoryUri")
    repository = project_config.get("awsSetup").get("repository")
    end = len(image_address) - len(repository) - 1
    repo_address = image_address[:end]
    logging.info(repo_address)
    output = os.system(
        "aws ecr get-login-password --region ca-central-1 |"
        f" docker login --username AWS --password-stdin {repo_address}"
    )
    logging.info(output)
    output = os.system(f"docker build -t {repository} .")
    logging.info(output)
    output = os.system(f"docker tag {repository}:latest {image_address}:latest")
    logging.info(output)
    output = os.system(f"docker push {image_address}:latest")
    logging.info(output)


def check_dependencies():
    dependencies = ["docker", "aws"]
    for depend in dependencies:
        output = subprocess.run(["which", f"{depend}"], stdout=subprocess.PIPE).stdout
        assert output, f"{depend} not found. Please install {depend} before continuing."


def get_ssl_cert(project_config: Dict[str, dict]):
    logging.info("Checking for SSL Cert...")
    ssl_bucket = project_config.get("ssl").get("sslBucket")
    fullchain = project_config.get("ssl").get("fullchain")
    privkey = project_config.get("ssl").get("privkey")
    if ssl_bucket and fullchain and privkey:
        try:
            s3resource = boto3.resource("s3")
            s3object = s3resource.Object(ssl_bucket, fullchain)
            s3object.download_file("src/hippogym_app/fullchain.pem")
            s3object = s3resource.Object(ssl_bucket, privkey)
            s3object.download_file("src/hippogym_app/privkey.pem")
            logging.info("SSL Cert files downloaded.")
            return
        except Exception as error:
            logging.info(error)
    os.system("chmod 600 src/hippogym_app/privkey.pem")
    logging.info("Config entry for SSL Cert files not found")
    logging.info("SSL Cert files NOT downloaded.")


def set_trial_config(
    trial_config: Dict[str, dict],
    project_config: Dict[str, dict],
    trial_config_path: str,
):
    trial_config["projectId"] = project_config.get("id")
    trial_config["bucket"] = project_config.get("awsSetup").get("bucket")
    defaultUI = {
        "left": True,
        "right": True,
        "up": True,
        "down": True,
        "start": True,
        "pause": True,
    }
    ui = list()
    ui_config = trial_config.get("ui", dict()) or defaultUI
    for key in ui_config:
        if ui_config.get(key):
            ui.append(key)
    trial_config["ui"] = ui
    with open(trial_config_path, "w", encoding="utf-8") as outfile:
        yaml.dump({"trial": trial_config}, outfile)
    logging.info("Trial config saved at %s", trial_config_path)
    return trial_config


def set_project_config(
    project_config: ConfigType,
    trial_config: ConfigType,
    project_config_path: str,
):
    with open(project_config_path, "w", encoding="utf-8") as outfile:
        yaml.dump({"project": project_config, "trial": trial_config}, outfile)
    logging.info("Project config saved to %s", project_config_path)


def set_dotenv():
    logging.info("Copying .env to src/hippogym_app...")
    os.system("cp .env src/hippogym_app/.env")
    logging.info(".env Copied.")
