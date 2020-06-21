
from collections import defaultdict, deque
from itertools import combinations
from multiprocessing import Pool as ThreadPool

from kirkpatrick.geo.drawer import plot
from kirkpatrick.geo.shapes import Point, Polygon, Triangle
from tqdm import tqdm

import constants
from kirkpatrick.geo.graph import UndirectedGraph
from kirkpatrick.kirkpatrick import Locator
from triangulation.earcut import earcut

'''
Creates a point location search structure
for a specific polygon
'''
def create_search_structure( poly):
    if len(poly.triangles) > constants.LINEAR_SEARCH_MAX_TRIANGLES:
        # Use Kirkpatrick structure (high construction complexity, O(logn) query)
        return KirkpatrickPointLocator(poly)
    else:
        # Use linear point locator (O(n) construction, O(n) query)
        return LinearPointLocator(poly)


# class ParallelPointLocator:
#
#     def __call__(self, *args, **kwargs):
#
#         return args[0].locate(args[1])

def parallel_locate(search_structure,point):
    return search_structure.locate(point)


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

        # Flatten points to pass them to triangulation
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

    def __init__(self, visualize_triang_path=False):

        # List of different polygons
        self.polygons = []

        # Parameter of whether we want to visualize
        # the triangles that the pathfinder passes from
        self.visualize_triang_path = visualize_triang_path

        # List of structures that will answer
        # point location queries (each search
        # structure corresponds to a single polygon)
        self.search_structures = []

    '''
    Adds a list of Polygons to the point locator
    '''
    def add_polygons(self, polygons):
        polygons = [PointLocatorPoly(p) for p in polygons]
        self.polygons = polygons
        num_polygons = len(polygons)

        with ThreadPool(constants.NUM_THREADS) as p:
            self.search_structures = list(tqdm(p.imap(create_search_structure, self.polygons),total=num_polygons))


    '''
    Finds the polygon id and the triangle where the
    point is located.
    Returns a tuple (polygon_id,triangle_id) if the point
    is found inside some polygon or None otherwise
    '''
    def locate(self, point: Point):

        # THREADS = constants.NUM_THREADS
        #
        # CHUNK_SIZE = 1000
        #
        # with ThreadPool(THREADS) as p:
        #     for i in range(0,len(self.search_structures),CHUNK_SIZE):
        #         args = [(s,point) for s in self.search_structures[i:i+CHUNK_SIZE]]
        #         partial_res = p.starmap(parallel_locate,args)
        #
        #         for j,l in enumerate(partial_res):
        #             if l is not None:
        #                 return (i+j, l)


        for i,s in enumerate(self.search_structures):
            l = s.locate(point)
            if l is not None:
                return (i,l)

        return None



    '''
    `pid` is the polygon id and `sid1` and `sid2` are the ids
    of the triangles of the polygon between which we want
    to find a path.
    '''
    def find_edge_path(self,pid,sid1,sid2):

        poly = self.polygons[pid]

        triangle_path = poly.dual_graph.find_path_between_nodes(sid1,sid2)


        for t in triangle_path:

            trig = poly.triangles[t]

            if self.visualize_triang_path:
                plot(trig,'b')

        if not triangle_path or len(triangle_path) < 2:
            return []

        path_edges = []
        for a, b in zip(triangle_path[:-1], triangle_path[1:]):
            ea = poly.get_triangle_edges(a)
            eb = poly.get_triangle_edges(b)

            e = list(set(ea) & set(eb))
            path_edges.append(e)


        return path_edges

'''
The kirkpatrick point locator is very efficient
for larger polygons and can answer point
location queries in O(logn). 
However, it is time-consuming to build
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
