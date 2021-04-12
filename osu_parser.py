import ctypes
import math

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
    def __init__(self, x, y, offset):
        super().__init__(x, y, offset, 1)

class Slider(HitObjects):
    def __init__(self, x, y, offset, kind, duration, repeat, sections, path):
        super().__init__(x, y, offset, 2)
        self.kind = kind
        self.duration = duration
        self.repeat = repeat
        self.sections = sections
        self.path = path

class Spinner(HitObjects):
    def __init__(self, offset, end_offset):
        self.offset = offset
        self.end_offset = end_offset
        self.obj = 3


def convert_coordinates(point):
    screen_x = ctypes.windll.user32.GetSystemMetrics(0)
    screen_y = ctypes.windll.user32.GetSystemMetrics(1)

    c = (4 / 3) / (screen_x / screen_y)
    sx = screen_x / 2 - (0.8 * screen_x * c) / 2
    sy = 0.2 * screen_y * (11 / 19)

    new_x = int(sx + point[0] * screen_x * 0.8 * c / 512)
    new_y = int(sy + point[1] * screen_y * 0.8 / 384)

    return (new_x, new_y)

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

            if len(data) == 1:
                break

            while float(data[2]) * constant >= TPs[tps_tracker + 1].offset:
                tps_tracker += 1

            if int(data[3]) % 2 != 0:
                HOs.append(Circle(data[0], data[1], int(data[2]) * constant))
            elif int(data[3]) in spinner_types:
                HOs.append(Spinner(int(data[2]) * constant, int(data[5]) * constant))
            else:
                sections, temp = [], [(int(data[0]), int(data[1]))]
                points = data[5][2:].split("|")
                tempc = 1

                for count, point in enumerate(points):
                    x, y = [int(x) for x in point.split(":")]

                    if len(temp) > 0 and (x, y) == (temp[tempc - 1][0], temp[tempc - 1][1]):
                        sections.append(temp)
                        temp = [(x, y)]
                        tempc = 1
                    else:
                        temp.append((x, y))
                        tempc += 1

                        if count + 1 == len(points):
                            sections.append(temp)

                if data[5][0] in ("L",  "B"):
                    path = coordinantesOnBezier(sections, 0.01)
                else:
                    path = coordinantesOnPerfect(sections[0][0], sections[0][1], sections[0][2])

                duration = float(data[7]) / (SM * TPs[tps_tracker].slider_velocity) * TPs[tps_tracker].beat_duration

                HOs.append(
                    Slider(data[0], data[1], int(data[2]) * constant, data[5][0],
                    round(duration), int(data[6]), sections, path)
                )

    return HOs

def coordinantesOnBezier(sections, t):
    path = []

    for section in sections:
        t_aux = 0

        while t_aux <= 1:
            bezierX = 0
            bezierY = 0
            degree = len(section) - 1

            if (degree == 1):
                bezierX = (1 - t_aux) * section[0][0] + t_aux * section[1][0]
                bezierY = (1 - t_aux) * section[0][1] + t_aux * section[1][1]
            elif (degree == 2):
                bezierX = pow(1 - t_aux, 2) * section[0][0] + 2 * (1 - t_aux) * t_aux * section[1][0] + pow(t_aux, 2) * section[2][0]
                bezierY = pow(1 - t_aux, 2) * section[0][1] + 2 * (1 - t_aux) * t_aux * section[1][1] + pow(t_aux, 2) * section[2][1]
            elif (degree == 3):
                bezierX = pow(1 - t_aux, 3) * section[0][0] + 3 * pow(1 - t_aux, 2) * t_aux * section[1][0] + 3 * (1 - t_aux) * pow(t_aux, 2) * section[2][0] + pow(t_aux, 3) * section[3][0]
                bezierY = pow(1 - t_aux, 3) * section[0][1] + 3 * pow(1 - t_aux, 2) * t_aux * section[1][1] + 3 * (1 - t_aux) * pow(t_aux, 2) * section[2][1] + pow(t_aux, 3) * section[3][1]
            else:
                for i in range(degree + 1): 
                    bezierX += binomialCoeficient(degree, i) * pow(1 - t_aux, degree - i) * pow(t_aux, i) * section[i][0]
                    bezierY += binomialCoeficient(degree, i) * pow(1 - t_aux, degree - i) * pow(t_aux, i) * section[i][1]
            
            t_aux += t
            path.append((bezierX, bezierY))

    return path

def binomialCoeficient(n, k):
    result = 1

    if (k > n):
        return 0
    
    for temporary in range(1, k + 1):
        result *= n
        n -= 1
        result /= temporary

    return result

def coordinantesOnPerfect(pA, pB, pC):
    # Most of this function was taken from
    # https://github.com/CookieHoodie/OsuBot/blob/master/OsuBots/OsuBot.cpp
    path = []
    center = findCenter(pA, pB, pC)
    direction = calcDirection(pA, pB, pC)

    aSq = math.pow(pB[0] - pC[0], 2) + math.pow(pB[1] - pC[1], 2)
    bSq = math.pow(pA[0] - pC[0], 2) + math.pow(pA[1] - pC[1], 2)
    cSq = math.pow(pA[0] - pB[0], 2) + math.pow(pA[1] - pB[1], 2)

    linear_distance = math.sqrt(bSq)
    circle_distance = math.sqrt(aSq) + math.sqrt(cSq)

    if abs(linear_distance - circle_distance) < 0.01:
        return coordinantesOnBezier([[pA, pB, pC]], 0.01)

    radius = math.sqrt(math.pow(center[0] - pA[0], 2) + math.pow(center[1] - pA[1], 2))

    dist_pA_center_x = pA[0] - center[0]
    dist_pA_center_y = pA[1] - center[1]

    dist_pC_center_x = pC[0] - center[0]
    dist_pC_center_y = pC[1] - center[1]

    ang_start = math.atan2(dist_pA_center_y, dist_pA_center_x)
    ang_end = math.atan2(dist_pC_center_y, dist_pC_center_x)

    while ang_start > ang_end:
        ang_end += 2 * math.pi

    ang_range = ang_end - ang_start

    if (direction < 0):
        ang_range = 2 * math.pi - ang_range

    points = max(2, int(math.ceil(ang_range / (2 * math.acos(1 - 0.01 / radius)))))

    for i in range(points):
        fract = i / (points - 1)
        increment = direction * fract * ang_range
        ang = ang_start + increment

        x = int(center[0] + radius * math.cos(ang))
        y = int(center[1] + radius * math.sin(ang))

        path.append((x, y))

        # fix overshoot
        # distance = abs(increment * radius);

        # if (distance >= pixelLength)
        #     break;
    
    return path

def findCenter(A, B, C):
    x1 = A[0]
    x2 = B[0]
    x3 = C[0]

    y1 = A[1]
    y2 = B[1]
    y3 = C[1]

    x12 = x1 - x2
    x13 = x1 - x3
  
    y12 = y1 - y2
    y13 = y1 - y3
  
    y31 = y3 - y1
    y21 = y2 - y1
  
    x31 = x3 - x1
    x21 = x2 - x1
  
    sx13 = math.pow(x1, 2) - math.pow(x3, 2); 
  
    sy13 = math.pow(y1, 2) - math.pow(y3, 2); 
  
    sx21 = math.pow(x2, 2) - math.pow(x1, 2); 
    sy21 = math.pow(y2, 2) - math.pow(y1, 2); 

    f = ((sx13) * (x12) \
        + (sy13) * (x12) \
        + (sx21) * (x13) \
        + (sy21) * (x13)) \
        / (2 * ((y31) * (x12) - (y21) * (x13)))
    g = ((sx13) * (y12) \
        + (sy13) * (y12) \
        + (sx21) * (y13) \
        + (sy21) * (y13)) \
        / (2 * ((x31) * (y12) - (x21) * (y13)))
  
    c = -pow(x1, 2) - pow(y1, 2) - 2 * g * x1 - 2 * f * y1

    return (-g, -f)

def calcDirection(pA, pB, pC):
    s = (pB[0] - pA[0]) * (pC[1] - pA[1]) - (pC[0] - pA[0]) * (pB[1] - pA[1])

    if (s > 0): # clockwise
        return 1
    elif (s < 0): # counter clockwise
        return -1
    else: # colinear
        return 0
