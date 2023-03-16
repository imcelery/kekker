from pynput import mouse, keyboard
import time
import json

import PySimpleGUI as sg



class Keker:
    def __init__(self):
        self.mem = []
        self.is_record = False
        self.is_play = False
        self.count = 0
        self.needed_time = 0
        self.keyboard = keyboard.Controller()
        self.mouse = mouse.Controller()

        self.file = "file.txt"

        time.time()

        self.button_rec = 123
        self.button_play = 122

        def on_mouse_move(x, y):
            if self.is_record:
                self.mem.append([time.time(), "move", [x, y]])

        def on_mouse_click(x, y, button, pressed):
            if self.is_record:
                if button == mouse.Button.left:
                    a = "left"
                elif button == mouse.Button.right:
                    a = "right"
                else:
                    a = "middle"
                self.mem.append([time.time(), "click", [x, y, a, pressed]])


        def on_mouse_scroll(x, y, dx, dy):
            if self.is_record:
                self.mem.append([time.time(), "scroll", [x, y, dx, dy]])

        self.mouse_listener = mouse.Listener(
            on_move=on_mouse_move,
            on_click=on_mouse_click,
            on_scroll=on_mouse_scroll)
        self.mouse_listener.start()

        def on_press(key):
            if type(key) == keyboard.Key:
                key = key.value.vk

            elif type(key) == keyboard.KeyCode:

                key = key.vk

            if self.is_record and key != self.button_rec and key != self.button_play:
                self.mem.append([time.time(), "press", key])

        def on_release(key):
            if type(key) == keyboard.Key:
                key = key.value.vk

            elif type(key) == keyboard.KeyCode:

                key = key.vk



            if key == self.button_rec:
                self.pres_rec()

            elif key == self.button_play:
                self.pres_play()


            elif self.is_record:

                self.mem.append([time.time(), "release", key])

        self.key_listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release)
        self.key_listener.start()

    def pres_rec(self):
        self.is_record = not self.is_record
        if self.is_record:

            self.mem = []
            self.count = 0
        else:
            self.safe()

    def pres_play(self):
        if not self.is_play:
            if self.is_record:
                self.safe()

            self.load()

        self.is_play = not self.is_play
        self.count = 0

    def safe(self):
        a = {"m":self.mem}
        with open(self.file, "w") as write_file:
            json.dump(a, write_file)

    def load(self):
        with open(self.file, "r") as read_file:
            data = json.load(read_file)
            self.mem = data["m"]

    def change_settings(self, rec, play):
        self.button_rec = rec
        self.button_play = play

    def play(self):
        if self.is_play and time.time() >= self.needed_time:
            d = self.mem[self.count]
            if d[1] == "press":
                print(d[2])
                self.keyboard.press(keyboard.KeyCode.from_vk(d[2]))

            elif d[1] == "release":
                self.keyboard.release(keyboard.KeyCode.from_vk(d[2]))

            elif d[1] == "move":
                p = self.mouse.position
                self.mouse.move(d[2][0] - p[0], d[2][1] - p[1])

            elif d[1] == "click":
                a = {"left": mouse.Button.left, "right": mouse.Button.right, "middle": mouse.Button.middle}
                if d[2][3]:
                    self.mouse.press(a[d[2][2]])
                else:
                    self.mouse.release(a[d[2][2]])

            elif d[1] == "scroll":
                self.mouse.move(*d[2][2:])

            self.count += 1
            if self.count == len(self.mem):
                self.count = 0
                self.needed_time = time.time() + 1
            else:
                self.needed_time = time.time() + self.mem[self.count][0] - d[0]
        else:
            self.current_time = time.time()


def open_window(k):
    rec, play  = keyboard.KeyCode.from_char(k.button_rec).char ,keyboard.KeyCode.from_char(k.button_play).char
    layout = [[sg.Text("HotKeys", key="new")],
              [sg.Text('Record'), sg.InputText(default_text=rec)],
              [sg.Text('Play'), sg.InputText(default_text=play)],
              [sg.Button('Default'), sg.Button('Apply')]]

    setting_window = sg.Window("Second Window", layout, modal=True)

    while True:
        event, values = setting_window.read()

        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        if event == "Apply" or event == sg.WIN_CLOSED:
            k.change_settings(keyboard.KeyCode.from_char(layout[1][1].get()).vk, keyboard.KeyCode.from_char(layout[2][1].get()).vk)
            break

        if event == "Default":
            k.change_settings("f12", "f11")
            break

    setting_window.close()


if __name__ == '__main__':
    sg.theme('DarkAmber')

    menu_def = ['&File', ["---", "Settings", "---", "Exit"]],

    layout = [[sg.Menu(menu_def)],
              [sg.Button('Rec'), sg.Button('Play')]]


    window = sg.Window('Window Title', layout)

    k = Keker()
    while True:
        event, values = window.read(timeout=0)
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        if event == "Settings":
            open_window(k)
            
        if event == 'Rec':
            k.pres_rec()

        if event == 'Play':
            k.pres_play()


        k.play()

    window.close()