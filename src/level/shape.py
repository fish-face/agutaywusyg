from generator import Generator

class Shape(object):
    def __init__(self):
        pass

class ArbitraryShape(Shape):
    def __init__(self, points=set()):
        self.points = points

    def draw(self, gen, fill, stroke):
        assert isinstance(gen, Generator)
        if fill:
            gen.draw_points(self.points, fill)
        if stroke:
            stroke_points = gen.get_outline(self.points)
            gen.draw_points(stroke_points, stroke)
