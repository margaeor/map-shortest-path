import matplotlib.pyplot as plt
import numpy as np
import shapefile

from geo.drawer import plot, plotPoints, show, showPoints
from geo.shapes import Point, Polygon, Triangle
from point_location.kirkpatrick import Locator
from point_location.point_locator import PointLocator, PointLocatorPoly


def ccw(A, B, C):
    """Tests whether the line formed by A, B, and C is ccw"""
    return (B.x - A.x) * (C.y - A.y) < (B.y - A.y) * (C.x - A.x)

class PathFinder:
    def __init__(self):
        pass

    def find_path_funnel(self, point_dict , edge_path, p, q):

        tail = [p]
        left = []
        right = []

        last_edge_l = None
        last_edge_r = None

        #i = 0
        #edge_path = edge_path + [(q,q)]
        print(len(edge_path))
        for i,e in enumerate(edge_path):
            p1, p2 = point_dict[e[0]], point_dict[e[1]]
            #p1_id, p2_id = e[0], e[1]


            if p2 == last_edge_l or p1 == last_edge_r or (last_edge_r is None and last_edge_l is None and ccw(tail[-1], p2, p1)):
                p1, p2 = p2, p1
                #p1_id, p2_id = p2_id, p1_id

            # prev_center = tail[-1] if last_edge_l is None or last_edge_r is None else (
            #                                                                           last_edge_r + last_edge_l) / 2
            # # print('Prev center:',prev_center)
            # if ccw(prev_center, p1, p2):
            #     p1, p2 = p2, p1
            #     p1_id, p2_id = p2_id, p1_id

            # if p2 == last_edge_l:
            #     # Proceeding right
            #     if ccw(tail[-1], p2, point_dict[left[-1]]):
            #         print("OK situation right", p2)
            #         right[-1] = p2_id
            #     else:
            #         print("Weird situation right")
            #         # change the appex
            #         right[-1] = p2_id
            #
            #         # left[-1] = p1_id
            #         tail.append(point_dict[left.pop()])
            #         plt.plot(np.array([tail[-1].x, p2.x]), np.array([tail[-1].y, p2.y]), 'y')
            #
            # elif p2 == last_edge_r:
            #     if ccw(tail[-1], point_dict[right[-1]], p1):
            #         print("OK situation left", p1)
            #         left[-1] = p1_id
            #         plt.plot(np.array([tail[-1].x,p1.x]),np.array([tail[-1].y,p1.y]),'y')
            #     else:
            #         print("Weird situation left")
            #         # change the appex
            #         left[-1] = p1_id
            #         tail.append(point_dict[right.pop()])
            #
            # else:
            #     left.append(p1_id)
            #     right.append(p2_id)

            print(p1)
            print(p2)
            if len(left) == 0 and p1 != tail[-1]: #or (left[-1] == tail[-1]):
                # If appex is the same as previous left, then add the current point
                print("L:reset left")
                left = [p1]
            elif len(left) > 0 and left[-1] != p1:

                if not ccw(tail[-1], p1, left[-1]):

                    last_collision = -1
                    for i,p in enumerate(right):
                        if ccw(tail[-1], p, p1):
                            # Point of right segment is left of point of left segment(violation)
                            tail.append(right[i])
                            last_collision = i

                    if last_collision >= 0:
                        print("L:collision")
                        left = [p1]
                        right = right[last_collision + 1:]
                    else:
                        print("L:narrowing funnel")
                        left[-1] = p1
                else:
                    print("L: appending")
                    left.append(p1)
                # if ccw(tail[-1], right[-1], p1):
                #     print("OK situation left", p1)
                #     left[-1] = p1
                #     plt.plot(np.array([tail[-1].x,p1.x]),np.array([tail[-1].y,p1.y]),'b')
                # else:
                #     print("Weird situation left")
                #     # change the appex
                #     tail.append(right[-1])
                #
                #     left = [p1]

            if len(right) == 0 and p2 != tail[-1]:
                # If appex is the same as previous right, then add the current point
                right = [p2]
                print("R:reset right")
            elif len(right) > 0 and right[-1] != p2:

                if not ccw(tail[-1], right[-1], p2):

                    last_collision = -1
                    for i,p in enumerate(left):
                        if ccw(tail[-1], p2, p):
                            # Point of right segment is left of point of left segment(violation)
                            tail.append(left[i])
                            last_collision = i

                    if last_collision >= 0:
                        right = [p2]
                        left = left[last_collision + 1:]
                        print("R:collision")
                    else:
                        right[-1] = p2
                        print("R:narrowing funnel")
                else:
                    print("R: appending")
                    right.append(p2)

            # if i == 0:
            #     right.append(p2_id)
            # elif point_dict[right[-1]] == tail[-1]:
            #     # If appex is the same as previous right, then add the current point no matter what
            #     right.append(p2_id)
            # elif right[-1] != p2_id and ccw(tail[-1], point_dict[right[-1]], p2):
            #     if ccw(tail[-1], p2, point_dict[left[-1]]):
            #         print("OK situation right", p2)
            #         right[-1] = p2_id
            #     else:
            #         print("Weird situation right")
            #         # change the appex
            #
            #
            #         # left[-1] = p1_id
            #         tail.append(point_dict[left[-1]])
            #
            #         right = [tail[-1],p2_id]
            #
            #         plt.plot(np.array([tail[-1].x, p2.x]), np.array([tail[-1].y, p2.y]), 'y')
            # else:
            #     print("Not preceeding right", p2)


            # print('(l1,r1,a)=', dg.P[left[-1]],dg.P[right[-1]],tail[-1])
            last_edge_l = p1
            last_edge_r = p2

        # Fix last collisions
        for i, p in enumerate(right[:-1]):
            if ccw(tail[-1], p, q):
                tail.append(right[i])

        for i,p in enumerate(left[:-1]):
            if ccw(tail[-1], q, p):
                tail.append(left[i])
        tail.append(q)
        return tail

    def find_path_funnel2(self, point_dict , edge_path, p, q):

        tail = [p]
        left = []
        right = []

        last_edge_l = None
        last_edge_r = None

        i = 0

        print(len(edge_path))
        for e in edge_path:
            p1, p2 = point_dict[e[0]], point_dict[e[1]]
            p1_id, p2_id = e[0], e[1]

            prev_center = tail[-1] if last_edge_l is None or last_edge_r is None else (
                                                                                      last_edge_r + last_edge_l) / 2
            # print('Prev center:',prev_center)
            if ccw(prev_center, p1, p2):
                p1, p2 = p2, p1
                p1_id, p2_id = p2_id, p1_id

            if len(left) == 0:
                left.append(p1_id)
            elif left[-1] != p1_id and ccw(tail[-1], p1, point_dict[left[-1]]):
                if ccw(tail[-1], point_dict[right[-1]], p1):
                    print("OK situation left", p1)
                    left[-1] = p1_id
                    plt.plot(np.array([tail[-1].x,p1.x]),np.array([tail[-1].y,p1.y]),'b')
                else:
                    print("Weird situation left")
                    # change the appex
                    left[-1] = p1_id
                    tail.append(point_dict[right.pop()])
            else:
                print("Not preceeding left", p1)

            if len(right) == 0:
                right.append(p2_id)
            elif right[-1] != p2_id and ccw(tail[-1], point_dict[right[-1]], p2):
                if ccw(tail[-1], p2, point_dict[left[-1]]):
                    print("OK situation right", p2)
                    right[-1] = p2_id
                else:
                    print("Weird situation right")
                    # change the appex
                    right[-1] = p2_id

                    # left[-1] = p1_id
                    tail.append(point_dict[left.pop()])
                    plt.plot(np.array([tail[-1].x, p2.x]), np.array([tail[-1].y, p2.y]), 'y')
            else:
                print("Not preceeding right", p2)

            # print('(l1,r1,a)=', dg.P[left[-1]],dg.P[right[-1]],tail[-1])
            last_edge_l = p1
            last_edge_r = p2

        tail.append(q)
        return tail



class ClickEvent():
    def __init__(self, fig, func, button=1):
        self.fig = fig
        self.ax=fig.axes[0]
        self.func=func
        self.button=button
        self.press=False
        self.move = False


    def onclick(self,event):
        if event.inaxes == self.fig.axes[0]:
            if event.button == self.button:
                self.func(event)
    def onpress(self,event):
        self.press=True
    def onmove(self,event):
        if self.press:
            self.move=True
    def onrelease(self,event):
        if self.press and not self.move:
            self.onclick(event)
        self.press=False; self.move=False




class ProgramDriver:

    def __init__(self, shape_file="./GSHHS_c_L1.shp"):

        self.point_locator = PointLocator()
        self.path_finder = PathFinder()

        # Contain (polygon_id,triangle_id) of the starting
        # and finishing points
        self.s,self.f = None,None

        # Contain the actual starting and finishing point
        self.ps,self.pf = None,None


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
            #self.ps,self.pf = Point(-74.6,-10.7),Point(-70.7,-34.1); self.s,self.f = self.point_locator.locate(self.ps),self.point_locator.locate(self.pf)
            if self.s is None:
                self.s = l
                self.ps = p
            elif self.f is None:
                if l[0] != self.s[0]:
                    print('Points not inside the same polygon. Pick another one')
                    return
                else:
                    self.pf = p
                    self.f = l

            if self.s is not None and self.f is not None:
                print('Calculate path: ')
                edge_path = self.point_locator.find_edge_path(self.s[0],self.s[1],self.f[1])

                poly_points = self.point_locator.polygons[self.s[0]].points
                path = self.path_finder.find_path_funnel(poly_points,edge_path,self.ps,self.pf)
                print(path)
                plotPoints(path,'r--')
                self.s,self.f = None,None
                self.ps, self.pf = None, None

        plt.plot(event.xdata, event.ydata,markerfacecolor="red", marker=".", markersize=20)
        self.fig.canvas.draw()


    def show_map(self):

        self.fig = plt.figure()
        plot(self.point_locator.polygons)

        ce = ClickEvent(self.fig, self.click_event, button=1)

        self.fig.canvas.mpl_connect('button_press_event', ce.onpress)
        self.fig.canvas.mpl_connect('button_release_event', ce.onrelease)
        self.fig.canvas.mpl_connect('motion_notify_event', ce.onmove)

        #cid = self.fig.canvas.mpl_connect('button_press_event', self.click_event)
        plt.show()


driver = ProgramDriver()
driver.show_map()


