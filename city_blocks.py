import numpy as np
from numpy.linalg import norm
from tqdm import tqdm
from config import lat_key, lon_key, MAX_RECURSION_DEPTH
from shapely.geometry import Polygon
import geopandas as gpd

# Algorithm described here: 
# https://blog.reactoweb.com/2012/04/algorithm-101-finding-all-polygons-in-an-undirected-graph/

def angle(a,b):
#     print(a, b)
    return np.degrees(np.arccos(np.dot(a, b)/(norm(a)*norm(b))))*np.sign(np.cross(b,a))

def step(graph, edge, path, depth, traversed, edge_coords, polygons):
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
    angles = [angle(edge_coords.get(edge), edge_coords.get(successor)) for successor in successors]
    
    # pick leftmost edge
    edge_to_walk = successors[np.argmin(angles)]
        
    if edge_to_walk in path:
        traversed.update([edge_to_walk])
        #We are back where we started, which means that we found a polygon
        polygons.append(path)
        return
    else:
        if depth > MAX_RECURSION_DEPTH:
            return
        path.append(edge_to_walk)   
        step(graph, edge_to_walk, path, depth, traversed, edge_coords, polygons)


def city_blocks(street_graph):
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
        step(directed, edge, path, 0, traversed, edge_coords, graph_polygons)
        
    # Remove the polygon with the most nodes (assuming that it is the perimeter
    polygons = sorted(graph_polygons, key=lambda x: len(x))[:-1]

    # grabbing the endpoint of all edges in the graph
    polygons_points = [[e[0] for e in p] for p in polygons]
    path_coords = [[(float(directed.node[n][lon_key]), float(directed.node[n][lat_key]))
                    for n in path] for path in polygons_points]
    polygons = [Polygon(path) for path in path_coords]
    areas = gpd.GeoDataFrame({'geometry': polygons})


    return areas



