import time
from hippogym import HippoGym
from hippogym.browser.control_panel import end_button

def main():
    hippo = HippoGym()
    while True:
        hippo.standby(play_grid)

def play_grid(hippo):
    grid = hippo.get_grid(rows=41,columns=42)
    grid.add_tile(20,21,text='Hello')
    grid.send()
    info = hippo.get_info_panel()
    control = hippo.get_control_panel()
    control.use_standard_buttons()
    control.send()
    while not hippo.stop:
        info.update(text="Selected Tiles:", items=grid.get_selected())
        time.sleep(1)
    hippo.disconnect()
    
if __name__ == '__main__':
    main()
