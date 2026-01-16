import folium
import pandas as pd
import geopandas as gpd
import requests
import osmnx as ox
import numpy as np
from folium.plugins import MarkerCluster

# --- CONFIGURATION ---
# Replace this with your key once active
CENSUS_API_KEY = "YOUR_API_KEY_HERE"

cities = [
    "Fayetteville, Arkansas, USA", 
    "Springdale, Arkansas, USA", 
    "Rogers, Arkansas, USA", 
    "Bentonville, Arkansas, USA"
]

project_name = "NWA_Retail_Opportunity_Map"
print(f"--- 🚀 Starting {project_name} ---")

# --- STEP 1: SUPPLY (Get the Coffee Shops) ---
print("1. Fetching Coffee Shop Locations (Supply)...")
tags = {"amenity": "cafe"}
all_cafes = pd.DataFrame()

for city in cities:
    try:
        # Fetch data
        cafes = ox.features_from_place(city, tags=tags)
        if not cafes.empty:
            # Clean and normalize
            cafes = cafes[['name', 'geometry']].copy()
            cafes['city'] = city.split(",")[0]
            # Handle polygons (buildings) vs points
            cafes['lat'] = cafes.geometry.apply(lambda x: x.centroid.y if x.geom_type == 'Polygon' else x.y)
            cafes['lon'] = cafes.geometry.apply(lambda x: x.centroid.x if x.geom_type == 'Polygon' else x.x)
            all_cafes = pd.concat([all_cafes, cafes])
    except Exception as e:
        print(f"   Note: Could not fetch for {city}")

print(f"   > Found {len(all_cafes)} cafes in NWA.")

# --- STEP 2: FLOW (Calculate Commuter Access) ---
print("2. Calculating Commuter Access (Flow)...")

# Download just the highway network (fast)
G_highway = ox.graph_from_place(cities, custom_filter='["highway"~"motorway|motorway_link"]', simplify=True)
gdf_nodes = ox.graph_to_gdfs(G_highway, nodes=True, edges=False)

# Find nearest highway node for every cafe
nearest_nodes = ox.nearest_nodes(G_highway, X=all_cafes['lon'].values, Y=all_cafes['lat'].values)

# Manual Haversine Distance Function
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000 # Earth radius (meters)
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

# Calculate distances
distances = []
for i, node_id in enumerate(nearest_nodes):
    dist = haversine(
        all_cafes.iloc[i]['lat'], all_cafes.iloc[i]['lon'], 
        gdf_nodes.loc[node_id].y, gdf_nodes.loc[node_id].x
    )
    distances.append(dist)

all_cafes['dist_to_hwy'] = distances
print("   > Commuter metrics calculated.")

# --- STEP 3: DEMAND (Fetch Census Income) ---
print("3. Fetching Census Income Data (Demand)...")
state_code, county_codes = "05", "007,143" # AR, Benton & Washington
variable = "B19013_001E" # Median Household Income

url = f"https://api.census.gov/data/2021/acs/acs5?get=NAME,{variable}&for=tract:*&in=state:{state_code}&in=county:{county_codes}&key={CENSUS_API_KEY}"

try:
    response = requests.get(url)
    response.raise_for_status() # Check for HTTP errors
    
    # Process JSON
    data = response.json()
    df_census = pd.DataFrame(data[1:], columns=data[0])
    df_census = df_census.rename(columns={variable: "income", "tract": "TRACTCE"})
    df_census["income"] = pd.to_numeric(df_census["income"], errors="coerce")
    df_census = df_census[df_census["income"] > 0] # Remove invalid/negative incomes

    # Download Shapes
    shape_url = "https://www2.census.gov/geo/tiger/TIGER2021/TRACT/tl_2021_05_tract.zip"
    gdf_tracts = gpd.read_file(shape_url)
    gdf_tracts = gdf_tracts[gdf_tracts["COUNTYFP"].isin(["007", "143"])]
    
    # Merge Shapes with Data
    gdf_final = gdf_tracts.merge(df_census, on="TRACTCE", how="inner")
    print(f"   > Census data merged for {len(gdf_final)} tracts.")

    # --- STEP 4: VISUALIZATION ---
    print("4. Building Final Map...")
    m = folium.Map(location=[36.18, -94.14], zoom_start=11, tiles="CartoDB positron")

    # Layer A: Income Choropleth (Green = Wealth)
    folium.Choropleth(
        geo_data=gdf_final,
        data=gdf_final,
        columns=["TRACTCE", "income"],
        key_on="feature.properties.TRACTCE",
        fill_color="YlGn", 
        fill_opacity=0.6,
        line_opacity=0.1,
        legend_name="Median Household Income ($)",
        name="Income Layer"
    ).add_to(m)

    # Layer B: Cafe Clusters (Red = Commuter, Blue = Destination)
    marker_cluster = MarkerCluster(name="Coffee Shops").add_to(m)
    
    for idx, row in all_cafes.iterrows():
        # Classification Logic
        if row['dist_to_hwy'] < 600:
            category = "Commuter Hub"
            color = "red"
            icon = "car"
        elif row['dist_to_hwy'] < 2000:
            category = "Neighborhood Cafe"
            color = "orange"
            icon = "home"
        else:
            category = "Destination/Study"
            color = "blue" 
            icon = "book"
            
        popup_text = f"""
        <b>{row['name']}</b><br>
        Type: {category}<br>
        Dist to Hwy: {int(row['dist_to_hwy'])}m
        """
        
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=popup_text,
            icon=folium.Icon(color=color, icon=icon, prefix="fa")
        ).add_to(marker_cluster)

    folium.LayerControl().add_to(m)
    output_file = "NWA_Final_Analysis.html"
    m.save(output_file)
    print(f"✅ SUCCESS! Map saved to {output_file}")

except Exception as e:
    print("❌ ERROR: The Census API is likely still activating.")
    print(f"   Details: {e}")