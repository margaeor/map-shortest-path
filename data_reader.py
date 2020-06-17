import shapefile
import tripy
import json
import numpy as np
from geo.shapes import Point, Polygon, Triangle
from geo.spatial import triangulatePolygon
from geo.generator import randomConvexPolygon, randomConcaveTiling
from geo.drawer import plot, plotPoints, show, showPoints
from graph import DirectedGraph, UndirectedGraph
from kirkpatrick import Locator
import matplotlib.pyplot as plt
import constants
from collections import defaultdict,deque
from itertools import combinations

from triangulator import earcut


with shapefile.Reader("./GSHHS_c_L1.shp") as shp:
    shapes = shp.shapes()

polygons = [shape.points for shape in shapes]

t = []
flattened = []

ANIMATE = True



def runLocator(regions,outline,point_to_id):
    # Pre-process regions
    l = Locator(regions,outline=outline)

    if ANIMATE:
       show(regions)
       plot(l.boundary, style='g--')
       show(regions)


    n = 50
    # Ensure correctness
    for region in reversed(regions):
        # Test n random interior points per region
        for k in range(n):
            target = region.smartInteriorPoint()
            print(target)
            target_region = l.locate(target)

        # Animate one interior point
        if ANIMATE:
            plot(l.regions)
            plot(target_region, style='ro-')
            showPoints(target, style='bo')

        # Test n random exterior points per region
        for k in range(n):
            target = region.exteriorPoint()
            target_region, is_valid = l.annotatedLocate(target)


        # Animate one exterior point
        if ANIMATE and target_region:
            plot(l.regions)
            plot(target_region, style='ro--')
            showPoints(target, style='bx')


def create_kirkpatrick(point_dict,triangulation):

    converted_points = [Point(p[0],p[1]) for p in point_dict]
    point_to_id = {Point(p[0],p[1]):i for i,p in enumerate(point_dict)}
    triangulation = [Point(*point_dict[t]) for t in triangulation]

    triangles = [Triangle(*[triangulation[i+j] for j in range(3)])
                for i in range(0,len(triangulation),3)]

    plt.figure()

    x = []
    y = []

    for p in point_dict:

        x.append(p[0])
        y.append(p[1])

    x.append(point_dict[0][0])
    y.append(point_dict[0][1])
    x = np.array(x)
    y = np.array(y)
    plt.plot(x, y)

    lst = []

    for t in triangles:

        x = [t.points[0].x,t.points[1].x,t.points[2].x,t.points[0].x]
        y = [t.points[0].y, t.points[1].y, t.points[2].y,t.points[0].y]

        lst.append([[t.points[0].x,t.points[0].y],[t.points[1].x,t.points[1].y],[t.points[2].x,t.points[2].y]])
        #plt.plot(x, y)

    outline = Polygon(converted_points)
    #plt.show()
    runLocator(triangles,outline,point_to_id)


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

    # def id_to_point(self,id):
    #
    #     if  id>=0 and id<len(self.points):
    #         return self.points[id]
    #     else:
    #         return -1



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

    def click_event(self,event):

        print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              (event.button, event.x, event.y, event.xdata, event.ydata))

        p = Point(event.xdata,event.ydata)
        l = self.locate(p)
        print(l)
        plt.plot(event.xdata, event.ydata,markerfacecolor="red", marker=".", markersize=20)
        self.fig.canvas.draw()

    def start_gui(self):

        self.fig = plt.figure()
        plot(self.polygons)

        #show(self.polygons[0].triangles)

        cid = self.fig.canvas.mpl_connect('button_press_event', self.click_event)
        plt.show()



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



rp = polygons

point_locator = PointLocator()

for i,p in enumerate(rp):

    point_locator.add_polygon(PointLocatorPoly(p))



    # flattened_point  = []
    #
    # for point in p:
    #     flattened_point.append(point[0])
    #     flattened_point.append(point[1])
    #
    # #flattened_point = list(reversed(flattened_point))
    #
    # flattened.append(flattened_point)
    #
    # trig = earcut(flattened_point)
    #
    # create_kirkpatrick(p, trig)
    # #create_kirkpatrick(idxes,idxes2_out)
    #
    # t.append(trig)
    # print(f"Finished {i}")



point_locator.start_gui()


# with open('data.json', 'w') as outfile:
#     json.dump(flattened, outfile)

