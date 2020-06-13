import shapefile
import tripy
import json

from geo.shapes import Point, Polygon, Triangle
from geo.spatial import triangulatePolygon
from geo.generator import randomConvexPolygon, randomConcaveTiling
from geo.drawer import plot, plotPoints, show, showPoints
from graph import DirectedGraph, UndirectedGraph
from kirkpatrick import Locator


from Naked.toolshed.shell import execute_js, muterun_js

from polytri import triangulate
from triangulator import earcut


with shapefile.Reader("./GSHHS_c_L1.shp") as shp:
    shapes = shp.shapes()

polygons = [shape.points for shape in shapes]


t = []
flattened = []

ANIMATE = True

rp = polygons[:1]#reversed(polygons)


def runLocator(regions):
    # Pre-process regions
    l = Locator(regions)

    if ANIMATE:
        show(regions)
        plot(l.boundary, style='g--')
        show(regions)


    n = 50
    # Ensure correctness
    for region in regions:
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

    triangulation = [Point(*point_dict[t]) for t in triangulation]

    trianges = [Triangle(*[triangulation[i+j] for j in range(3)])
                for i in range(len(triangulation)//3)]

    runLocator(trianges)




for i,p in enumerate(rp):


    flattened_point  = []

    for point in p:
        flattened_point.append(point[0])
        flattened_point.append(point[1])


    trig = earcut(flattened_point)


    create_kirkpatrick(p,trig)

    t.append(trig)
    print(f"Finished {i}")

#with open('data.json', 'w') as outfile:
#    json.dump(flattened, outfile)

print("HI")

