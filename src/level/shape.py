from pygame.rect import Rect
from generator import Generator


class Shape(object):
    def __init__(self):
        self.points = set()
        self.outline_gaps = set()

    @property
    def outline(self):
        """
        The points making up the shape's boundary

        @return: Sequence[(int, int)]
        """
        return set(Generator.get_outline(self.points))

    @property
    def inner_edges(self):
        """
        The points of the shape's boundary that are not corners

        @return: Sequence[(int, int)]
        """
        inner_corners = []
        points = self.points
        for x, y in Generator.get_outline(points):
            if (((x - 1, y) in points and (x + 1, y) in points) or
                    ((x, y - 1) in points and (x, y + 1) in points)):
                inner_corners.append((x, y))

        return set(inner_corners)

    def draw(self, gen, fill, stroke):
        """
        Draws the shape to the level using the generator's settings
        @type gen: Generator
        @param gen: a Generator to use to draw
        @type fill: Terrain
        @param fill: Terrain to fill the shape with (or None)
        @type stroke: Terrain
        @param stroke: Terrain to draw the edge of the shape with (or None)
        """
        if fill:
            gen.draw_points(self.points, fill)
        if stroke:
            stroke_points = set(gen.get_outline(self.points)) - self.outline_gaps
            gen.draw_points(stroke_points, stroke)

    def __contains__(self, item):
        if isinstance(item, Shape):
            my_points = self.points
            return all((p in my_points for p in item.points))
        else:
            return item in self.points

    def collides(self, other):
        my_points = self.points
        if isinstance(other, Shape):
            return any((p in my_points for p in other.points))

        try:
            return any((p in my_points for shape in other for p in shape.points))
        except TypeError as e:
            raise e

    def collidelist(self, seq):
        return [i for i, shape in enumerate(seq) if self.collides(shape)]

    def __and__(self, other):
        return ArbitraryShape(self.intersection(other))

    def intersection(self, other):
        if isinstance(other, Shape):
            return self.points & other.points
        else:
            return self.points & other

    def add_gaps(self, other):
        if isinstance(other, Shape):
            self.outline_gaps |= self.outline & other.points
        else:
            self.outline_gaps |= set(Generator.get_outline(self.points)) & other

    def mirror(self, axis, centre):
        """
        Return a mirrored copy of the shape
        @param axis: axis to mirror in
        @param centre: coordinate of mirror axis
        @return: Shape : the mirrored copy
        """

        new = ArbitraryShape(set(Generator.reflect_points(self.points, axis, centre)))
        new.outline_gaps = set(Generator.reflect_points(self.outline_gaps, axis, centre))
        return new


class ArbitraryShape(Shape):
    def __init__(self, points=set()):
        super(ArbitraryShape, self).__init__()
        self.points = points


class RectShape(Shape):
    def __init__(self, *args):
        super(RectShape, self).__init__()
        self.rect = Rect(*args)

    @property
    def points(self):
        return set(Generator.get_rect(self.rect))

    @points.setter
    def points(self, value):
        pass

    def mirror(self, axis, centre):
        new = RectShape(Generator.reflect_rect(self.rect, axis, centre))
        new.outline_gaps = set(Generator.reflect_points(self.outline_gaps, axis, centre))
        return new
