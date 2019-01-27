from heapq import heapify, heappush, heappop
from visgraph.visible_vertices import edge_distance


def dijkstra(graph, origin, destination):
    D = {}
    P = {}
    Q = priority_dict()
    Q[origin] = 0

    for v in Q:
        D[v] = Q[v]
        if v == destination: break
        edges = graph[v]

        for e in edges:
            w = e.get_adjacent(v)
            elength = D[v] + edge_distance(v, w)
            if w in D:
                if elength < D[w]:
                    raise ValueError
            elif w not in Q or elength < Q[w]:
                Q[w] = elength
                P[w] = v
    return (D, P)


def shortest_path(graph, origin, destination):
    D, P = dijkstra(graph, origin, destination)
    path = []
    while 1:
        path.append(destination)
        if destination == origin: break
        destination = P[destination]
    path.reverse()
    return path


class priority_dict(dict):

    def __init__(self, *args, **kwargs):
        super(priority_dict, self).__init__(*args, **kwargs)
        self._rebuild_heap()

    def _rebuild_heap(self):
        self._heap = [(v, k) for k, v in iteritems(self)]
        heapify(self._heap)

    def smallest(self):
        heap = self._heap
        v, k = heap[0]
        while k not in self or self[k] != v:
            heappop(heap)
            v, k = heap[0]
        return k

    def pop_smallest(self):
        heap = self._heap
        v, k = heappop(heap)
        while k not in self or self[k] != v:
            v, k = heappop(heap)
        del self[k]
        return k

    def __setitem__(self, key, val):
        super(priority_dict, self).__setitem__(key, val)

        if len(self._heap) < 2 * len(self):
            heappush(self._heap, (val, key))
        else:
            self._rebuild_heap()

    def setdefault(self, key, val):
        if key not in self:
            self[key] = val
            return val
        return self[key]

    def update(self, *args, **kwargs):
        super(priority_dict, self).update(*args, **kwargs)
        self._rebuild_heap()

    def __iter__(self):
        def iterfn():
            while len(self) > 0:
                x = self.smallest()
                yield x
                del self[x]
        return iterfn()
