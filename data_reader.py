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
        self.triangles = [Triangle(*[triang[i+j] for j in range(3)])
                for i in range(0,len(triang),3)]

        # Triangles where the edges are represented by point
        # ids instead of coordinates
        self.id_triangles = [triang[i:i+3] for i in range(0,len(triang),3)]

        self.point_id_dict = {Point(p[0], p[1]): i for i, p in enumerate(points)}
        self.triangle_id_dict = {t:i for i,t in enumerate(triang)}

        

    def size(self):
        return len(self.points)

    def triangle_to_id(self, triang: Triangle):

        if point in self.triangle_id_dict:
            return self.triangle_id_dict[point]
        else:
            return -1

    def point_to_id(self,point: Point):

        if point in self.point_id_dict:
            return self.point_id_dict[point]
        else:
            return -1

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
            if l>=0:
                return (i,l)
            else:
                return None



'''
The kirkpatrick point locator is very efficient
for larger polygons and can answer point
location queries in O(logn)
'''
class KirkpatrickPointLocator:

    def __init__(self, poly : PointLocatorPoly):
        self.poly = poly
        self.locator = Locator(poly.triangles,outline=Polygon(poly.points))


    def locate(self, point: Point):

        loc = self.locator.locate(point)


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
            else:
                return -1



rp = polygons[:1]


for i,p in enumerate(rp):


    flattened_point  = []

    for point in p:
        flattened_point.append(point[0])
        flattened_point.append(point[1])

    #flattened_point = list(reversed(flattened_point))

    flattened.append(flattened_point)

    trig = earcut(flattened_point)

    create_kirkpatrick(p, trig)
    #create_kirkpatrick(idxes,idxes2_out)

    t.append(trig)
    print(f"Finished {i}")

# with open('data.json', 'w') as outfile:
#     json.dump(flattened, outfile)

