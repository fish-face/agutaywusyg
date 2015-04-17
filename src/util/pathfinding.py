import heapq


class ObstacleGrid(object):
    """
    Implements a basic weighted graph interface. Supply it with a Rect and a sequence of impassable points, then
    neighbors(p) will return the elements of the Rect that are accessible from p.
    """
    def __init__(self, rect, obstacles):
        self.rect = rect
        self.obstacles = set(obstacles)

    def in_bounds(self, p):
        x, y = p
        return (self.rect.x <= x < self.rect.right and
                self.rect.y <= y < self.rect.bottom)

    def neighbours(self, p):
        x, y = p
        return [p for p in ((x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)) if
                p not in self.obstacles and
                self.rect.x <= x < self.rect.right and
                self.rect.y <= y < self.rect.bottom]
        # return [p for p in ((x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)) if p not in self.obstacles and self.in_bounds(p)]
        # results = [p for p in results if p not in self.obstacles and self.in_bounds(p)]
        # return results

    def cost(self, p1, p2):
        return 1


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def __nonzero__(self):
        return len(self.elements) != 0

    def push(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def pop(self):
        return heapq.heappop(self.elements)[1]


def dijkstra(graph, start, end, early_exit=True, straighten=False, next_node=None):
    """
    Create and return a dijkstra map
    @type straighten: bool
    @param graph : ObstacleGrid
    @param start : object
    @param end : object
    @param early_exit : bool

    @rtype : (list, dict)
    """
    frontier = PriorityQueue()
    frontier.push(start, 0)
    predecessor = {}
    cost = {}
    predecessor[start] = (0, 0)  # Doesn't really make sense but provides values for px, py
    cost[start] = 0

    if next_node:
        predecessor[next_node] = start
        cost[next_node] = graph.cost(start, next_node)
        frontier.push(next_node, cost[next_node])

    # Reduce member lookups
    neighbour_func = graph.neighbours
    cost_func = graph.cost
    pop = frontier.pop
    push = frontier.push

    while frontier:
        current = pop()
        if current == end and early_exit:
            break

        cx, cy = current
        px, py = predecessor[current]

        for next_node in neighbour_func(current):
            if straighten:
                prev_dx, prev_dy = cx - px, cy - py
                dx, dy = next_node[0] - cx, next_node[1] - cy
                direction_change_cost = 0.001 if dx != prev_dx or dy != prev_dy else 0
            else:
                direction_change_cost = 0
            # new_cost = cost[current] + graph.cost(current, next) + direction_change_cost
            new_cost = cost[current] + 1 + direction_change_cost
            if next_node not in cost or new_cost < cost[next_node]:
                cost[next_node] = new_cost
                push(next_node, new_cost)
                predecessor[next_node] = current

    return predecessor, cost


class NoPathError(ValueError):
    pass


def pathfind(graph, start, goal, straight=True, next=None):
    """
    Return a path starting at start and ending at goal. Possibly try and create a nice path.
    @param graph: ObstacleGrid : Or another type implementing a neighbours() method
    @param start: (int, int) : Or whatever kind of value you put in @param graph. Must be in @param graph.
    @param goal: (int, int) : As for start.
    @param straight: bool : Whether to prefer paths which go straight (rather than diagonal)
    @param next: (int, int) : As for start. Tries to pre-seed the straightening heuristic.
    @return: list of [(int, int)]
    """
    predecessor, cost = dijkstra(graph, start, goal, True, straight, next)
    try:
        return get_path(predecessor, start, goal)
    except NoPathError:
        raise ValueError('No path exists between %s and %s in the supplied graph' % (start, goal))

def get_path(predecessor, start, goal):
    """
    Returns a path from start to goal based on the given predecessor map.
    @type predecessor dict of [(int, int), (int, int)]
    @type start (int, int)
    @type goal (int, int)
    @rtype list of [(int, int)]
    """
    current = goal
    path = [current]
    try:
        while current != start:
            current = predecessor[current]
            path.append(current)
    except KeyError:
        raise NoPathError('No path exists in the supplied predecessor map')

    path.reverse()

    return path