import time
import math
import keyboard
import ctypes
import tkinter
from tkinter.filedialog import askopenfilename
import osu_parser

screen_x = ctypes.windll.user32.GetSystemMetrics(0)
screen_y = ctypes.windll.user32.GetSystemMetrics(1)
screen_dif = (0.6 / 19) * screen_y

def spin(duration):
    angle = 0
    end = time.time() + duration / 1000

    while end > time.time() and not keyboard.is_pressed("s"):
        x = int(math.cos(angle) * (screen_x * 0.025) + (screen_x / 2))
        y = int(math.sin(angle) * (screen_x * 0.025) + (screen_y + screen_dif) / 2)
    
        ctypes.windll.user32.SetCursorPos(x, y)
        angle += 1

def main():
    tkinter.Tk().withdraw()
    DT, HT = False, False
    LOADED = False
    f = None

    print(
        "Press L to load a map \n" \
        "Press P to start the map (TEMPORARY) " \
        "You can press S mid-map to stop. \n"
        "Press D to toggle DT, H to toggle HT.\n"
    )
    while True:
        if keyboard.is_pressed("l"):
            beatmap = askopenfilename(filetypes=[("Osu files", "*.osu")])

            try:
                f = open(file=beatmap, mode="r", encoding="utf8")
            except FileNotFoundError:
                continue

            HOs = osu_parser.parse_HOs(f, DT, HT)
            osu_parser.convert_coordinates(HOs)
            print("Loaded successfully")

            LOADED = True

        elif keyboard.is_pressed("p") and LOADED:
            tracker = 0
            start = time.time()

            while len(HOs) > tracker and not keyboard.is_pressed("s"):
                if (time.time() - start) * 1000 >= HOs[tracker].offset - HOs[0].offset:
                    if HOs[tracker].obj == 1:
                        ctypes.windll.user32.SetCursorPos(HOs[tracker].x, HOs[tracker].y)
                    elif HOs[tracker].obj == 2:
                        osu_parser.move(HOs[tracker].path, HOs[tracker].duration, HOs[tracker].repeat)
                    else:
                        spin(HOs[tracker].end_offset - HOs[tracker].offset)

                    tracker += 1

        elif keyboard.is_pressed("d") or keyboard.is_pressed("h"):
            if keyboard.is_pressed("d"):
                DT = not DT
                if HT: HT = False
            elif keyboard.is_pressed("h"):
                HT = not HT
                if DT: DT = False

            if f is not None:
                HOs = osu_parser.parse_HOs(f, DT, HT)
                osu_parser.convert_coordinates(HOs)
 
            print(f"DT: {DT}   HT: {HT}")
            time.sleep(0.1)

if __name__ == "__main__":
    main()
