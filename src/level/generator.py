from pygame import Rect

class Generator:
    def __init__(self):
        pass

    def generate(self, level, centre, **kwargs):
        pass
    def expand(self, points, amount=1):
        for i in xrange(amount):
            for p in set(points):
                points |= set(((p[0]+1, p[1]), (p[0]-1, p[1]), (p[0], p[1]-1), (p[0], p[1]+1)))

    def draw_set(self, points, terrain):
        for p in points:
            self.level.set_terrain(p, terrain)

    def outline(self, points, eight=True):
        outline = set()
        if isinstance(points, Rect):
            outline |= set(self.level.get_line(points.left, points.top,
                                               points.left, points.bottom))
            outline |= set(self.level.get_line(points.left, points.bottom,
                                               points.right, points.bottom))
            outline |= set(self.level.get_line(points.right, points.bottom,
                                               points.right, points.top))
            outline |= set(self.level.get_line(points.right, points.top,
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
