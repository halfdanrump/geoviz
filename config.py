
# set area name and radius (should be set dynamically rather than here)
radius = 1000
area_name = 'shinjuku'
network_type = 'drive'

# folder for saving downloaded street graphs
graph_folder = '/Users/halfdan-rump/projects/datalab/data/street_networks'

# folder for storing city blocks geojson data
def get_cityblock_geojson_filename(area_name, radius):
    return '/Users/halfdan-rump/projects/datalab/data/areas/{}-{}.geojson'.format(area_name, radius)

# Toggle this False to force city_blocks notebook to recalculate city_blocks
cityblocks_use_cached = False

#folder for storing choropleth maps
choropleth_filename = '/Users/halfdan-rump/projects/datalab/maps/choropleth-{}-{}'.format(area_name, radius)

# dict with named coordinates for convenience
area_coords = {'nakano': (35.7059402,139.6664317),
               'shinjuku': (35.6918383, 139.702996),
               'daikanyama': (35.64776,139.7019901)}

assert area_name in area_coords.keys()

# in some dataframes longitude is stored as 'x' and latitude as 'y'
lat_key = 'y'
lon_key = 'x'


northlatitude, eastlongitude = area_coords.get(area_name)

# Specify origin tuples. osmxn switch uses (lat,lon) whereas geopy(?) uses (lon, lat)
origin = (eastlongitude, northlatitude)
origin_osmnx = (northlatitude, eastlongitude) 

# specify names of columns with coordinates. The order matters. 
coordinate_columns = ['eastlongitude', 'northlatitude']

MAX_RECURSION_DEPTH = 999
