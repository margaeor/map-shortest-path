import matplotlib.pyplot as plt
import numpy as np
import shapefile

from geo.drawer import plot, show, showPoints
from geo.shapes import Point, Polygon, Triangle
from point_location.kirkpatrick import Locator
from point_location.point_locator import PointLocator, PointLocatorPoly



# class PathFinder:
#     def __init__(self, dg):
#         self.dg = dg
#
#     def convert_trig_path_to_edges(self, path):
#
#         if not path or len(path) < 2:
#             return []
#
#         path_edges = []
#         for a, b in zip(path[:-1], path[1:]):
#             ea = dg.get_trig_edges(a)
#             eb = dg.get_trig_edges(b)
#
#             e = list(set(ea) & set(eb))[0]
#             # plt.plot([dg.P[e[0]][0],dg.P[e[1]][0]], [dg.P[e[0]][1],dg.P[e[1]][1]],'r-')
#             path_edges.append(e)
#
#         return path_edges
#
#     def ccw(self, a, b, c):
#         return np.cross(b - a, c - a) > 0
#         # return
#
#     def find_triangle_path(self, p, q):
#         s = dg.find_triangle_from_point(p)
#         print('STARTING ID', s)
#         if s:
#             path = dg.bfs(s, q)
#             print(path)
#             edge_path = self.convert_trig_path_to_edges(path)
#
#             tail = [np.array(p)]
#             left = []
#             right = []
#
#             last_edge_l = None
#             last_edge_r = None
#             print(edge_path)
#             for e in edge_path:
#                 p1, p2 = dg.P[e[0]], dg.P[e[1]]
#                 p1_id, p2_id = e[0], e[1]
#
#                 prev_center = tail[-1] if last_edge_l is None or last_edge_r is None else (
#                                                                                           last_edge_r + last_edge_l) / 2
#                 # print('Prev center:',prev_center)
#                 if self.ccw(prev_center, p1, p2):
#                     p1, p2 = p2, p1
#                     p1_id, p2_id = p2_id, p1_id
#
#                 if len(left) == 0:
#                     left.append(p1_id)
#                 elif left[-1] != p1_id and self.ccw(tail[-1], p1, dg.P[left[-1]]):
#                     if self.ccw(tail[-1], dg.P[right[-1]], p1):
#                         print("OK situation left", p1)
#                         left[-1] = p1_id
#                     else:
#                         print("Weird situation left")
#                         # change the appex
#                         left[-1] = p1_id
#                         tail.append(dg.P[right.pop()])
#                 else:
#                     print("Not preceeding left", p1)
#
#                 if len(right) == 0:
#                     right.append(p2_id)
#                 elif right[-1] != p2_id and self.ccw(tail[-1], dg.P[right[-1]], p2):
#                     if self.ccw(tail[-1], p2, dg.P[left[-1]]):
#                         print("OK situation right", p2)
#                         right[-1] = p2_id
#                     else:
#                         print("Weird situation right")
#                         # change the appex
#                         right[-1] = p2_id
#                         # left[-1] = p1_id
#                         tail.append(dg.P[left.pop()])
#                 else:
#                     print("Not preceeding right", p2)
#
#                 # print('(l1,r1,a)=', dg.P[left[-1]],dg.P[right[-1]],tail[-1])
#                 last_edge_l = p1
#                 last_edge_r = p2
#
#             tail.append(q)
#             return np.array(tail)



class ProgramDriver:

    def __init__(self, shape_file="./GSHHS_c_L1.shp"):

        self.point_locator = PointLocator()

        # Starting and finishing points
        self.s,self.f = None,None

        with shapefile.Reader(shape_file) as shp:
            shapes = shp.shapes()

        self.polygons = [shape.points for shape in shapes]


        for i,p in enumerate(self.polygons):

            self.point_locator.add_polygon(PointLocatorPoly(p))



    def click_event(self,event):

        #print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #      (event.button, event.x, event.y, event.xdata, event.ydata))

        p = Point(event.xdata,event.ydata)
        l = self.point_locator.locate(p)

        if l is None:
            print('Point not inside any polygon. Pick another one')
            return
        else:
            if self.s is None:
                self.s = l
            elif self.f is None:
                if l[0] != self.s[0]:
                    print('Points not inside the same polygon. Pick another one')
                    return
                else:
                    self.f = l

            if self.s is not None and self.f is not None:
                print('Calculate path: ')
                self.point_locator.find_edge_path(self.s[0],self.s[1],self.f[1])
                self.s,self.f = None,None

        plt.plot(event.xdata, event.ydata,markerfacecolor="red", marker=".", markersize=20)
        self.fig.canvas.draw()


    def show_map(self):

        self.fig = plt.figure()
        plot(self.point_locator.polygons)

        cid = self.fig.canvas.mpl_connect('button_press_event', self.click_event)
        plt.show()


driver = ProgramDriver()
driver.show_map()


