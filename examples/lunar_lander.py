import logging
import time

import gym

from hippogym import HippoGym
from hippogym.ui_elements import InfoPanel, ControlPanel, standard_controls

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def play(hippo: HippoGym):
    window = hippo.get_game_window()

    control_panel = ControlPanel(
        hippo.out_q,
        buttons=standard_controls,
        keys=True,
    )
    hippo.set_control_panel(control_panel)

    info_panel = hippo.get_info_panel()
    info_panel.update(
        text="Use keyboard to play the game",
        items=["s = down", "a = left", "d = right"],
    )

    env = gym.make("LunarLander-v2")
    LOGGER.debug("Env created")

    send_render(env, window)
    hippo.start()
    while not hippo.stop:
        action = 0
        env.reset()
        while hippo.run:
            send_render(env, window)
            new_action = check_action(hippo, action)
            if new_action is not None:
                action = new_action
            if action < 0 or take_step(env, action, info_panel):
                break

            time.sleep(0.03)
        time.sleep(1)
    env.close()


def send_render(env, window):
    render = window.convert_numpy_array_to_base64(env.render("rgb_array"))
    window.update(image=render)


def check_action(hippo, old_action):
    actions = ["noop", "right", "down", "left"]
    combo = ["upleft", "upright", "downleft", "downright"]
    first_action = None
    action = None
    for item in hippo.poll():
        action = item.get("ACTION", None)
        if action in combo:
            print(action)
            action = action.replace(actions[old_action], "")
        if action in actions:
            print(action)
            if not first_action:
                first_action = action
            elif action == "noop":
                action = first_action
        button = item.get("BUTTONPRESSED", None)
        if button == "reset":
            print("RESETTING")
            return -1

    print("action", action)
    if action in actions:
        return actions.index(action)
    return None


def take_step(env, action, info_panel: InfoPanel):
    observation, reward, done, _ = env.step(action)
    info_panel.update(
        text="Observation:",
        items=observation.tolist(),
        key_value={"Reward": reward},
    )
    if done:
        info_panel.update(kv={"Score": reward})
    return done


def main():
    hippo = HippoGym()
    hippo.standby(play)


if __name__ == "__main__":
    main()
