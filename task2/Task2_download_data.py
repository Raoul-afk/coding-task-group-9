import json
import math
import os
import requests

# Bounding box autour de Surabaya
BBOX = (-7.33, 112.70, -7.22, 112.82)

def haversine(lat1, lon1, lat2, lon2):
    x = math.radians(lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2))
    y = math.radians(lat2 - lat1)
    return 6371.0 * math.hypot(x, y)

def fetch_osm_raw_data():
    # Filtrage restreint aux axes principaux pour éviter l'explosion du nombre de rues
    query = f"""
    [out:json][timeout:60];
    (
      way["highway"~"^(trunk|primary|secondary|tertiary)$"]{BBOX};
    );
    out body center;
    >;
    out skel qt;
    """
    headers = {"User-Agent": "DLH-ChinesePostman-Surabaya/1.0"}
    endpoints = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.openstreetmap.fr/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
    ]
    for url in endpoints:
        try:
            print(f"Tentative de téléchargement via {url}...")
            response = requests.post(url, data={"data": query}, headers=headers, timeout=60)
            if response.status_code == 200:
                return response.json()
        except Exception:
            continue
    raise RuntimeError("Impossible de récupérer les données depuis les serveurs Overpass.")

def process_and_save():
    raw_data = fetch_osm_raw_data()
    all_osm_nodes = {}
    road_ways = []

    for element in raw_data.get("elements", []):
        if element["type"] == "node":
            all_osm_nodes[element["id"]] = (element["lat"], element["lon"])
        elif element["type"] == "way":
            if "highway" in element.get("tags", {}):
                road_ways.append(element)

    edges = {}
    nodes = {}
    edge_names = {}

    for way in road_ways:
        nodes_sequence = way["nodes"]
        tags = way.get("tags", {})
        name = tags.get("name", "Unnamed road")
        oneway = tags.get("oneway", "no")

        for i in range(len(nodes_sequence) - 1):
            u_id = nodes_sequence[i]
            v_id = nodes_sequence[i + 1]

            if u_id not in all_osm_nodes or v_id not in all_osm_nodes:
                continue

            u, v = str(u_id), str(v_id)
            lat1, lon1 = all_osm_nodes[u_id]
            lat2, lon2 = all_osm_nodes[v_id]
            dist = haversine(lat1, lon1, lat2, lon2)

            nodes[u] = [lat1, lon1]
            nodes[v] = [lat2, lon2]

            edges.setdefault(u, {})
            edge_names.setdefault(u, {})

            if oneway == "-1":
                edges.setdefault(v, {})[u] = dist
                edge_names.setdefault(v, {})[u] = name
            elif oneway in ("yes", "true", "1"):
                edges[u][v] = dist
                edge_names[u][v] = name
            else:
                edges[u][v] = dist
                edges.setdefault(v, {})[u] = dist
                edge_names[u][v] = name
                edge_names.setdefault(v, {})[u] = name

    dataset = {
        "nodes": nodes,
        "edges": edges,
        "edge_names": edge_names
    }

    output_path = "surabaya_map.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f)

    print(f"Fichier '{output_path}' généré avec succès !")
    print(f"- Nœuds : {len(nodes)}")
    print(f"- Arêtes : {len(edges)}")

if __name__ == "__main__":
    process_and_save()
