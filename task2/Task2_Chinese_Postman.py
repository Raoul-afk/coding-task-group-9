import json
import os
import time
import folium
import streamlit as st
from streamlit_folium import st_folium

from graph_engine import (
    dijkstra,
    find_nearest_node,
    get_path,
    haversine,
    hierholzer
)

st.set_page_config(layout="wide", page_title="DLH Waste Collection - Chinese Postman")
st.title("DLH Waste Collection Simulator (Chinese Postman Problem)")


@st.cache_data
def load_data():
    with open("surabaya_map.json", "r", encoding="utf-8") as f:
        return json.load(f)


try:
    data = load_data()
    nodes = data["nodes"]       # Format: {node_id: [lat, lon], ...}
    edges = data["edges"]       # Format: {u: {v: weight, ...}, ...}
    edge_names = data.get("edge_names", {})  # Street names extracted from OSMnx
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# DLH Depot Coordinates
if "lat" not in st.session_state:
    st.session_state.lat = -7.280000
if "lon" not in st.session_state:
    st.session_state.lon = 112.790000
if "result" not in st.session_state:
    st.session_state.result = None

col_map, col_menu = st.columns([2, 1])

with col_menu:
    input_lat = st.number_input("DLH Depot Latitude", value=float(st.session_state.lat), format="%.6f", step=0.001)
    input_lon = st.number_input("DLH Depot Longitude", value=float(st.session_state.lon), format="%.6f", step=0.001)

    if (input_lat, input_lon) != (st.session_state.lat, st.session_state.lon):
        st.session_state.lat = input_lat
        st.session_state.lon = input_lon
        st.session_state.result = None

    radius_km = st.slider("Collection radius (km)", 0.5, 5.0, 1.5, 0.1)
    depot_coord = [st.session_state.lat, st.session_state.lon]

    if st.button("Generate collection route", type="primary"):
        t_start = time.perf_counter()

        # 1. Network node closest to the DLH depot
        base_node = find_nearest_node(depot_coord[0], depot_coord[1], nodes)

        # 2. STRICT filtering of nodes within the geographical circle (Haversine)
        local_nodes = {
            nid for nid, coord in nodes.items()
            if haversine(depot_coord[0], depot_coord[1], coord[0], coord[1]) <= radius_km
        }

        # Guaranteed inclusion of the depot node
        local_nodes.add(base_node)

        # 3. Subgraph strictly restricted to these nodes
        sub_edges = {}
        for u in local_nodes:
            if u in edges:
                valid_neighbors = {v: w for v, w in edges[u].items() if v in local_nodes}
                if valid_neighbors:
                    sub_edges[u] = valid_neighbors

        # Isolation of the component connected to the depot
        dists_depot, _ = dijkstra(sub_edges, base_node)
        connected_nodes = set(dists_depot.keys())

        sub_edges = {
            u: {v: w for v, w in neighbors.items() if v in connected_nodes}
            for u, neighbors in sub_edges.items()
            if u in connected_nodes
        }

        if not connected_nodes or len(connected_nodes) < 2:
            st.warning("No accessible streets within this radius around the depot.")
        else:
            # 4. Balancing the directed graph (Chinese Postman Problem)
            in_deg = {n: 0 for n in connected_nodes}
            out_deg = {n: 0 for n in connected_nodes}
            for u, neighbors in sub_edges.items():
                out_deg[u] += len(neighbors)
                for v in neighbors:
                    in_deg[v] += 1

            balanced_edges = {u: dict(v_dict) for u, v_dict in sub_edges.items()}

            for _ in range(1000):
                imbalance = {n: in_deg[n] - out_deg[n] for n in connected_nodes if in_deg[n] != out_deg[n]}
                if not imbalance:
                    break

                excess = [n for n, d in imbalance.items() if d > 0]
                deficit = [n for n, d in imbalance.items() if d < 0]
                if not excess or not deficit:
                    break

                dists_ex, parents_ex = dijkstra(balanced_edges, excess[0])
                valid_targets = [v for v in deficit if v in dists_ex and dists_ex[v] != float('inf')]

                if valid_targets:
                    target = min(valid_targets, key=lambda v: dists_ex[v])
                    path = get_path(parents_ex, target)
                    for i in range(len(path) - 1):
                        u_node, v_node = path[i], path[i + 1]
                        w_val = sub_edges.get(u_node, {}).get(v_node, 1.0)
                        balanced_edges.setdefault(u_node, {})[v_node] = w_val
                        out_deg[u_node] += 1
                        in_deg[v_node] += 1
                else:
                    break

            try:
                eulerian_path = hierholzer(balanced_edges, base_node)

                # 6. GPS route plotting and direct distance calculation via Haversine
                gps_route = []
                total_dist_km = 0.0

                for i in range(len(eulerian_path) - 1):
                    u_node = eulerian_path[i]
                    v_node = eulerian_path[i + 1]

                    coord_u = nodes[u_node]
                    coord_v = nodes[v_node]

                    gps_route.append(coord_u)
                    total_dist_km += haversine(coord_u[0], coord_u[1], coord_v[0], coord_v[1])

                if eulerian_path:
                    gps_route.append(nodes[eulerian_path[-1]])

                exec_time = (time.perf_counter() - t_start) * 1000
                estimated_travel_time_min = (total_dist_km / 25.0) * 60.0

                st.session_state.result = {
                    "total_dist_km": total_dist_km,
                    "exec_time": exec_time,
                    "steps": len(eulerian_path),
                    "gps_route": gps_route,
                    "estimated_travel_time_min": estimated_travel_time_min,
                    "eulerian_path": eulerian_path
                }
            except Exception as ex:
                st.error(f"Error generating the circuit: {ex}")

# Map Display (Esri Tiles)
m = folium.Map(location=depot_coord, zoom_start=14, tiles=None)
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    attr="Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom"
).add_to(m)

# DLH Truck Depot Marker
folium.Marker(
    depot_coord,
    popup="DLH Truck Depot",
    icon=folium.Icon(color="green", icon="truck", prefix="fa")
).add_to(m)

# Intervention zone circle
folium.Circle(
    depot_coord,
    radius=radius_km * 1000,
    color="red",
    fill=True,
    fill_opacity=0.08
).add_to(m)

if st.session_state.result is not None:
    res = st.session_state.result
    folium.PolyLine(res["gps_route"], color="#e74c3c", weight=4, opacity=0.85).add_to(m)

    with col_menu:
        st.success("DLH collection route generated!")
        st.metric("Total distance", f"{res['total_dist_km']:.2f} km")
        st.metric("Estimated travel time (25 km/h)", f"{res['estimated_travel_time_min']:.1f} min")
        st.metric("Number of steps", res["steps"])
        st.metric("Execution time", f"{res['exec_time']:.2f} ms")

        st.subheader("Traversed streets (Routing order):")
        
        # Convert node path into a list of consecutive street names
        street_sequence = []
        path_nodes = res["eulerian_path"]
        for i in range(len(path_nodes) - 1):
            u_n = path_nodes[i]
            v_n = path_nodes[i + 1]
            s_name = edge_names.get(u_n, {}).get(v_n, "Unnamed road")
            street_sequence.append(s_name)

        # Group consecutive segments of the same street for clean display
        cleaned_streets = []
        for street in street_sequence:
            if not cleaned_streets or cleaned_streets[-1] != street:
                cleaned_streets.append(street)

        # Display the first 30 streets of the tour
        for idx, street_name in enumerate(cleaned_streets[:30]):
            st.write(f"**{idx + 1}.** {street_name}")
        if len(cleaned_streets) > 30:
            st.info(f"... and {len(cleaned_streets) - 30} additional streets in the circuit.")

with col_map:
    map_data = st_folium(m, width=750, height=580, returned_objects=["last_clicked"])
    if map_data and map_data.get("last_clicked"):
        c_lat = round(map_data["last_clicked"]["lat"], 6)
        c_lon = round(map_data["last_clicked"]["lng"], 6)
        if (c_lat, c_lon) != (st.session_state.lat, st.session_state.lon):
            st.session_state.lat = c_lat
            st.session_state.lon = c_lon
            st.session_state.result = None
            st.rerun()