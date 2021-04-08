import ctypes

class TimingPoint:
    def __init__(self, offset, slider_multiplier, beat_duration):
        self.offset = offset
        self.slider_multiplier = slider_multiplier
        self.beat_duration = beat_duration

class HitObjects:
    def __init__(self, x, y, offset, obj):
        self.x = x
        self.y = y
        self.offset = offset
        self.obj = obj

class Circle(HitObjects):
    def __init__(self, x, y, offset, obj):
        super().__init__(x, y, offset, obj)

class Slider(HitObjects):
    def __init__(self, x, y, offset, obj, kind, pixel_length, repeat, points):
        super().__init__(x, y, offset, obj)
        self.kind = kind
        self.pixel_length = pixel_length
        self.repeat = repeat
        self.points = points

class Spinner(HitObjects):
    def __init__(self, offset, end_offset, obj):
        self.offset = offset
        self.end_offset = end_offset
        self.obj = obj


def parse_SL(file_):
    for line in file_.readlines():
        if line.startswith("StackLeniency:"):
            file_.seek(0)
            return float(line.split(":")[1])

def parse_SM(file_):
    for line in file_.readlines():
        if line.startswith("SliderMultiplier:"):
            file_.seek(0)
            return float(line.split(":")[1])

def parse_TPs(file_, dt=False, ht=False):
    TPs = []
    reach = False

    constant = 1
    if dt:
        constant = 2 / 3
    elif ht:
        constant = 4 / 3

    for line in file_.readlines():
        if line.startswith("[TimingPoints]"):
            reach = True

        elif reach:
            try:
                data = [float(x) for x in line.split(",")]
            except ValueError:
                break

            if data[1] >= 0:
                last_positive = data[1] * constant
                TPs.append(TimingPoint(data[0]*constant, 1, last_positive))
            else:
                if data[1] / -100 >= 1:
                    beat_duration = last_positive
                else:
                    beat_duration = last_positive * (data[1] / -100)
                TPs.append(TimingPoint(data[0]*constant, -100 / data[1], beat_duration))

    file_.seek(0)
    return TPs

def parse_HOs(file_, dt=False, ht=False):
    HOs = []
    reach = False
    spinner_types = (8, 12, 24, 28, 40, 44, 72, 76)

    screen_x, screen_y = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
    c = (4 / 3) / (1.0 * screen_x / screen_y)
    sx = screen_x / 2 - (0.8 * screen_x * c) / 2
    sy = 0.2 * screen_y * (11 / 19)

    constant = 1
    if dt:
        constant = 2 / 3
    elif ht:
        constant = 4 / 3

    for line in file_.readlines():
        if line.startswith("[HitObjects]"):
            reach = True

        elif reach:
            data = line.split(",")
            data[0] = int(sx + int(data[0]) * screen_x * 0.8 * c / 512)
            data[1] = int(sy + int(data[1]) * screen_y * 0.8 / 384)

            if len(data) == 1:
                break

            if int(data[3]) % 2 != 0:
                HOs.append(Circle(data[0], data[1], int(data[2]) * constant, 1))
            elif int(data[3]) in spinner_types:
                HOs.append(Spinner(int(data[2]) * constant, int(data[5]) * constant, 3))
            else:
                points = data[5][2:].split("|")

                for count, point in enumerate(points):
                    x, y = [int(x) for x in point.split(":")]
                    points[count] = (x, y)

                HOs.append(
                    Slider(data[0], data[1], int(data[2]) * constant, 2,
                    data[5][0], float(data[7]), int(data[6]), points)
                )

    return HOs
