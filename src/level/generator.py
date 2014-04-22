from pygame import Rect

from constants import UP, DOWN, LEFT, RIGHT


class Generator:
    def __init__(self):
        pass

    def generate(self, level, centre, **kwargs):
        pass

    @staticmethod
    def coords_in_dir(x, y, d, l):
        """Return coordinates offset by l in cardinal direction d"""
        if d == RIGHT:
            return (x + l, y)
        elif d == UP:
            return (x, y - l)
        elif d == LEFT:
            return (x - l, y)
        elif d == DOWN:
            return (x, y + l)

    def draw_points(self, points, terrain):
        for p in points:
            self.level.set_terrain(p, terrain)

    @staticmethod
    def points_in(space):
        if isinstance(space, Rect):
            return [(x, y) for y in xrange(space.top, space.bottom+1)
                           for x in xrange(space.left, space.right+1)]
        else:
            return space

    def draw_line(self, x1, y1, x2, y2, terrain):
        self.draw_points(self.get_line(x1, y1, x2, y2), terrain)

    @staticmethod
    def get_line(x1, y1, x2, y2):
        """Return a list of points for the Bresenham line between the given coordinates."""
        points = []
        issteep = abs(y2-y1) > abs(x2-x1)
        if issteep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        rev = False
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            rev = True
        deltax = x2 - x1
        deltay = abs(y2-y1)
        error = int(deltax / 2)
        y = y1
        ystep = None
        if y1 < y2:
            ystep = 1
        else:
            ystep = -1
        for x in range(x1, x2 + 1):
            if issteep:
                points.append((y, x))
            else:
                points.append((x, y))
            error -= deltay
            if error < 0:
                y += ystep
                error += deltax
        # Reverse the list if the coordinates were reversed
        if rev:
            points.reverse()
        return points

    def draw_square(self, x1, y1, x2, y2, terrain):
        """Draw a filled rectangle with the given coordinates, inclusive"""
        self.draw_points(self.get_square(x1, y1, x2, y2), terrain)

    @staticmethod
    def get_square(x1, y1, x2, y2):
        """Get all points in the described rectangle, inclusive"""
        if y1 > y2:
            y1, y2 = y2, y1
        if x1 > x2:
            x1, x2 = x2, x1
        return [(x,y) for x in xrange(x1,x2+1) for y in xrange(y1,y2+1)]

    @staticmethod
    def expand(points, amount=1):
        for i in xrange(amount):
            for p in set(points):
                points |= set(((p[0]+1, p[1]), (p[0]-1, p[1]), (p[0], p[1]-1), (p[0], p[1]+1)))

    @staticmethod
    def outline(points, eight=True):
        outline = set()
        if isinstance(points, Rect):
            outline |= set(Generator.get_line(points.left, points.top,
                                              points.left, points.bottom))
            outline |= set(Generator.get_line(points.left, points.bottom,
                                              points.right, points.bottom))
            outline |= set(Generator.get_line(points.right, points.bottom,
                                              points.right, points.top))
            outline |= set(Generator.get_line(points.right, points.top,
                                              points.left, points.top))
        else:
            for p in points:
                if ((p[0]+1, p[1]) not in points or
                    (p[0]-1, p[1]) not in points or
                    (p[0], p[1]+1) not in points or
                    (p[0], p[1]-1) not in points or
                    eight and ((p[0]+1, p[1]+1) not in points or
                               (p[0]-1, p[1]-1) not in points or
                               (p[0]+1, p[1]-1) not in points or
                               (p[0]-1, p[1]+1) not in points)):
                    outline.add(p)
        return outline
