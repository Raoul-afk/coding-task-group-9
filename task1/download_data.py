import json
import math
import os
import requests

# Bounding box around Surabaya (South, West, North, East)
BBOX = (-7.33, 112.70, -7.22, 112.82)


def haversine(lat1, lon1, lat2, lon2):
    # calculates the distance in kilometers between two GPS points
    x = math.radians(lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2))
    y = math.radians(lat2 - lat1)
    return 6371.0 * math.hypot(x, y)

def fetch_osm_raw_data():
    #downloads road network and school locations via Overpass API
    query = f"""
    [out:json][timeout:60];
    (
      way["highway"~"^(trunk|primary|secondary|tertiary)$"]{BBOX};
      node["amenity"="school"]{BBOX};
      way["amenity"="school"]{BBOX};
    );
    out body center;
    >;
    out skel qt;
    """

    headers = {
        "User-Agent": "ITS-GraphTheory-Project-Surabaya/1.0"
    }

    endpoints = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.openstreetmap.fr/api/interpreter",
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
    ]

    for url in endpoints:
        try:
            print(f"Attempting download via {url}...")
            response = requests.post(url, data={"data": query}, headers=headers, timeout=60)
            if response.status_code == 200:
                return response.json()
            print(f"Failed ({response.status_code}), trying next mirror...")
        except Exception as e:
            print(f"Connection error ({e}), trying next mirror...")

    raise RuntimeError("Unable to fetch data from Overpass servers.")


def process_and_save():
    raw_data = fetch_osm_raw_data()

    all_osm_nodes = {}
    schools = []
    road_ways = []

    for element in raw_data.get("elements", []):
        elem_type = element["type"]

        if elem_type == "node":
            all_osm_nodes[element["id"]] = (element["lat"], element["lon"])
            if element.get("tags", {}).get("amenity") == "school":
                name = element.get("tags", {}).get("name", f"School {element['id']}")
                schools.append(
                    {"name": name, "lat": element["lat"], "lon": element["lon"]}
                )

        elif elem_type == "way":
            tags = element.get("tags", {})
            if tags.get("amenity") == "school" and "center" in element:
                name = tags.get("name", f"School {element['id']}")
                schools.append(
                    {
                        "name": name,
                        "lat": element["center"]["lat"],
                        "lon": element["center"]["lon"],
                    }
                )
            elif "highway" in tags:
                road_ways.append(element)

    graph = {}
    used_nodes = {}

    for way in road_ways:
        nodes_sequence = way["nodes"]
        oneway_tag = way.get("tags", {}).get("oneway", "no")

        for i in range(len(nodes_sequence) - 1):
            u_id = nodes_sequence[i]
            v_id = nodes_sequence[i + 1]

            if u_id not in all_osm_nodes or v_id not in all_osm_nodes:
                continue

            u = str(u_id)
            v = str(v_id)

            lat1, lon1 = all_osm_nodes[u_id]
            lat2, lon2 = all_osm_nodes[v_id]
            dist = haversine(lat1, lon1, lat2, lon2)

            used_nodes[u] = [lat1, lon1]
            used_nodes[v] = [lat2, lon2]

            graph.setdefault(u, {})
            graph.setdefault(v, {})

            if oneway_tag == "-1":
                graph[v][u] = dist
            elif oneway_tag in ("yes", "true", "1"):
                graph[u][v] = dist
            else:
                graph[u][v] = dist
                graph[v][u] = dist

    os.makedirs("data", exist_ok=True)
    output_path = "data/surabaya_data.json"

    dataset = {
        "nodes": used_nodes,
        "edges": graph,
        "schools": schools
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f)

    print("Download and processing completed successfully.")
    print(f"- Intersections (Digraph nodes): {len(used_nodes)}")
    print(f"- Schools recorded: {len(schools)}")
    print(f"- File saved: {output_path}")


if __name__ == "__main__":
    process_and_save()