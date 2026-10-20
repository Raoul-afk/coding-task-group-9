import heapq
import math


def haversine(lat1, lon1, lat2, lon2):
    #Calculates line distance in km between two GPS coordinates
    dx = (lon2 - lon1) * 110.0
    dy = (lat2 - lat1) * 111.0
    return math.sqrt(dx * dx + dy * dy)

def find_nearest_node(lat, lon, nodes):
    #Finds the nearest road intersection node from a given coordinate
    best_id = None
    min_d = float("inf")
    for nid, coord in nodes.items():
        d = haversine(lat, lon, coord[0], coord[1])
        if d < min_d:
            min_d = d
            best_id = nid
    return best_id


def dijkstra(graph, start_node):
    # computes shortest path from start_node to all other reachable nodes
    # returns distances and predecessor map for path reconstruction
    # same as UCS in IA
    
    distances = {start_node: 0.0}
    parents = {start_node: None}
    queue = [(0.0, start_node)]

    while queue:
        current_dist, u = heapq.heappop(queue)

        if current_dist > distances.get(u, float("inf")):
            continue

        for v, weight in graph.get(u, {}).items():
            new_dist = current_dist + weight
            if new_dist < distances.get(v, float("inf")):
                distances[v] = new_dist
                parents[v] = u
                heapq.heappush(queue, (new_dist, v))

    return distances, parents


def get_path(parents, target_node):
    # reconstructs the list of node IDs to reach target_node

    path = []
    curr = target_node
    while curr is not None:
        path.append(curr)
        curr = parents.get(curr)
    path.reverse()
    return path

def hierholzer(graph, start_node):
    # Create a local copy of the adjacency list to consume edges as we traverse them
    g = {u: list(v_dict.keys()) for u, v_dict in graph.items()}
    
    stack = [start_node]
    circuit = []
    
    while stack:
        curr = stack[-1]
        
        # If there are still unvisited outgoing edges from this node
        if g.get(curr):
            next_node = g[curr].pop()  # Take and remove the edge
            stack.append(next_node)
        else:
            # If there are no more outgoing edges, pop the node and add it to the circuit
            circuit.append(stack.pop())
            
    # The circuit is built in reverse order, so we reverse it back to get the correct chronological path
    return circuit[::-1]