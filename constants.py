
# Maximum number of triangles for which we allow linear
# point location instead of kirkpatrick.
# Increasing this number yields slower preprocessing
# but faster point location
LINEAR_SEARCH_MAX_TRIANGLES = 500

# In order for the GUI to work correctly, we have to restrict
# the number of polygons used, so for each file we keep
# the 2000 biggest polygons.
# The algorithms work equally well for all polygons,
# but the GUI doesn't
MAX_POLYGONS = 2000

# Number of threads in the thread pool.
# Set this equal to the number of threads
# in your CPU
NUM_THREADS = 8

# Whether or not we want to visualize
# the trinagles participating in the pathfinding
VISUALIZE_TRIANGLES = False