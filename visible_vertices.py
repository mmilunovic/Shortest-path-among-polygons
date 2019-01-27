from math import pi, sqrt, atan
from visgraph.graph import Point

INF = 10000
CCW = 1
CW = -1
COLLINEAR = 0
T = 10**10
T2 = 10.0**10

def visible_vertices(point, graph, origin=None, destination=None):

    edges = graph.get_edges()
    points = graph.get_points()
    if origin: points.append(origin)
    if destination: points.append(destination)

    points.sort(key=lambda p: (angle(point, p), edge_distance(point, p)))

    
    open_edges = OpenEdges()
    point_inf = Point(INF, point.y)

    for edge in edges:
        if point in edge: continue
        if edge_intersect(point, point_inf, edge):
            if on_segment(point, edge.p1, point_inf): continue
            if on_segment(point, edge.p2, point_inf): continue
            open_edges.insert(point, point_inf, edge)

    visible = []
    prev = None
    prev_visible = None

    for p in points:
        if p == point: continue
        
        is_visible = False

        # Ne kolinearne tacke
        if prev is None or ccw(point, prev, p) != COLLINEAR or not on_segment(point, prev, p):
            if len(open_edges) == 0:
                is_visible = True
            elif not edge_intersect(point, p, open_edges.smallest()):
                is_visible = True

        # Kolinearne tacke ali prethodna nije vidljiva iz p
        elif not prev_visible:
            is_visible = False

        # Kolinearne tacke ali je prethodna vidljiva iz p
        else:
            is_visible = True
            for edge in open_edges:
                if prev not in edge and edge_intersect(prev, p, edge):
                    is_visible = False
                    break
            if is_visible and edge_in_polygon(prev, p, graph):
                    is_visible = False

        # Provera da li je vidljiva tacka unutar nekog poligona
        if is_visible and p not in graph.get_adjacent_points(point):
            is_visible = not edge_in_polygon(point, p, graph)

        if is_visible: visible.append(p)

        # Dodaj edge u stablo
        for edge in graph[p]:
            if (point not in edge) and ccw(point, p, edge.get_adjacent(p)) == CCW:
                open_edges.insert(point, p, edge)

        prev = p
        prev_visible = is_visible

    return visible


def polygon_crossing(p1, poly_edges):
    """Vraća true ako je tačka p1 deo poligona."""
    p2 = Point(INF, p1.y)
    intersect_count = 0
    for edge in poly_edges:
        if p1.y < edge.p1.y and p1.y < edge.p2.y: continue
        if p1.y > edge.p1.y and p1.y > edge.p2.y: continue
        if p1.x > edge.p1.x and p1.x > edge.p2.x: continue

        edge_p1_collinear = (ccw(p1, edge.p1, p2) == COLLINEAR)
        edge_p2_collinear = (ccw(p1, edge.p2, p2) == COLLINEAR)
        if edge_p1_collinear and edge_p2_collinear: continue
        if edge_p1_collinear or edge_p2_collinear:
            collinear_point = edge.p1 if edge_p1_collinear else edge.p2
            if edge.get_adjacent(collinear_point).y > p1.y:
                intersect_count += 1
        elif edge_intersect(p1, p2, edge):
            intersect_count += 1
    if intersect_count % 2 == 0:
        return False
    return True


def edge_in_polygon(p1, p2, graph):
    """Vraća true ako je duž p1-p2 deo nekog poligona iz grafa."""
    if p1.polygon_id != p2.polygon_id:
        return False
    if p1.polygon_id == -1 or p2.polygon_id == -1:
        return False
    mid_point = Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
    return polygon_crossing(mid_point, graph.polygons[p1.polygon_id])


def point_in_polygon(p, graph):
    """Vraća true ako je tačka p u nekom od poligona."""
    for polygon in graph.polygons:
        if polygon_crossing(p, graph.polygons[polygon]):
            return polygon
    return -1

def edge_distance(p1, p2):
    """Vraca Euklidsku distancu izmedju dve tacke."""
    return sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)


def intersect_point(p1, p2, edge):
    """Vraca tacku u kojoj duž p1-p2 seče edge."""
    if p1 in edge: return p1
    if p2 in edge: return p2
    if edge.p1.x == edge.p2.x:
        if p1.x == p2.x:
            return None
        k = (p1.y - p2.y) / (p1.x - p2.x)
        intersect_x = edge.p1.x
        intersect_y = k * (intersect_x - p1.x) + p1.y
        return Point(intersect_x, intersect_y)

    if p1.x == p2.x:
        ek = (edge.p1.y - edge.p2.y) / (edge.p1.x - edge.p2.x)
        intersect_x = p1.x
        intersect_y = ek * (intersect_x - edge.p1.x) + edge.p1.y
        return Point(intersect_x, intersect_y)

    k = (p1.y - p2.y) / (p1.x - p2.x)
    ek = (edge.p1.y - edge.p2.y) / (edge.p1.x - edge.p2.x)
    if ek == k:
        return None
    intersect_x = (ek * edge.p1.x - k * p1.x + p1.y - edge.p1.y) / (ek - k)
    intersect_y = ek * (intersect_x - edge.p1.x) + edge.p1.y
    return Point(intersect_x, intersect_y)


def point_edge_distance(p1, p2, edge):
    """Vraca Euklidsku distancu od p1 do mesta gde seče edge ako prolazi kroz p2."""
    ip = intersect_point(p1, p2, edge)
    if ip is not None:
        return edge_distance(p1, ip)
    return 0


def angle(center, point):
    """Vraća ugao u radijanima između centra i pointa. """
    dx = point.x - center.x
    dy = point.y - center.y
    if dx == 0:
        if dy < 0:
            return pi * 3 / 2
        return pi / 2
    if dy == 0:
        if dx < 0:
            return pi
        return 0
    if dx < 0:
        return pi + atan(dy / dx)
    if dy < 0:
        return 2 * pi + atan(dy / dx)
    return atan(dy / dx)


def ccw(A, B, C):
    """Vraca 1 if counter clockwise, -1 if clock wise, 0 if kolinearne """
    area = int(((B.x - A.x) * (C.y - A.y) - (B.y - A.y) * (C.x - A.x))*T)/T2
    if area > 0: return 1
    if area < 0: return -1
    return 0


def on_segment(p, q, r):
    """Vraca true ako q lezi na duzi p-r."""
    if (q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)):
        if (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y)):
            return True
    return False


def edge_intersect(p1, q1, edge):
    """Vraca true ako duz p1-q1 sece edge."""
    p2 = edge.p1
    q2 = edge.p2
    o1 = ccw(p1, q1, p2)
    o2 = ccw(p1, q1, q2)
    o3 = ccw(p2, q2, p1)
    o4 = ccw(p2, q2, q1)

    if (o1 != o2 and o3 != o4):
        return True
    if o1 == COLLINEAR and on_segment(p1, p2, q1):
        return True
    if o2 == COLLINEAR and on_segment(p1, q2, q1):
        return True
    if o3 == COLLINEAR and on_segment(p2, p1, q2):
        return True
    if o4 == COLLINEAR and on_segment(p2, q1, q2):
        return True
    return False


class OpenEdges(object):
    def __init__(self):
        self._open_edges = []

    def insert(self, p1, p2, edge):
        self._open_edges.insert(self._index(p1, p2, edge), edge)

    """Vraća najlevlji list (prvi edge koji udara)"""
    def smallest(self):
        return self._open_edges[0]

    def _less_than(self, p1, p2, edge1, edge2):
        """Vraca true ako je edge1 manje od edge2, false u suprotnom."""
        if edge1 == edge2:
            return False
        if not edge_intersect(p1, p2, edge2):
            return True
        edge1_dist = point_edge_distance(p1, p2, edge1)
        edge2_dist = point_edge_distance(p1, p2, edge2)
        if edge1_dist > edge2_dist:
            return False
        if edge1_dist < edge2_dist:
            return True
        # Ako su udaljenosti iste moramo ugao da računamo
        if edge1_dist == edge2_dist:
            if edge1.p1 in edge2:
                same_point = edge1.p1
            else:
                same_point = edge1.p2
            angle_edge1 = angle2(p1, p2, edge1.get_adjacent(same_point))
            angle_edge2 = angle2(p1, p2, edge2.get_adjacent(same_point))
            if angle_edge1 < angle_edge2:
                return True
            return False

    def _index(self, p1, p2, edge):
        lo = 0
        hi = len(self._open_edges)
        while lo < hi:
            mid = (lo+hi)//2
            if self._less_than(p1, p2, edge, self._open_edges[mid]):
                hi = mid
            else:
                lo = mid + 1
        return lo

