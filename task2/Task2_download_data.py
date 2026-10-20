import json
import osmnx as ox

# Coordinates of the center of Surabaya and radius (16 km)
surabaya_center = (-7.2575, 112.7521)
radius_meters = 16000
custom_filter = '["highway"~"trunk|primary|secondary|tertiary"]'

print("Downloading the Surabaya road network via OSMnx...")
G = ox.graph_from_point(
    surabaya_center,
    dist=radius_meters,
    network_type="drive",
    custom_filter=custom_filter,
)

nodes = {}
for node, data in G.nodes(data=True):
    nodes[str(node)] = [data['y'], data['x']]

edges = {}
edge_names = {}
edge_geometries = {}  # Pour stocker les points intermédiaires de la courbe de la rue

for u, v, key, data in G.edges(keys=True, data=True):
    u_str = str(u)
    v_str = str(v)
    weight = data.get('length', 1.0)
    
    edges.setdefault(u_str, {})[v_str] = weight
    
    # Récupération propre du nom de la rue
    name = data.get("name", "Unnamed road")
    if isinstance(name, list):
        name = ", ".join(name)
    edge_names.setdefault(u_str, {})[v_str] = name

    # Extraction de la géométrie détaillée (courbes de la route) si disponible
    if "geometry" in data:
        # geometry.coords donne une liste de (lon, lat), on convertit en [lat, lon] pour Folium
        geom_coords = [[coord[1], coord[0]] for coord in data["geometry"].coords]
        edge_geometries.setdefault(u_str, {})[v_str] = geom_coords
    else:
        # Fallback sur les points de début et de fin si pas de géométrie spécifique
        edge_geometries.setdefault(u_str, {})[v_str] = [nodes[u_str], nodes[v_str]]

dataset = {
    "nodes": nodes,
    "edges": edges,
    "edge_names": edge_names,
    "edge_geometries": edge_geometries
}

output_path = "surabaya_map.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(dataset, f)

print(f"File '{output_path}' successfully generated with precise street geometries!")
print(f"- Nodes: {len(nodes)}")
print(f"- Edges: {len(edges)}")
