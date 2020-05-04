import numpy as np
#import matplotlib
from  matplotlib import tri as mtri
import matplotlib.pyplot as plt
from collections import defaultdict
from functools import lru_cache

TOLERANCE = 0.0001


def area(x1, y1, x2, y2, x3, y3):
    return abs((x1 * (y2 - y3) + x2 * (y3 - y1)
                + x3 * (y1 - y2)) / 2.0)


def is_inside(x1, y1, x2, y2, x3, y3, x, y):
    # Calculate area of triangle ABC
    A = area(x1, y1, x2, y2, x3, y3)

    # Calculate area of triangle PBC
    A1 = area(x, y, x2, y2, x3, y3)

    # Calculate area of triangle PAC
    A2 = area(x1, y1, x, y, x3, y3)

    # Calculate area of triangle PAB
    A3 = area(x1, y1, x2, y2, x, y)

    # Check if sum of A1, A2 and A3
    # is same as A
    if (abs(A1 + A2 + A3 - A) <= TOLERANCE):
        return True
    else:
        return False


def ray_tracing_numpy(x,y,poly):
    n = len(poly)
    inside = np.zeros(len(x),np.bool_)
    p2x = 0.0
    p2y = 0.0
    xints = 0.0
    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        idx = np.nonzero((y > min(p1y,p2y)) & (y <= max(p1y,p2y)) & (x <= max(p1x,p2x)))[0]
        if p1y != p2y:
            xints = (y[idx]-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
        if p1x == p2x:
            inside[idx] = ~inside[idx]
        else:
            idxx = idx[x[idx] <= xints]
            inside[idxx] = ~inside[idxx]

        p1x,p1y = p2x,p2y
    return inside

# Solve the system p = p0 + (p1 - p0) * s + (p2 - p0) * t
# to calculate barycentric coordinates

def is_inside3(p0,p1,p2,p):

    A = np.concatenate((p1-p0,p2-p0),axis=1)
    b = p-p0
    x = np.linalg.solve(A, b)

    return x[0][0]>=0 and x[1][0]>=0 and x[0][0]+x[1][0]<=1

def is_inside2(x1, y1, x2, y2, x3, y3, x, y):

    #r = ray_tracing_numpy(np.array([x]),np.array([y]),[[x1,y1],[x2,y2],[x3,y3]])
    r = is_inside3(np.array([x1,y1]),np.array([x2,y2]),np.array([x3,y3]),np.array([x,y]))
    return r


class DualGraph:
    def __init__(self,points):
        self.adj = defaultdict(set)
        self.P = points
        self.mtrig = mtri.Triangulation(points[:,0], points[:,1])
        self.trigs = self.mtrig.triangles

        d = defaultdict(set)

        for i, trig in enumerate(self.trigs):
            for t1 in trig:
                d[t1].add(i)

        for key, value in d.items():
            value = list(value)
            for i in range(len(value)):
                for j in range(i + 1, len(value)):
                    self.add_edge(value[i], value[j])

    @lru_cache(maxsize=None)
    def triangle_id_to_coords(self, triangle_id):

        return np.array([self.P[t] for t in self.trigs[triangle_id]]).T

    def is_inside_triangle(self, p, triangle_id):


        T = self.triangle_id_to_coords(triangle_id)

        p0,p1,p2 = T[:,[0]],T[:,[1]],T[:,[2]]

        p = np.array([p]).T

        A = np.concatenate((p1 - p0, p2 - p0), axis=1)
        b = p - p0
        x = np.linalg.solve(A, b)

        return x[0][0] >= 0 and x[1][0] >= 0 and x[0][0] + x[1][0] <= 1

        #return ray_tracing_numpy(np.array([p[0]]),np.array([p[1]]),T.T)[0]

    def dfs(self,visited,s,q):

        if self.is_inside_triangle(q,s):
            print("FOUND POINT ",s)
            return
        if s not in visited:
            visited.add(s)
            for neighbour in self.adj[s]:
                self.dfs(visited, neighbour,q)

    def print_path(self,pred,f):

        if f not in pred:
            print("ERROR")
            return

        print(f)
        if pred[f] == None:
            print('This was the start')
            return

        print(self.print_path(pred,pred[f]))

    def bfs(self,visited,s,q):

        # Mark all the vertices as not visited
        visited = [False] * (len(self.adj))

        # Create a queue for BFS
        queue = []

        # Mark the source node as
        # visited and enqueue it
        queue.append(s)
        visited[s] = True

        pred = {s:None}

        while queue:

            # Dequeue a vertex from
            # queue and print it
            s = queue.pop(0)

            if self.is_inside_triangle(q, s):
                print("FOUND POINT ", s)
                print(pred)
                self.print_path(pred,s)
                return

            # Get all adjacent vertices of the
            # dequeued vertex s. If a adjacent
            # has not been visited, then mark it
            # visited and enqueue it
            for i in self.adj[s]:
                if visited[i] == False:
                    pred[i] = s
                    queue.append(i)
                    visited[i] = True

    def find_triangle_from_point(self, p):

        for i in range(len(self.trigs)):
            if self.is_inside_triangle(p,i):
                return i

    def add_edge(self,a,b):
        self.adj[a].add(b)
        self.adj[b].add(a)

#coords = np.array([[0,0],[0,1],[1,0],[1,1],[2,0],[2,1]])
coords = np.random.rand(10,2)

dg = DualGraph(coords)



print("Calculating")
p = (0.33, 0.33)
q = (0.55, 0.55)
s = dg.find_triangle_from_point(p)
print('STARTING ID',s)

visited =  set()
print(dg.bfs(visited,s,q))




x = coords[:,0]
y = coords[:,1]

triang = mtri.Triangulation(x, y)

Cpoints = x + 0.5*y

xmid = x[triang.triangles].mean(axis=1)
ymid = y[triang.triangles].mean(axis=1)
Cfaces = 0.5*xmid + ymid#0.66*np.ones(shape=(triang.triangles.shape[0]))#



plt.tripcolor(triang, facecolors=Cfaces, edgecolors='k')
plt.title('facecolors')




for i in range(len(dg.trigs)):
    t = np.array(dg.triangle_id_to_coords(i))
    c = np.sum(t,axis=(1))/3
    plt.text(c[0],c[1],i)

#print(coords)
#print(dg.trigs)
#print(dict(dg.adj))





plt.show()