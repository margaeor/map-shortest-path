
# Maximum number of triangles for which we allow linear
# point location instead of kirkpatrick.
# Increasing this number yields slower preprocessing
# but faster point location
LINEAR_SEARCH_MAX_TRIANGLES = 500

# In order for the GUI to work correctly, we have to restrict
# the number of polygons used, so for each file we keep
# the 2000 biggest polygons
MAX_POLYGONS = 2000

# Number of threads in the thread pool
NUM_THREADS = 4

# Whether or not we want to visualize
# the trinagles participating in the pathfinding
VISUALIZE_TRIANGLES = False