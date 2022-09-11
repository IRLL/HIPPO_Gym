import os
import hippogym

from hippogym.handle_config import handle_config


def main():
    print(hippogym.__doc__)
    config_path = "config.yml"
    stepfiles_path = "StepFiles"
    project_config_path = ".project_config.yml"
    trial_config_path = ".trial_config.yml"

    if not os.path.exists(project_config_path) or not os.path.exists(trial_config_path):
        handle_config(
            config_path=config_path,
            stepfiles_path=stepfiles_path,
            project_config_path=project_config_path,
            trial_config_path=trial_config_path,
        )


if __name__ == "__main__":
    main()
