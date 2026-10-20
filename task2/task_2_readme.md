# DLH Waste Collection Route Simulator - Task 2

This application simulates optimal garbage collection routes for the Surabaya Department of Environment (DLH) across the local road network using OpenStreetMap data and graph algorithms to solve the Chinese Postman Problem (CPP).

## Prerequisites

Ensure you have Python 3.9+ installed.

Install the required dependencies using:
```bash
pip install -r requirements
```

Key packages utilized:
- `streamlit`: powers the interactive web dashboard.
- `folium` & `streamlit-folium`: render the interactive map layer and process map clicks.
- `osmnx`: handles downloading and parsing OpenStreetMap road networks.

## Project Files

- `Task2_Chinese_Postman.py`: The main Streamlit web application. Manages user inputs, performs spatial subgraph filtering, graph balancing, and renders the collection route.
- `graph_engine.py`: Contains the core pure-Python algorithmic logic (Dijkstra's shortest path, Haversine distance, path reconstruction, and Hierholzer's algorithm).
- `Task2_download_data.py`: Data extraction script to fetch the Surabaya street network and export `surabaya_map.json`.
- `surabaya_map.json`: Pre-processed JSON dataset containing street nodes, weighted directed edges, and street names.

## How to Run

### 1. Data Setup
Rebuilding the map dataset is optional, as `surabaya_map.json` is already bundled in the repository.

To regenerate the network dataset from OpenStreetMap, execute:
```bash
python Task2_download_data.py
```

### 2. Launch the Application
Start the simulator using Streamlit:
```bash
streamlit run Task2_Chinese_Postman.py
```
The interface will automatically open in your default browser at `http://localhost:8501`.

## How to Use the Simulator

1. **Set the DLH Depot location:** Enter precise latitude and longitude values in the menu panel or click anywhere directly on the map.
2. **Adjust collection radius:** Use the slider control to set the coverage radius in kilometers.
3. **Compute the route:** Click "Generate collection route" to solve the Chinese Postman Problem for the selected zone.
4. **Review outputs:** The application draws the full Eulerian circuit on the map, enumerates the ordered sequence of traversed streets, and computes key operational metrics (total distance, estimated collection time, and execution runtime).
