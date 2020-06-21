# Map Shortest Path Finding
This repository is a Computational Geometry Project, where the goal was, given 2 points in a map, to find the shortest
polyline that connects those points by implementing the 
Funnel Pathfinding algorithm.

The preprocessing steps conducted on the given Earth Map are the following:

1. Triangulate every polygon on the map and construct the dual graph of the triangulation.
2. Create a search structure for this polygon used for point location. The main search structure we use is the Kirkpatrick search structure which can answer point location queries in O(logn) time.
3. Draw a graphical representation of the map using matplotlib and register click events so that the user can click on the map on the desired points.

Then, when the user clicks on 2 points on the map, the process followed is:
1. Find the Polygon and the Triangles of this polygon where the given points are located.
2. Run a BFS on the dual graph to find the triangles that are part of the shortest path between our points.
3. Run the Funnel Algorithm to find the shortest polyline
   between our points given the triangle path.

# Running
In order to run the project, navigate to the root directory of the repo and install the requirements as:
```
pip3 install -r requirements.txt
```

Then, launch the file `main.py` as:
```
python3 main.py
```
After you choose a map to load, wait for preprocessing to finish and for the map to appear.
When the map appears, you can click at any points (not in the sea) to find the shortest polyline between them, as shown in the figure below.

![Program in Action](./figs/map.png?raw=true "Shortest Polyline")

# Configuration
You can adjust the project configuration by editing the file `constants.py`. There you can adjust the number of threads, the maximum number of polygons that are shown, turn on and off the triangle path visualization and determine the threshold above which we use Kirkpatrick point location instead of Exhaustive point location.

# Performance
To estimate the overall performance, I measured the time taken to perform preprocessing
and point location on the different data files.
The data files that were used come from the [GSHHS dataset]([GSHHS](http://www.earthmodels.org/data-and-tools/coastlines/gshhs)) and discribe earth shorelines using polygons. 
The size of the different files used is described in the table below:

| File | Total polygons | Total Points | Max polygon points |
|------|----------------|--------------|--------------------|
| (c)  | 802            | 7721         | 1000               |
| (l)  | 5812           | 57912        | 6730               |
| (i)  | 33447          | 347247       | 34329              |
| (h)  | 145483         | 1643797      | 139789             |

## Preprocessing
In the table below, we can see the approximate time taken for preprocessing of the different files for various thread pool sizes.
The results are shown in `seconds`.
| Threads | File (c) | File (l) | File (i) | File (h) |
|---------|----------|----------|----------|----------|
|    1    |   1.3 s  |   7.6 s  |   49 s   |   233 s  |
|    2    |  1.08 s  |   5.3 s  |   31 s   |   161 s  |
|    4    |   1.3 s  |   4.8 s  |   29 s   |   140 s  |
|    8    |   1.3 s  |   4.8 s  |   24 s   |   125 s  |

## Point Location
In the table below we can see the time taken for point
location of a single point in the different files:

| File (c)   | File (l)  | File (i)  | File (h) |
|------------|-----------|-----------|----------|
|   0.015 s  |   0.08 s  |   0.3 s   |   1 s    |

# Acknowledgements
Apart from the classic python libraries used (e.g. numpy,matplotlib, scipy...), I also used and modified the following repositories for the project:

- [mapbox/earcut](https://github.com/mapbox/earcut) as a very fast javascript polygon triangulation library, which I converted to python and used as the core triangulator.
- [crm416/point-location](https://github.com/crm416/point-location) as an implementation of the Kirkpatrick point location in python.
