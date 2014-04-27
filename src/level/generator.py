from pygame import Rect

from constants import LEFT, RIGHT, UP, DOWN

class Generator:
    def __init__(self, level):
        self.level = level
        self.x = 0
        self.y = 0

    def generate(self, level, centre, **kwargs):
        pass

    def translate(self, x, y):
        self.x += x
        self.y += y

    def transform(self, p):
        return (p[0]+self.x, p[1]+self.y)

    def transform_points(self, points):
        return [(p[0]+self.x, p[1]+self.y) for p in points]

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

    @staticmethod
    def rotate(p, c, amount, clockwise=True):
        """Rotate x,y around cx,cy by amount (1 = 90 degrees)"""
        if not clockwise:
            amount*=-1
        offsetx = (0, 1, 0, 1)[amount]
        offsety = (1, 0, 1, 0)[amount]
        signx = (-1, 1, 1, -1)[amount]
        signy = (-1, 1, 1, -1)[(amount+1) % 4]
        return (c[0] + (c[offsetx] - p[offsetx])*signx,
                c[1] + (c[offsety] - p[offsety])*-signy)

    @staticmethod
    def rotate_rect(rect, c, amount, clockwise=True):
        rect.left, rect.top = Generator.rotate((rect.left, rect.top), c, amount, clockwise)
        rect.w, rect.h = Generator.rotate((rect.w, rect.h), (0,0), amount, clockwise)
        rect.normalize()

    def draw(self, p, terrain):
        self.level.set_terrain(self.transform(p), terrain)

    def draw_points(self, points, terrain):
        for p in self.transform_points(points):
            self.level.set_terrain(p, terrain)

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

    def outline(self, shape, terrain):
        self.draw_points(self.get_outline(shape), terrain)

    @staticmethod
    def get_outlines(shapes, eight=True):
        """Get the outline of the union of several shapes"""
        # TODO: support any kind of shape
        union = set([p for shape in shapes for p in Generator.get_rect(shape)])
        if eight:
            return [p for shape in shapes for p in Generator.get_outline(shape)
                    if ((p[0]+1, p[1]) not in union or
                        (p[0]-1, p[1]) not in union or
                        (p[0], p[1]+1) not in union or
                        (p[0], p[1]-1) not in union or
                        (p[0]+1, p[1]+1) not in union or
                        (p[0]-1, p[1]-1) not in union or
                        (p[0]+1, p[1]-1) not in union or
                        (p[0]-1, p[1]+1) not in union)]
        else:
            return [p for shape in shapes for p in Generator.get_outline(shape)
                    if ((p[0]+1, p[1]) not in union or
                        (p[0]-1, p[1]) not in union or
                        (p[0], p[1]+1) not in union or
                        (p[0], p[1]-1) not in union)]

    @staticmethod
    def get_outline(shape, eight=True):
        """Get the outline of a shape"""
        outline = []
        if isinstance(shape, Rect):
            if eight:
                outline += [(shape.left, y) for y in xrange(shape.top, shape.bottom)]
                outline += [(x, shape.bottom-1) for x in xrange(shape.left, shape.right)]
                outline += [(shape.right-1, y) for y in xrange(shape.bottom-1, shape.top, -1)]
                outline += [(x, shape.top) for x in xrange(shape.right-1, shape.left, -1)]
            else:
                outline += [(shape.left, y) for y in xrange(shape.top+1, shape.bottom-1)]
                outline += [(x, shape.bottom-1) for x in xrange(shape.left+1, shape.right-1)]
                outline += [(shape.right-1, y) for y in xrange(shape.top+1, shape.bottom-1)]
                outline += [(x, shape.top) for x in xrange(shape.left+1, shape.right-1)]
        else:
            try:
                if len(shape) == 4:
                    outline += [(shape[0], y) for y in xrange(shape[1], shape[3])]
                    outline += [(x, shape[3]) for x in xrange(shape[0], shape[2])]
                    outline += [(shape[2], y) for y in xrange(shape[3], shape[1], -1)]
                    outline += [(x, shape[1]) for x in xrange(shape[2], shape[0], -1)]
            except TypeError:
                raise TypeError('Don\'t know how to make an outline for the given shape.')

        return outline
        #else:
        #    for p in points:
        #        if ((p[0]+1, p[1]) not in points or
        #            (p[0]-1, p[1]) not in points or
        #            (p[0], p[1]+1) not in points or
        #            (p[0], p[1]-1) not in points or
        #            eight and ((p[0]+1, p[1]+1) not in points or
        #                       (p[0]-1, p[1]-1) not in points or
        #                       (p[0]+1, p[1]-1) not in points or
        #                       (p[0]-1, p[1]+1) not in points)):
        #            outline.append(p)
        #return outline

    def fill_rect(self, *args):
        """Draw a filled rectangle with the given coordinates and dimensions"""
        try:
            rect = args[:-1]
            terrain = args[-1]
        except IndexError:
            raise TypeError('fill_rect expects a rect-style and terrain')
        self.draw_points(self.get_rect(*rect), terrain)

    @staticmethod
    def get_rect(*args):
        """Get all points in the described rectangle, inclusive"""
        rect = Rect(args)
        rect.normalize()
        return [(x, y) for x in xrange(rect.x, rect.x+rect.w)
                       for y in xrange(rect.y, rect.y+rect.h)]

    @staticmethod
    def expand(points, amount=1):
        for i in xrange(amount):
            for p in set(points):
                points |= set(((p[0]+1, p[1]), (p[0]-1, p[1]), (p[0], p[1]-1), (p[0], p[1]+1)))
