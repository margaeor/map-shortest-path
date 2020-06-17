import matplotlib.pyplot as plt
import numpy as np
import shapefile

from geo.drawer import plot, show, showPoints
from geo.shapes import Point, Polygon, Triangle
from point_location.kirkpatrick import Locator
from point_location.point_locator import PointLocator, PointLocatorPoly




class ProgramDriver:

    def __init__(self, shape_file="./GSHHS_c_L1.shp"):

        self.point_locator = PointLocator()

        with shapefile.Reader(shape_file) as shp:
            shapes = shp.shapes()

        self.polygons = [shape.points for shape in shapes]


        for i,p in enumerate(self.polygons):

            self.point_locator.add_polygon(PointLocatorPoly(p))


    def click_event(self,event):

        print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              (event.button, event.x, event.y, event.xdata, event.ydata))

        p = Point(event.xdata,event.ydata)
        l = self.point_locator.locate(p)
        print(l)
        plt.plot(event.xdata, event.ydata,markerfacecolor="red", marker=".", markersize=20)
        self.fig.canvas.draw()


    def show_map(self):

        self.fig = plt.figure()
        plot(self.point_locator.polygons)

        cid = self.fig.canvas.mpl_connect('button_press_event', self.click_event)
        plt.show()


driver = ProgramDriver()
driver.show_map()


