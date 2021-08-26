import sys
import time

from hippo_gym.hippo_gym import HippoGym
import play_lunar_lander


def main():
    hippo = HippoGym()

    hippo.standby()
    # Start Phase 1, play game
    group = hippo.group(12)
    print(group)
    play_lunar_lander.play(hippo)

    # Start Phase 2
    control = hippo.get_control_panel()
    control.reset()
    control.add_button(text="Finish", color='white', bgcolor='red', value='end', confirm=True)
    control.add_button(text="Run", color='white', bgcolor='green', value='run')
    control.add_button(text="Hide Game Window", color='white', bgcolor='blue', value='hide')
    control.add_button(text="Show Game Window", color='white', bgcolor='blue', value='show')
    info = hippo.get_info_panel()
    info.reset()
    window = hippo.get_game_window()
    textbox = hippo.add_text_box()
    textbox.update(text="Input Code Here")
    hippo.start()
    while not hippo.stop:
        if get_run(hippo):
            textbox.request()
            time.sleep(0.1)
            textbox.hide()
            do_stuff(textbox, window, info)
            textbox.send()
        time.sleep(0.1)
    print('All Done')
    hippo.disconnect()
    exit()

def do_stuff(textbox, window, info):
    window.send()
    text = textbox.get_text()
    print(text)
    try:
        text.append(33)
    except Exception as e:
        error = f'{sys.exc_info()}'
        info.update(text=error)
    time.sleep(2)

def get_run(hippo):
    for item in hippo.poll():
        button = item.get('BUTTONPRESSED', None)
        if button == 'run':
            return True
        if button == 'hide':
            hippo.get_game_window().hide()
        if button == 'hide':
            hippo.get_game_window().send()
    return False

if __name__ == '__main__':
    main()
