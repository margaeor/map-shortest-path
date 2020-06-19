
from collections import defaultdict, deque
from itertools import combinations

import constants
from geo.graph import UndirectedGraph
from geo.shapes import Point, Polygon, Triangle
from point_location.kirkpatrick import Locator
from triangulator import earcut


class DualGraph:

    def __init__(self, triangulation):
        self.g = UndirectedGraph()
        self.edges = defaultdict(list)
        self.triangulation = triangulation

        # Process every triangle of the triangulation
        for i,trig in enumerate(triangulation):

            self.g.add_node(i)

            # Process every edge of the triangle
            for subset in combinations(trig, 2):
                key = tuple(sorted(subset))

                if len(self.edges[key]) > 0:
                    # Connect triangle to neighbouring triangles
                    for j in self.edges[key]:
                        self.g.connect(i,j)

                self.edges[key].append(i)


    def __construct_path(self, pred, f):

        node = f
        path = []

        while True:

            if node not in pred:
                return []

            path.append(node)
            if pred[node] == None:
                return list(reversed(path))

            node = pred[node]

    def bfs(self, s, f):

        # Mark all the vertices as not visited
        visited = [False] * (len(self.triangulation))

        # Create a queue for BFS
        queue = deque([])

        # Mark the source node as
        # visited and enqueue it
        queue.append(s)
        visited[s] = True

        pred = {s: None}

        while queue:

            # Dequeue a vertex from
            # queue and print it
            s = queue.popleft()

            if s == f:
                return self.__construct_path(pred, s)

            # Get all adjacent vertices of the
            # dequeued vertex s. If a adjacent
            # has not been visited, then mark it
            # visited and enqueue it
            for i in self.g.e[s]:
                if visited[i] == False:
                    pred[i] = s
                    queue.append(i)
                    visited[i] = True


    def find_path_between_nodes(self,s,f):
        return self.bfs(s,f)


class PointLocatorPoly:

    '''
    `points` is a list of (x,y) tuples
    '''
    def __init__(self,points):

        self.points = [Point(p[0], p[1]) for p in points]

        flattened_points = []

        # Flatten points to pass them to triangulator
        for point in points:
            flattened_points.append(point[0])
            flattened_points.append(point[1])

        # Triangulate the polygon
        triang = earcut(flattened_points)

        # Create triangle object from triangles
        self.triangles = [Triangle(*[self.points[triang[i+j]] for j in range(3)])
                for i in range(0,len(triang),3)]

        # Triangles where the edges are represented by point
        # ids instead of coordinates
        self.id_triangles = [triang[i:i+3] for i in range(0,len(triang),3)]

        self.point_id_dict = {Point(p[0], p[1]): i for i, p in enumerate(points)}
        self.triangle_id_dict = {t:i for i,t in enumerate(self.triangles)}

        # Construct the dual graph
        self.dual_graph = DualGraph(self.id_triangles)


    def size(self):
        return len(self.points)

    def get_triangle_id(self, triang: Triangle):

        if triang in self.triangle_id_dict:
            return self.triangle_id_dict[triang]
        else:
            return None

    def get_point_id(self,point: Point):

        if point in self.point_id_dict:
            return self.point_id_dict[point]
        else:
            return None


    def get_triangle_edges(self,tid):
        return tuple(sorted(list(self.id_triangles[tid])))


class PointLocator:

    def __init__(self):

        # List of different polygons
        self.polygons = []

        # List of structures that will answer
        # point location queries (each search
        # structure corresponds to a single polygon)
        self.search_structures = []

    '''
    Adds a new polygon to the search structure.
    (The map contains multiple polygons).
    '''
    def add_polygon(self, poly : PointLocatorPoly):

        self.polygons.append(poly)

        if len(poly.triangles) > constants.LINEAR_SEARCH_MAX_TRIANGLES:
            # Use Kirkpatrick structure (O(nlogn) construction, O(logn) query)
            self.search_structures.append(KirkpatrickPointLocator(poly))
        else:
            # Use linear point locator (O(n) construction, O(n) query)
            self.search_structures.append(LinearPointLocator(poly))

    def locate(self, point: Point):

        for i,s in enumerate(self.search_structures):
            l = s.locate(point)
            if l is not None:
                return (i,l)

        return None


    # pid is the polygon id and
    # sid1 and sid2 are the triangle ids between
    # which we want to find a path
    def find_edge_path(self,pid,sid1,sid2):

        poly = self.polygons[pid]
        struct = self.search_structures[pid]

        triangle_path = poly.dual_graph.find_path_between_nodes(sid1,sid2)


        #plot(poly.triangles,'b-')

        for t in triangle_path:

            trig = poly.triangles[t]

            #plot(trig,'b')

        if not triangle_path or len(triangle_path) < 2:
            return []

        path_edges = []
        for a, b in zip(triangle_path[:-1], triangle_path[1:]):
            ea = poly.get_triangle_edges(a)
            eb = poly.get_triangle_edges(b)

            e = list(set(ea) & set(eb))
            # plt.plot([dg.P[e[0]][0],dg.P[e[1]][0]], [dg.P[e[0]][1],dg.P[e[1]][1]],'r-')
            path_edges.append(e)



        return path_edges

'''
The kirkpatrick point locator is very efficient
for larger polygons and can answer point
location queries in O(logn)
'''
class KirkpatrickPointLocator:

    def __init__(self, poly : PointLocatorPoly):
        self.poly = poly
        poly_shape = Polygon(poly.points)
        triangles = poly.triangles

        self.locator = Locator(triangles,outline=poly_shape)


    def locate(self, point: Point):

        loc = self.locator.locate(point)

        if loc:
            return self.poly.get_triangle_id(loc)
        else:
            return None


'''
The linear point locator checks every triangle
of the triangulation about whether it contains
our point. It is used for small polygons in case
we don't want to create a Kirkpatrick structure
for those.
Can answer point location queries in O(n)
'''
class LinearPointLocator:
    def __init__(self, poly : PointLocatorPoly):

        self.poly = poly

    def locate(self,point: Point):
        for i,t in enumerate(self.poly.triangles):
            if t.contains(point):
                return i
        return None
