import ctypes

class TimingPoint:
    def __init__(self, offset, slider_velocity, beat_duration):
        self.offset = offset
        self.slider_velocity = slider_velocity
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
    def __init__(self, x, y, offset, obj, kind, duration, repeat, sections):
        super().__init__(x, y, offset, obj)
        self.kind = kind
        self.duration = duration
        self.repeat = repeat
        self.sections = sections # change it to store the path

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
                velocity = 1
            else:
                velocity = -100 / data[1]

            TPs.append(TimingPoint(data[0]*constant, velocity, last_positive))

    file_.seek(0)
    return TPs

def parse_HOs(file_, dt=False, ht=False):
    HOs = []
    TPs = parse_TPs(file_, dt, ht)
    tps_tracker = 0
    SM = parse_SM(file_) * 100
    reach = False
    spinner_types = (8, 12, 24, 28, 40, 44, 72, 76)

    screen_x, screen_y = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
    c = (4 / 3) / (screen_x / screen_y)
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

            while float(data[2]) * constant >= TPs[tps_tracker + 1].offset:
                tps_tracker += 1

            if int(data[3]) % 2 != 0:
                HOs.append(Circle(data[0], data[1], int(data[2]) * constant, 1))
            elif int(data[3]) in spinner_types:
                HOs.append(Spinner(int(data[2]) * constant, int(data[5]) * constant, 3))
            else:
                sections, temp = [], [(data[0], data[1])]
                points = data[5][2:].split("|")
                tempc = 1

                for count, point in enumerate(points):
                    x, y = [int(x) for x in point.split(":")]
                    x = int(sx + x * screen_x * 0.8 * c / 512)
                    y = int(sy + y * screen_y * 0.8 / 384)

                    if len(temp) > 0 and (x, y) == (temp[tempc - 1][0], temp[tempc - 1][1]):
                        sections.append(temp)
                        temp = [(x, y)]
                        tempc = 1
                    else:
                        temp.append((x, y))
                        tempc += 1

                        if count + 1 == len(points):
                            sections.append(temp)

                duration = float(data[7]) / (SM * TPs[tps_tracker].slider_velocity) * TPs[tps_tracker].beat_duration

                HOs.append(
                    Slider(data[0], data[1], int(data[2]) * constant, 2,
                    data[5][0], round(duration), int(data[6]), sections)
                )

    return HOs

def coordinantesOnBezier(pointArray, t):
    bezierX = 0
    bezierY = 0
    degree = len(pointArray) - 1

    if (degree == 1):
        bezierX = (1 - t) * pointArray[0][0] + t * pointArray[1][0]
        bezierY = (1 - t) * pointArray[0][1] + t * pointArray[1][1]
    elif (degree == 2):
        bezierX = pow(1 - t, 2) * pointArray[0][0] + 2 * (1 - t) * t * pointArray[1][0] + pow(t, 2) * pointArray[2][0]
        bezierY = pow(1 - t, 2) * pointArray[0][1] + 2 * (1 - t) * t * pointArray[1][1] + pow(t, 2) * pointArray[2][1]
    elif (degree == 3):
        bezierX = pow(1 - t, 3) * pointArray[0][0] + 3 * pow(1 - t, 2) * t * pointArray[1][0] + 3 * (1 - t) * pow(t, 2) * pointArray[2][0] + pow(t, 3) * pointArray[3][0]
        bezierY = pow(1 - t, 3) * pointArray[0][1] + 3 * pow(1 - t, 2) * t * pointArray[1][1] + 3 * (1 - t) * pow(t, 2) * pointArray[2][1] + pow(t, 3) * pointArray[3][1]
    else:
        for i in range(degree + 1): 
            bezierX += binomialCoeficient(degree, i) * pow(1 - t, degree - i) * pow(t, i) * pointArray[i][0]
            bezierY += binomialCoeficient(degree, i) * pow(1 - t, degree - i) * pow(t, i) * pointArray[i][1]
    
    return bezierX, bezierY

def binomialCoeficient(n, k):
    result = 1

    if (k > n):
        return 0
    
    for temporary in range(1, k + 1):
        result *= n
        n -= 1
        result /= temporary

    return result
