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

for u, v, data in G.edges(data=True):
    u_str = str(u)
    v_str = str(v)
    weight = data.get('length', 1.0)
    
    edges.setdefault(u_str, {})[v_str] = weight
    
    # Clean retrieval of the street name from OSMnx
    name = data.get("name", "Unnamed road")
    if isinstance(name, list):
        name = ", ".join(name)
    
    edge_names.setdefault(u_str, {})[v_str] = name

# Clean structure without schools
dataset = {
    "nodes": nodes,
    "edges": edges,
    "edge_names": edge_names
}

output_path = "surabaya_map.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(dataset, f)

print(f"File '{output_path}' successfully generated!")
print(f"- Nodes: {len(nodes)}")
print(f"- Edges: {len(edges)}")