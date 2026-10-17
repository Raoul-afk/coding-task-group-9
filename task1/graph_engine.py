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


def solve_tsp(cost_matrix):
    # greedy hamiltonian tour (nearest neighbor): at each step, visits the nearest unvisited school
    
    n = len(cost_matrix)
    unvisited = set(range(1, n))
    tour = [0]
    current = 0

    while unvisited:
        next_node = min(unvisited, key=lambda x: cost_matrix[current][x])
        tour.append(next_node)
        unvisited.remove(next_node)
        current = next_node

    tour.append(0)  # Retour au SPPG pour fermer le cycle Hamiltonien
    total_cost = sum(cost_matrix[tour[i]][tour[i + 1]] for i in range(len(tour) - 1))

    return tour, total_cost