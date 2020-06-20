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

![Program in Action](figs/map.png?raw=true "Shortest Polyline")

# Configuration
You can adjust the project configuration by editing the file `constants.py`. There you can adjust the number of threads, the maximum number of polygons that are shown, turn on and off the triangle path visualization and determine the threshold above which we use Kirkpatrick point location instead of Exhaustive point location.

# Acknowledgements
Apart from the classic python libraries used (e.g. numpy,matplotlib, scipy...), I also used and modified the following repositories for the project:

- [mapbox/earcut](https://github.com/mapbox/earcut) as a very fast javascript polygon triangulation library, which I converted to python and used as the core triangulator.
- [crm416/point-location](https://github.com/crm416/point-location) as an implementation of the Kirkpatrick point location in python.
