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

def compass_to(a, b, precision=2):
    above = True if a[1] > b[1] else False
    try:
        slope = float(a[1]-b[1])/(b[0]-a[0])
    except ZeroDivisionError:
        if above:
            result = 'N'
        else:
            result = 'S'
    else:
        if precision == 3:
            if slope >= 0 and above:
                if slope < EENE:
                    result = 'E'
                elif slope < NENE:
                    result = 'ENE'
                elif slope < ENNE:
                    result = 'NE'
                elif slope < NNNE:
                    result = 'NNE'
                else:
                    result = 'N'
            elif slope >= 0 and not above:
                if slope < EENE:
                    result = 'W'
                elif slope < NENE:
                    result = 'WSW'
                elif slope < ENNE:
                    result = 'SW'
                elif slope < NNNE:
                    result = 'SSW'
                else:
                    result = 'S'
            elif slope < 0 and above:
                if slope > EENE:
                    result = 'W'
                elif slope > NENE:
                    result = 'WNW'
                elif slope > ENNE:
                    result = 'NW'
                elif slope > NNNE:
                    result = 'NNW'
                else:
                    result = 'N'
            elif slope < 0 and not above:
                if slope > EENE:
                    result = 'E'
                elif slope > NENE:
                    result = 'ESE'
                elif slope > ENNE:
                    result = 'SE'
                elif slope > NNNE:
                    result = 'SSE'
                else:
                    result = 'S'
        elif precision == 2:
            if slope > 0 and above:
                if slope < ENE:
                    result = 'E'
                elif slope < NNE:
                    result = 'NE'
                else:
                    result = 'N'
            elif slope > 0 and not above:
                if slope < ENE:
                    result = 'W'
                elif slope < NNE:
                    result = 'SW'
                else:
                    result = 'S'
            elif slope < 0 and above:
                if slope > ENE:
                    result = 'W'
                elif slope > NNE:
                    result = 'NW'
                else:
                    result = 'N'
            elif slope < 0 and not above:
                if slope > ENE:
                    result = 'E'
                elif slope > NNE:
                    result = 'SE'
                else:
                    result = 'S'
        elif precision == 1:
            if slope > 0 and above:
                if slope < 1:
                    result = 'E'
                else:
                    result = 'N'
            elif slope > 0 and not above:
                if slope < 1:
                    result = 'W'
                else:
                    result = 'S'
            elif slope < 0 and above:
                if slope > 1:
                    result = 'W'
                else:
                    result = 'N'
            elif slope < 0 and not above:
                if slope > 1:
                    result = 'E'
                else:
                    result = 'S'

    try:
        return compass_words[result]
    except NameError:
        print 'No result for', slope, above, precision
        return compass_words['N']

def canonicalise(string):
    return text_compare_re.sub('', unicode(string).lower())

def match_topic(a, b):
    return canonicalise(a) == canonicalise(b)
