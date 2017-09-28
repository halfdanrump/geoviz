import os

# set area name and radius (should be set dynamically rather than here)
radius = 1000
area_name = 'shinjuku'
network_type = 'drive'

# folder for saving downloaded street graphs

basepath = os.environ.get('GEOVIZ_TMP', None)

tmp_folder_path = '~/geotmp' ### Set this to an existing folder
assert tmp_folder_path, 'please specify a path to store temprary/cached files'

# Toggle this False to force city_blocks notebook to recalculate city_blocks
cityblocks_use_cached = False

# dict with named coordinates for convenience
area_coords = {'nakano': (35.7059402,139.6664317),
               'shinjuku': (35.6918383, 139.702996),
               'daikanyama': (35.64776,139.7019901)}

assert area_name in area_coords.keys()

# in some dataframes longitude is stored as 'x' and latitude as 'y'
lat_key = 'y'
lon_key = 'x'
