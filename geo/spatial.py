import numpy as np
import scipy.spatial as sp
from triangulator import earcut
from  matplotlib import tri as mtri
from copy import deepcopy
#from p2t import CDT


from . import shapes as shapes


def toNumpy(points):
    return np.array(list(map(lambda p: p.np(), points)), np.float32)


def triangulatePolygon(poly, hole=None):

    x = np.array([0] * poly.n, np.float32)
    y = np.array([0] * poly.n, np.float32)

    points = []
    point_list = poly.points
    for i,p in enumerate(poly.points):
        x[i] = p.x
        y[i] = p.y
        points.append(p.x)
        points.append(p.y)

    hole_param = None

    if hole:
        point_list = point_list+hole
        hole_param = [len(points)//2]
        for p in hole:
            points.append(p.x)
            points.append(p.y)

        #print("SHIT")
    # Triangulate poly with hole
    #triangles = mtri.Triangulation(x,y)
    triangles = earcut(points,hole_param,2)

    # cdt = CDT(poly.points)
    # if hole:
    #     cdt.add_hole(hole)
    #triangles = cdt.triangulate()

    # Frustratingly, CDT sometimes returns points that are not
    # EXACTLY the same as the input points, so we use a KDTree
    valid_points = [shapes.Point(p.x, p.y) for p in poly.points]
    #if hole:
    #    valid_points += [shapes.Point(p.x, p.y) for p in hole]
    tree = sp.KDTree(toNumpy(valid_points))

    # def convert(t):
    #     def findClosest(point):
    #         idx = tree.query(toNumpy([point]))[1]
    #         return valid_points[idx]
    #     A = findClosest(shapes.Point(t.a.x, t.a.y))
    #     B = findClosest(shapes.Point(t.b.x, t.b.y))
    #     C = findClosest(shapes.Point(t.c.x, t.c.y))
    #     return shapes.Triangle(A, B, C)


    # trig_list = []
    #
    # for i in range(triangles.triangles.shape[0]):
    #     trig = triangles.triangles[i]
    #     tri_points = [poly.points[j] for j in trig]
    #     trig_list.append(shapes.Triangle(*tri_points))


    triangulation = [point_list[t] for t in triangles]

    triangles = [shapes.Triangle(*[triangulation[i+j] for j in range(3)])
                for i in range(0,len(triangulation),3)]

    return triangles


def triangulatePoints(points):
    points = toNumpy(points)
    triangulation = sp.Delaunay(points)
    triangles = []
    for i in range(len(triangulation.simplices)):
        verts = list(map(lambda p: shapes.Point(p[0], p[1]),
                    points[triangulation.simplices[i, :]]))
        triangle = shapes.Triangle(
            verts[0], verts[1], verts[2])
        triangles.append(triangle)
    return triangles


def convexHull(points):
    points = toNumpy(points)
    verts = sp.ConvexHull(points).vertices
    hull = list(map(lambda idx: shapes.Point(points[idx, 0], points[idx, 1]), verts))
    return shapes.Polygon(hull)
