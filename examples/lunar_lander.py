import logging
import time
import gym

from hippogym import HippoGym
from hippogym.ui_elements import InfoPanel, GameWindow, ControlPanel, standard_controls

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def send_render(env: gym.Env, window: GameWindow):
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
            action = action.replace(actions[old_action], "")
        if action in actions:
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
    window = GameWindow()
    info_panel = InfoPanel(
        text="Use keyboard to play the game",
        items=["s = down", "a = left", "d = right"],
    )
    control_panel = ControlPanel(
        buttons=standard_controls,
        keys=True,
    )

    hippo = HippoGym(ui_elements=[window, info_panel, control_panel])

    env = gym.make("LunarLander-v2")
    LOGGER.debug("Env created")

    hippo.standby()
    hippo.send()

    env.reset()
    while not hippo.stop:
        action = 0

        send_render(env, window)
        while hippo.run:
            new_action = check_action(hippo, action)
            if new_action is not None:
                action = new_action

            done = take_step(env, action, info_panel) or action < 0
            if done:
                env.reset()
                break
            send_render(env, window)

            time.sleep(0.03)
        time.sleep(1)
    env.close()


if __name__ == "__main__":
    main()
