import base64

from hippo_gym.hippo_gym import HippoGym

images = ['logo_vertical.png', 'icon_dark.png', 'words_horizontal.png', 'logo_horizontal.png', 'icon_light.png',
          'words_vertical.png']


def main():
    index = 0
    hippo = HippoGym()
    control_panel = hippo.get_control_panel()
    game_window = hippo.get_game_window()
    game_window.update(image=get_image(images[index//len(images)]))
    buttons = [{"Button": {"text": "start"}}]
    control_panel.update(buttons=buttons)
    while True:
        hippo.standby()
        for item in hippo.poll():
            action = item.get('ACTION', None)
            if action == 'right':
                index += 1
                game_window.update(image=get_image(images[index // len(images)]))
                control_panel.send_controls()
            elif action == 'left':
                index -= 1
                game_window.update(image=get_image(images[index // len(images)]))


def get_image(filename):
    with open(f'img/{filename}', 'rb') as infile:
        frame = base64.b64encode(infile.read()).decode('utf-8')
    return frame


if __name__ == '__main__':
    main()
