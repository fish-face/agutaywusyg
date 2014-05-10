import re
import math
from pygame import Rect


def dist_2(a, b):
    return (b[0]-a[0])**2 + (b[1]-a[1])**2


def manhattan(a, b):
    return abs(b[0]-a[0]) + abs(b[1]-a[1])


def sup_dist(a, b):
    return max(abs(b[0]-a[0]), abs(b[1]-a[1]))

text_compare_re = re.compile('[\W_]+')

ENE = math.tan(math.pi/8.0)
NNE = math.tan(3*math.pi/8.0)
EENE = math.tan(math.pi/16.0)
NENE = math.tan(3*math.pi/16.0)
ENNE = math.tan(5*math.pi/16.0)
NNNE = math.tan(7*math.pi/16.0)

compass_words = {
    'N': 'North',
    'E': 'East',
    'S': 'South',
    'W': 'West',
    'NE': 'Northeast',
    'NW': 'Northwest',
    'SE': 'Southeast',
    'SW': 'Southwest',
    'NNE': 'North-northeast',
    'NNW': 'North-northwest',
    'ENE': 'East-northeast',
    'WNW': 'West-northwest',
    'SSE': 'South-southeast',
    'SSW': 'South-southwest',
    'ESE': 'East-southeast',
    'WSW': 'West-southwest',
}

compass_letters = (
    "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW",
    "W", "WNW", "NW", "NNW",
    "N", "NNE", "NE", "ENE",
)

compass_angles = dict(
    (letters, math.pi * 2 / len(compass_letters) * i)
    for i, letters in enumerate(compass_letters))

def angle_diff(a, b):
    return (b - a + math.pi) % (math.pi * 2) - math.pi

def compass_to(a, b, precision=2):
    angle_to = math.atan2(b[1] - a[1], b[0] - a[0])

    def distance(item):
        return abs(angle_diff(angle_to, item[1])) if len(item[0]) <= precision else math.pi

    return min(compass_angles.items(), key=distance)[0]

def canonicalise(string):
    return text_compare_re.sub('', unicode(string).lower())

def match_topic(a, b):
    return canonicalise(a) == canonicalise(b)

if __name__ == "__main__":
    point = [int(coord) for coord in raw_input("x,y,prec: ").split(",")]
    print compass_to((0, 0), point[:2], point[2])
