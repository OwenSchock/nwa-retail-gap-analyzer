# nwa-retail-gap-analyzer
Geospatial analysis tool for retail site selection in Northwest Arkansas.
#  NWA Retail Gap Analyzer: A Spatial Intelligence Tool

[![View Interactive Map](https://img.shields.io/badge/View-Interactive%20Map-blue?style=for-the-badge)](https://owenschock.github.io/nwa-retail-gap-analyzer/NWA_Final_Analysis.html)

### *Optimizing site selection for retail expansion in Northwest Arkansas using Demographic & Network Analysis.*

![Project Banner](images/final_master_map.png)
*(Above: Final output showing the "Golden Quadrant" analysis—High Income Zones overlayed with Commuter Access data)*

---

##  Executive Summary
Business owners often rely on "gut feeling" or expensive consulting firms to decide where to open their next location. This project democratizes that process by building a **Spatial Decision Support System** for Northwest Arkansas (Fayetteville, Springdale, Rogers, Bentonville).

By ingesting data from the **US Census Bureau (ACS)** and **OpenStreetMap**, this tool identifies "Market Efficiency Gaps"—specific neighborhoods where high disposable income meets low service density.

##  Key Insights & Findings
* **The "Old Wealth" Gap (East Rogers):** Analysis identified a cluster of high-income Census tracts ($120k+ Median Household Income) east of I-49 with near-zero coffee shop density, presenting a prime opportunity for high-end "destination" retail.
* **The Commuter Wall (Centerton/Bentonville):** 80% of drive-thru chains are located within 600m of a highway interchange. The map reveals a sharp drop-off in service density at the Centerton city limit, despite high residential growth—signaling a "first-mover" advantage for commuter-focused chains.
* **Polycentric Gravity:** The model validated that NWA operates as two distinct retail morphologies:
    * *Fayetteville:* Success correlates with "Walkability" and "University Proximity" (Green dots > 2km from highway).
    * *Rogers/Bentonville:* Success correlates with "Commuter Flow" (Red dots < 600m from highway).

##  Tech Stack & Methodology
This project utilizes a pure Python geospatial stack:

* **Data Ingestion:** `requests` (US Census API), `osmnx` (OpenStreetMap extraction).
* **Geospatial Engineering:** `geopandas` for shapefile manipulation and coordinate reference system (CRS) transformations.
* **Network Analysis:** Calculated "Commuter Gravity" by computing the Haversine distance from every potential site to the nearest I-49 motorway link.
* **Visualization:** `folium` (Leaflet.js wrapper) for interactive, layered choropleth maps.

##  Repository Structure
```bash
├── nwa_retail_analyzer.py   # Main analysis script
├── requirements.txt         # Dependency list
├── README.md                # Project documentation
├── output/                  # Generated HTML maps
└── images/                  # Screenshots for documentation
