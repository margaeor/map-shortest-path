import matplotlib.pyplot as plt
import shapefile
import time
import constants
import sys
from geo.drawer import plot, plotPoints, show, showPoints
from geo.shapes import Point, Polygon, Triangle
from point_location.kirkpatrick import Locator
from point_location.point_locator import PointLocator, PointLocatorPoly
from tqdm import tqdm
from pathfinder.pathfinder import PathFinder


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

    def __init__(self, shape_file="./data/h/GSHHS_h_L1.shp"):

        self.point_locator = PointLocator(constants.VISUALIZE_TRIANGLES)
        self.path_finder = PathFinder()

        # Contain (polygon_id,triangle_id) of the starting
        # and finishing points
        self.s,self.f = None,None

        # Contain the actual starting and finishing point
        self.ps,self.pf = None,None


        with shapefile.Reader(shape_file) as shp:
            shapes = sorted(shp.shapes(),key=lambda x:-len(x.points))

        num_points = sum([len(poly.points) for poly in shapes])

        self.polygons = [shape.points for shape in reversed(shapes[:constants.MAX_POLYGONS])]

        print(f"Number of polygons in file: {len(shapes)}")
        print(f"Number of points in file: {num_points}")
        print(f"Points of largest polygon: {len(self.polygons[-1])}")
        print("Preprocessing map")

        tic = time.perf_counter()
        self.point_locator.add_polygons(self.polygons)
        toc = time.perf_counter()
        print(f"Preprocessing took {toc - tic:0.4f} seconds")

    def click_event(self,event):


        p = Point(event.xdata,event.ydata)
        tic = time.perf_counter()
        l = self.point_locator.locate(p)
        toc = time.perf_counter()
        print(f"Point location took {toc - tic:0.4f} seconds")

        if l is None:
            print('Point not inside any polygon. Pick another one')
            return
        else:
            #self.ps,self.pf = Point(34.45,28.32),Point(35.74,28.9); self.s,self.f = self.point_locator.locate(self.ps),self.point_locator.locate(self.pf)
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
                print(f'Calculating path between {self.ps} and {self.pf}:')
                edge_path = self.point_locator.find_edge_path(self.s[0],self.s[1],self.f[1])

                poly_points = self.point_locator.polygons[self.s[0]].points
                path = self.path_finder.find_path_funnel(poly_points,edge_path,self.ps,self.pf)
                plotPoints(path,'r--')
                self.s,self.f = None,None
                self.ps, self.pf = None, None

        plt.plot(event.xdata, event.ydata,markerfacecolor="red", marker=".", markersize=20)
        self.fig.canvas.draw()


    def show_map(self):

        self.fig = plt.figure()
        print("Rendering matplotlib GUI...")
        polys_to_plot = self.point_locator.polygons
        plot(polys_to_plot)

        ce = ClickEvent(self.fig, self.click_event, button=1)

        self.fig.canvas.mpl_connect('button_press_event', ce.onpress)
        self.fig.canvas.mpl_connect('button_release_event', ce.onrelease)
        self.fig.canvas.mpl_connect('motion_notify_event', ce.onmove)

        print("GUI successfully rendered!")
        print("Click 2 points on the map to find a path between them")

        #cid = self.fig.canvas.mpl_connect('button_press_event', self.click_event)
        plt.show()




#driver = ProgramDriver("./data/GSHHS_h_L1.shp")
#driver.show_map()



if __name__ == '__main__':

    choices = ['c','l','i','h']
    files = [str("GSHHS_"+c+"_L1.shp") for i,c in enumerate(choices)]

    while True:
        print("Choose map shapefile:")
        print("1) File (c) with 802 polygons, 7721 points")
        print("2) File (l) with 5812 polygons, 57912 points")
        print("3) File (i) with 33447 polygons, 347247 points")
        print("4) File (h) with 145483 polygons, 1643797 points")


        choice = input("Please make a choice: ")

        try:
            choice = int(choice)

            if choice >=1 and choice <=5:
                driver = ProgramDriver("./data/"+files[choice-1])
                driver.show_map()

        except ValueError as e:
            print("Wrong input")
