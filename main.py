import numpy as np
#import matplotlib
from  matplotlib import tri as mtri
import matplotlib.pyplot as plt
from collections import defaultdict
from functools import lru_cache
import itertools
from collections import deque

np.random.seed(3)

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
    def __init__(self,points,mask=None):
        self.adj = defaultdict(set)
        self.P = points
        self.mtrig = mtri.Triangulation(points[:,0], points[:,1])
        self.trigs = self.mtrig.triangles[~mask.astype(bool),:] if mask is not None else self.mtrig.triangles
        print('len',len(self.trigs))
        self.edges = defaultdict(list)

        for i, trig in enumerate(self.trigs):
            for subset in itertools.combinations(trig, 2):
                self.edges[tuple(sorted(subset))].append(i)

        for key, value in self.edges.items():
            value = list(value)
            for i in range(len(value)):

                for j in range(i + 1, len(value)):
                    self.add_edge(value[i], value[j])

    def get_trig_edges(self, trig_id):
        l = []
        for subset in itertools.combinations(self.trigs[trig_id], 2):
            l.append(tuple(sorted(subset)))

        return l

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

    def construct_path(self, pred, f):

        node = f
        path = []

        while True:

            if node not in pred:
                print("ERROR")
                return []

            path.append(node)
            if pred[node] == None:
                return list(reversed(path))

            node = pred[node]


    def bfs(self,s,q):

        # Mark all the vertices as not visited
        visited = [False] * (len(self.adj))

        # Create a queue for BFS
        queue = deque([])

        # Mark the source node as
        # visited and enqueue it
        queue.append(s)
        visited[s] = True

        pred = {s:None}

        while queue:

            # Dequeue a vertex from
            # queue and print it
            s = queue.popleft()

            if self.is_inside_triangle(q, s):
                print("FOUND ENDING ", s)
                return self.construct_path(pred, s)

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

class PathFinder:

    def __init__(self,dg):
        self.dg = dg

    def convert_trig_path_to_edges(self, path):

        if not path or len(path)<2:
            return []

        path_edges = []
        for a,b in zip(path[:-1],path[1:]):

            ea = dg.get_trig_edges(a)
            eb = dg.get_trig_edges(b)

            e = list(set(ea) & set(eb))[0]
            #plt.plot([dg.P[e[0]][0],dg.P[e[1]][0]], [dg.P[e[0]][1],dg.P[e[1]][1]],'r-')
            path_edges.append(e)

        return path_edges


    def ccw(self,a,b,c):
        return np.cross(b-a,c-a) > 0
        #return

    def find_triangle_path(self,p,q):
        s = dg.find_triangle_from_point(p)
        print('STARTING ID', s)
        if s:
            path = dg.bfs(s, q)
            print(path)
            edge_path = self.convert_trig_path_to_edges(path)

            tail = [np.array(p)]
            left = []
            right = []

            last_edge_l = None
            last_edge_r = None
            print(edge_path)
            for e in edge_path:
                p1,p2 = dg.P[e[0]],dg.P[e[1]]
                p1_id,p2_id = e[0],e[1]

                prev_center = tail[-1] if last_edge_l is None or last_edge_r is None else (last_edge_r+last_edge_l)/2
                #print('Prev center:',prev_center)
                if self.ccw(prev_center,p1,p2):
                    p1,p2 = p2,p1
                    p1_id,p2_id = p2_id,p1_id


                if len(left) == 0:
                    left.append(p1_id)
                elif left[-1] != p1_id and self.ccw(tail[-1], p1, dg.P[left[-1]]):
                    if self.ccw(tail[-1],dg.P[right[-1]], p1):
                        print("OK situation left",p1)
                        left[-1] = p1_id
                    else:
                        print("Weird situation left")
                        # change the appex
                        left[-1] = p1_id
                        tail.append(dg.P[right.pop()])
                else:
                    print("Not preceeding left",p1)

                if len(right) == 0:
                    right.append(p2_id)
                elif right[-1] != p2_id and self.ccw(tail[-1], dg.P[right[-1]], p2):
                    if self.ccw(tail[-1], p2, dg.P[left[-1]]):
                        print("OK situation right",p2)
                        right[-1] = p2_id
                    else:
                        print("Weird situation right")
                        # change the appex
                        right[-1] = p2_id
                        #left[-1] = p1_id
                        tail.append(dg.P[left.pop()])
                else:
                    print("Not preceeding right",p2)

                #print('(l1,r1,a)=', dg.P[left[-1]],dg.P[right[-1]],tail[-1])
                last_edge_l = p1
                last_edge_r = p2

            tail.append(q)
            return np.array(tail)


#coords = np.array([[0,0],[0,1],[1,0],[1,1],[2,0],[2,1]])
#coords = np.random.rand(10,2)
coords = np.array(
[[8.30000000000001, -3.78000000000000],
 [7.14000000000001, -7.70000000000001],
 [13.7600000000000, -5.64000000000001],
 [11.3800000000000, -10.7600000000000],
 [16.6000000000000, -9.98000000000001],
 [21.2600000000000, -7.84000000000001],
 [21.7400000000000, -3.66000000000000],
 [15.4400000000000, -1.22000000000000],
 [16.8200000000000, 2.02000000000000],
 [21.5800000000000, 0.880000000000001],
 [11.0000000000000, 3.00000000000000],
 [9.30000000000001, 0.280000000000000],
 [7.36615871821730, 5.55833384277120],
 [11.7558194162222, 8.74204379956599],
 [10.0000000000000, 12.0000000000000],
 [17.4479069147342, 13.4211326754614],
 [18.9915238634832, 8.23554448825773],
 [23.9841599320932, 11.6363255784704]]
)
mask = 1-np.array([1,1,0,0,1,1,0,0,1,0,1,1,1,1,1,0,0,1,1,1,1,1,1,0,0,0])

dg = DualGraph(coords,mask)
pf = PathFinder(dg)


print("Calculating")
#p = (0.33, 0.33)
#q = (0.55, 0.55)
p = (8.7,-5.7)
q = (20,11)
#p = (20,-6)
#q = (20,11)



x = coords[:,0]
y = coords[:,1]



triang = mtri.Triangulation(x, y, mask=mask)

Cpoints = x + 0.5*y

xmid = x[triang.triangles].mean(axis=1)
ymid = y[triang.triangles].mean(axis=1)
Cfaces = 0.5*xmid + ymid#0.66*np.ones(shape=(triang.triangles.shape[0]))#

print(len(triang.triangles))

plt.tripcolor(triang, facecolors=Cfaces, edgecolors='k')
#plt.plot([p[0],q[0]],[p[1],q[1]],'ro')
plt.title('facecolors')


points = pf.find_triangle_path(p,q)

if points is not None:
    plt.plot(points[:,0],points[:,1],'r--')
    plt.plot(points[:,0],points[:,1],'ro')

for i in range(len(dg.trigs)):
    t = np.array(dg.triangle_id_to_coords(i))
    c = np.sum(t,axis=(1))/3
    plt.text(c[0],c[1],i)

#print(coords)
#print(dg.trigs)
#print(dict(dg.adj))
print(pf.ccw(np.array([0,0]),np.array([1,1]),np.array([1,0])))




plt.show()