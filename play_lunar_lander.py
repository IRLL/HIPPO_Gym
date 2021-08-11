import time

import gym

from hippo_gym.hippo_gym import HippoGym


def play(hippo):
    window = hippo.get_game_window()
    control = hippo.get_control_panel()
    control.use_standard_buttons()
    control.update(keys=True)
    info_panel = hippo.get_info_panel()
    info_panel.update(text='Use keyboard to play the game', items=['s = down', 'a = left', 'd = right'])
    hippo.get_control_panel().send()
    env = gym.make('LunarLander-v2')
    send_render(env, window)
    send_render(env, window)
    while not hippo.stop:
        action = 0
        print(hippo.stop, hippo.run)
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
    print('All Done')


def send_render(env, window):
    render = window.convert_numpy_array_to_base64(env.render('rgb_array'))
    window.update(image=render)


def check_action(hippo, old_action):
    actions = ['noop', 'right', 'down', 'left']
    combo = ['upleft', 'upright', 'downleft', 'downright']
    first_action = None
    action = None
    for item in hippo.poll():
        action = item.get('ACTION', None)
        if action in combo:
            print(action)
            action = action.replace(actions[old_action], '')
        if action in actions:
            print(action)
            if not first_action:
                first_action = action
            elif action == 'noop':
                action = first_action
        button = item.get('BUTTONPRESSED', None)
        if button == 'reset':
            print('RESETTING')
            return -1

    print('action', action)
    if action in actions:
        return actions.index(action)
    return None


def take_step(env, action, info_panel):
    o, r, d, i = env.step(action)
    info_panel.update(text="Observation:", items=o.tolist(), kv=[{'Reward': r}])
    if d:
        info_panel.update(kv=[{'Score': r}])
    return d


def main():
    hippo = HippoGym()
    hippo.standby()
    play(hippo)


if __name__ == '__main__':
    main()
