# SPPG mealbox delivery simulator - Task 1

This application simulates mealbox delivery routes from an SPPG center to nearby schools in Surabaya using OpenStreetMap data and graph algorithms.

## Prerequisites

Make sure you have Python 3.9+ installed.

## Prerequisites

Make sure you have Python 3.9+ installed.

First, navigate to the `task1` directory:
```bash
cd task1
```

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

> **Important :** Ensure your terminal is positioned inside the `task1/` directory before running any commands.
> ```bash
> cd task1
> ```

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