# Coding Task - Group 9

## Member
Rida BINDECH / 5999261011

Emmanuel SANTINI / 5999261124

Calixte BERTHIER / 5999261123

# Task 1 : Traveling Salesman Problem

# SPPG mealbox delivery simulator

This application simulates mealbox delivery routes from an SPPG center to nearby schools in Surabaya using OpenStreetMap data and graph algorithms.

## Prerequisites

Make sure you have Python 3.9+ installed.

Install the required packages using:
```bash
pip install -r requirements.txt
```

The packages used are:
- `streamlit`: for the web interface.
- `folium` & `streamlit-folium`: to display the interactive map and handle user clicks.
- `requests`: to fetch data from the Overpass API.

## Project Files

- `app.py`: The Streamlit web application. Contains the UI, handles user input, and calls graph functions to compute and display the route.
- `graph_engine.py`: Contains the core algorithms (Dijkstra, Haversine distance, and the greedy TSP solver).
- `download_data.py`: Script used to fetch road and school data from OpenStreetMap.
- `data/surabaya_data.json`: The pre-processed dataset with road nodes, edges, and schools around Surabaya.

## How to Run

### 1. Data Setup
You do not need to download the data again. The dataset `data/surabaya_data.json` is already included in the repository.

If you ever need to rebuild the dataset, you can run:
```bash
python download_data.py
```

### 2. Launch the Application
Run the Streamlit app from your terminal:
```bash
streamlit run app.py
```

If your terminal says `streamlit: command not found`, run this instead:

```bash
python -m streamlit run app.py
```

Open your browser at `http://localhost:8501`.


## How to Use the Simulator

1. **Pick the SPPG location:** You can either type the coordinates manually in the right menu or simply click anywhere on the map.
2. **Set the radius:** Use the slider to choose the delivery radius in kilometers.
3. **Calculate the route:** Click the "Calculate TSP route" button.
4. **View results:** The app will draw the complete route on the road network, list the order of schools visited, and display the total distance, estimated delivery time, and calculation time.

# Task 2 : Chinese Postman Problem 

## Problem
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

# Task 3 : Knight's Tour 


## Problem
Given a rectangular board and a starting square, find a sequence of legal knight moves that visits **every square exactly once**. This is a Hamiltonian **path**, not necessarily a Hamiltonian cycle.

## Prerequisites
- Python 3.8 or newer
- No external libraries

## How to run
From this directory, run:

```bash
python knights_tour.py
```

Enter two lines: first `columns rows`, then `start_x start_y` (zero-based indexing):

```text
5 5
2 2
```

The program prints one `x y` coordinate per line. A complete tour has `columns * rows` lines and starts at the requested starting square.

If there is no complete tour, the output is exactly:

```text
path not found
```

An invalid or incomplete input instead produces `invalid input`. Positive dimensions and a starting coordinate within the board are required.

## Approach
1. Create a graph whose vertices are board squares `(x, y)`.
2. Add undirected edges for the eight legal knight moves, discarding out-of-bounds moves.
3. Apply quick necessary-condition checks: no isolated squares on a nontrivial board, at most two degree-one vertices (if there are two, the start must be one of them), valid start color for odd-sized boards, and graph connectivity.
4. Search using **depth-first search with backtracking**. Keep the current path and the set of visited squares. Never revisit a square.
5. Apply **Warnsdorff's rule** to order next moves: try the unvisited square with the fewest available onward moves first. This is a heuristic, not a proof that a tour exists.
6. If a choice fails, undo it and try the next one. Exhausting all choices means that no complete tour exists.

## Complexity
Let `N = columns * rows`.

- Building the graph takes `O(N)` time and `O(N)` space since each vertex has at most 8 neighbors.
- The graph checks take `O(N)` time.
- In the worst case, DFS backtracking explores exponentially many partial paths: a simple upper bound is `O(8^N)` time. Warnsdorff's rule generally reduces practical search but does not improve that worst-case guarantee.
- Graph, path, visited set, and recursion stack together use `O(N)` space.

## Sample cases

### Example 1: 5 x 5 from (2, 2)

Input:
```text
5 5
2 2
```

One valid output, interpreted as the **move order** placed on each square (rows have increasing `y`, columns increasing `x`):

```text
25 10 15  4 19
16  5 18  9 14
11 24  1 20  3
 6 17 22 13  8
23 12  7  2 21
```

The actual program outputs the coordinates in this order. The first move is `(2, 2)`, followed by `(3, 4)`, `(4, 2)`, etc.

### Example 2: 4 x 4 from (0, 0)

Input:
```text
4 4
0 0
```

Output:
```text
path not found
```

### Example 3: 1 x 1 from (0, 0)

Input:
```text
1 1
0 0
```

Output:
```text
0 0
```

## Tests
Run:
```bash
python -m unittest test_knights_tour.py
```

## AI usage disclosure
The assignment asks for honest disclosure of AI use and the prompt history. Document the assistance used to develop and test the algorithm, and attach the relevant prompt history as required by the course instructions.
