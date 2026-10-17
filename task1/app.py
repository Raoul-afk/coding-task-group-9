import json
import time
import folium
import streamlit as st
from streamlit_folium import st_folium

from graph_engine import (
    dijkstra,
    find_nearest_node,
    get_path,
    haversine,
    solve_tsp
)

st.set_page_config(layout="wide", page_title="SPPG Simulator")
st.title("SPPG mealbox delivery")


@st.cache_data
def load_data():
    with open("data/surabaya_data.json", "r", encoding="utf-8") as f:
        return json.load(f)


data = load_data()
nodes = data["nodes"]
edges = data["edges"]
schools = data["schools"]

# we set default start location
if "sppg_lat" not in st.session_state:
    st.session_state.sppg_lat = -7.280000
if "sppg_lon" not in st.session_state:
    st.session_state.sppg_lon = 112.790000
if "result" not in st.session_state:
    st.session_state.result = None

col_map, col_menu = st.columns([2, 1])

with col_menu:

    input_lat = st.number_input(
        "SPPG Latitude",
        value=float(st.session_state.sppg_lat),
        format="%.6f",
        step=0.001
    )
    input_lon = st.number_input(
        "SPPG Longitude",
        value=float(st.session_state.sppg_lon),
        format="%.6f",
        step=0.001
    )

    if (input_lat, input_lon) != (st.session_state.sppg_lat, st.session_state.sppg_lon):
        st.session_state.sppg_lat = input_lat
        st.session_state.sppg_lon = input_lon
        st.session_state.result = None

    radius = st.slider("Delivery radius x (km)", 0.2, 5.0, 1.5, 0.1)
    sppg_coord = [st.session_state.sppg_lat, st.session_state.sppg_lon]

    nearby_schools = [
        s for s in schools
        if haversine(sppg_coord[0], sppg_coord[1], s["lat"], s["lon"]) <= radius
    ]

    st.write(f"**Schools in radius:** {len(nearby_schools)}")

    if st.button("Calculate TSP route", type="primary"):
        if len(nearby_schools) == 0:
            st.warning("No schools found within this radius.")
            st.session_state.result = None
        else:
            t_start = time.perf_counter()

            # nearest road intersection to position the SPPG
            sppg_node = find_nearest_node(sppg_coord[0], sppg_coord[1], nodes)

            # reverse graph for reachability check
            rev_edges = {}
            for u in edges:
                for v, dist in edges[u].items():
                    rev_edges.setdefault(v, {})[u] = dist

            # we run Dijkstra to find the strongly connected vertices with SPPG
            dist_out, preds_out = dijkstra(edges, sppg_node)
            dist_in, _ = dijkstra(rev_edges, sppg_node)

            valid_nodes = set(dist_out.keys()) & set(dist_in.keys())
            if not valid_nodes:
                valid_nodes = set(dist_out.keys())

            # attach each school to the nearest valid intersection
            target_points = [{"name": "SPPG (Start/End)", "node": sppg_node}]

            for school in nearby_schools:
                min_d = float("inf")
                best_n = sppg_node
                for nid in valid_nodes:
                    d = haversine(school["lat"], school["lon"], nodes[nid][0], nodes[nid][1])
                    if d < min_d:
                        min_d = d
                        best_n = nid
                target_points.append({"name": school["name"], "node": best_n})

            num_points = len(target_points)

            # build distance matrix and path table
            cost_matrix = [[0.0] * num_points for _ in range(num_points)]
            paths = {}

            for i in range(num_points):
                dep = target_points[i]["node"]
                dists, parents = dijkstra(edges, dep)
                paths[i] = {}
                for j in range(num_points):
                    if i == j:
                        cost_matrix[i][j] = 0.0
                    else:
                        arr = target_points[j]["node"]
                        if dep == arr:
                            cost_matrix[i][j] = 0.0
                            paths[i][arr] = [dep]
                        elif arr in dists:
                            cost_matrix[i][j] = dists[arr]
                            paths[i][arr] = get_path(parents, arr)
                        else:
                            p_to_sppg = get_path(parents, sppg_node)
                            p_from_sppg = get_path(preds_out, arr)
                            cost_matrix[i][j] = dists.get(sppg_node, 0.0) + dist_out.get(arr, 0.0)
                            paths[i][arr] = p_to_sppg + p_from_sppg[1:]

            # solve TSP
            tour, total_dist = solve_tsp(cost_matrix)
            exec_time_ms = (time.perf_counter() - t_start) * 1000

            # reconstruct actual GPS coordinates for the road route
            gps_route = []
            for k in range(len(tour) - 1):
                dep_idx = tour[k]
                arr_node = target_points[tour[k + 1]]["node"]
                segment_nodes = paths[dep_idx].get(arr_node, [])
                for nid in segment_nodes:
                    gps_route.append(nodes[nid])

            st.session_state.result = {
                "tour": tour,
                "points": target_points,
                "total_dist": total_dist,
                "exec_time_ms": exec_time_ms,
                "gps_route": gps_route
            }

# the map rendering
m = folium.Map(location=sppg_coord, zoom_start=14, tiles=None)
folium.TileLayer(
    tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    attr="&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors",
    referrer_policy="strict-origin"
).add_to(m)

folium.Marker(
    sppg_coord,
    popup="SPPG",
    icon=folium.Icon(color="red", icon="home")
).add_to(m)

folium.Circle(
    sppg_coord,
    radius=radius * 1000,
    color="red",
    fill=True,
    fill_opacity=0.05
).add_to(m)

for s in nearby_schools:
    folium.CircleMarker(
        [s["lat"], s["lon"]],
        radius=5,
        color="blue",
        fill=True,
        popup=s["name"]
    ).add_to(m)

if st.session_state.result is not None:
    res = st.session_state.result
    folium.PolyLine(res["gps_route"], color="green", weight=4, opacity=0.8).add_to(m)

    with col_menu:
        st.success("Route successfully generated")
        st.metric("Total distance", f"{res['total_dist']:.2f} km")
        st.metric("Estimated travel time (30 km/h)", f"{(res['total_dist'] / 30) * 60:.0f} min")
        st.metric("TSP solver execution time", f"{res['exec_time_ms']:.2f} ms")

        st.subheader("Visiting order:")
        for step, p_idx in enumerate(res["tour"]):
            st.write(f"**{step + 1}.** {res['points'][p_idx]['name']}")
# for interactive map
with col_map:
    map_data = st_folium(m, width=750, height=580, returned_objects=["last_clicked"])
    if map_data and map_data.get("last_clicked"):
        c_lat = round(map_data["last_clicked"]["lat"], 6)
        c_lon = round(map_data["last_clicked"]["lng"], 6)
        if (c_lat, c_lon) != (st.session_state.sppg_lat, st.session_state.sppg_lon):
            st.session_state.sppg_lat = c_lat
            st.session_state.sppg_lon = c_lon
            st.session_state.result = None
            st.rerun()