import numpy as np
from numpy.linalg import norm
from tqdm import tqdm
from shapely.geometry import Polygon
import geopandas as gpd
import osmnx as ox
from pathlib import Path
from .config import lat_key, lon_key, tmp_folder_path

# Algorithm described here: 
# https://blog.reactoweb.com/2012/04/algorithm-101-finding-all-polygons-in-an-undirected-graph/

_MAX_RECURSION_DEPTH = 999

def _angle(a,b):
    return np.degrees(np.arccos(np.dot(a, b)/(norm(a)*norm(b))))*np.sign(np.cross(b,a))

def _step(graph, edge, path, depth, traversed, edge_coords, polygons):
    depth += 1
    
    # create list of successors to the edge
    successors = [(edge[1], n) for n in graph.neighbors(edge[1])]

    # Remove edge in the opposite direction, so that the algorithm doesn't simple jump back to the previous point
    successors.remove(tuple(np.flip((edge),0)))
    
    # Remove edges that have already been traversed
    successors = list(filter(lambda s: s not in traversed, successors))

    if not successors: 
        # The successors have all been walked, so no more areas can be found 
        return 

    # calculate angles to incoming edge and order successors by smallest angle
    angles = [_angle(edge_coords.get(edge), edge_coords.get(successor)) for successor in successors]
    
    # pick leftmost edge
    edge_to_walk = successors[np.argmin(angles)]
        
    if edge_to_walk in path:
        traversed.update([edge_to_walk])
        #We are back where we started, which means that we found a polygon
        polygons.append(path)
        return
    else:
        if depth > _MAX_RECURSION_DEPTH:
            return
        path.append(edge_to_walk)   
        _step(graph, edge_to_walk, path, depth, traversed, edge_coords, polygons)


def city_blocks(street_graph):
    """
    Given a street graph, returns city-blocks, i.e., blocks of land that occupy 
    space in the city and are encapsulated by roads on every side.

    Args:
        street_graph (networkx.classes.multidigraph): graph representing street network as returned by osmnx.

    Returns: 
        

    """
    directed = street_graph.to_directed()

    # pre-compute mapping from edge name to edge coordinates
    edge_coords = {(f,t): 
               ([float(directed.node.get(f).get(lat_key))-float(directed.node.get(t).get(lat_key)), 
                 float(directed.node.get(f).get(lon_key))-float(directed.node.get(t).get(lon_key))]) 
               for (f, t, d) in directed.edges(data=True)}

    traversed = set()
    graph_polygons = list()

    for edge in tqdm(directed.edges()):
        path = [edge]
        _step(directed, edge, path, 0, traversed, edge_coords, graph_polygons)
        
    # Remove the polygon with the most nodes (assuming that it is the perimeter
    polygons = sorted(graph_polygons, key=lambda x: len(x))[:-1]

    # grabbing the endpoint of all edges in the graph
    polygons_points = [[e[0] for e in p] for p in polygons]
    path_coords = [[(float(directed.node[n][lon_key]), float(directed.node[n][lat_key]))
                    for n in path] for path in polygons_points]
    polygons = [Polygon(path) for path in path_coords]
    areas = gpd.GeoDataFrame({'geometry': polygons})
    return areas


def remove_deadends(g, plot_all=False):
    """
    Reduce the number of nodes and edges in g by iteratively removing
    every node with degree one, and the connected vertex.
    
    Args:
        g (networkx.classes.multidigraph): Street graph from osmnx.
    
    Returns:
        networkx.classes.multidigraph: The simplified street graph.
    """
    
    simpler = g.to_undirected().copy()
    while True:
        nc = ['r' if degree <= 1 else 'b' for node, degree in simpler.degree().items()]
        n_nodes = len(simpler.nodes())        
        n_removed = len(list(filter(lambda x: x=='r', nc)))
        if plot_all:
            print('number of nodes in graph: {}, and number of nodes that will be removed: {}'.format(n_nodes, n_removed))
            ox.plot_graph(simpler, node_color=nc, node_zorder=3)

        for node, degree in simpler.degree().items():
            if degree <= 1: 
                simpler.remove_node(node)

        if len(simpler.nodes()) == n_nodes:
            break
    return simpler



def load_street_graph(coords, radius=1000, network_type='drive', filename=None, use_cached=True):
    """
    Loads street graph data that falls within the circle defined by a center
    and a radius. Uses cached data, or download if necessary. 
    
    Args:
        coords (tuple): (latitude,longitude) tuple of coordinates.
        radius (int): radius in meters.
        network_type (str): The type of street network to download.
        name (str): optional alias for graph when stored on disk.
        use_cached: Set to False to force redownload of graph data.
        
    Returns:
        networkx.classes.multidigraph: street graph data
    """
    if use_cached:
        tmp = Path(tmp_folder_path).expanduser()
        assert tmp.exists(), 'please create the tmp folder manually, to avoid any funky mishaps'
    ### some path acrobatics for compatibility with osmnx
    if filename:
        assert filename.endswith('.graphml')
    else:
        filename = '{}-{}-{}.graphml'.format(coords, radius, network_type)
    graph_file = Path(tmp, filename)
    folder = str(tmp)
    
    if graph_file.exists() and use_cached:
        print('restoring full street graph from disk')
        street_graph = ox.load_graphml(filename=filename, folder=folder)
    else:
        print('downloading street graph')
        street_graph = ox.graph_from_point(
            coords, 
            distance=radius,
            distance_type='network', 
            network_type=network_type, 
            simplify=False)

        print('saving graph to disk')
        ox.save_graphml(
            street_graph, 
            filename=filename, 
            folder=folder)
    return street_graph
