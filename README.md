# 🗺️ Drive Time Polygon Mapper

Generate drive-time polygons (isochrones) for any address and visualize them on Google Maps. Perfect for analyzing service areas, delivery zones, commute times, and market reach.

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)

## 📋 What This Does

This tool calculates **how far you can drive from any address in a given time** and creates map-ready polygon data. It can also exclude specific ZIP codes from the result (e.g., exclude downtown areas from suburban analysis).

## ✨ Features

- 🎯 **Interactive CLI** - No code editing required, just answer prompts
- 🚗 **Driving isochrones** - Calculate reachable areas by drive time
- 🗺️ **Multiple output formats** - GeoJSON and Google Maps-ready JSON
- 🚫 **ZIP exclusion** - Easily exclude specific areas
- 📊 **Geometry simplification** - Optimized for web mapping
- 🆓 **Free APIs** - Uses free OpenRouteService API

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed ([Download](https://www.python.org/downloads/))
2. **OpenRouteService API key** (free) - [Sign up here](https://openrouteservice.org/dev/#/signup)
3. **ZCTA Shapefile** from US Census (only if excluding ZIP codes)

### Installation

1. **Download this repository** or clone it:
   ```bash
   git clone <repository-url>
   cd drive-time-polygon-mapper
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download ZCTA data** (only if excluding ZIP codes):
   - Visit [US Census TIGER/Line Files](https://www.census.gov/cgi-bin/geo/shapefiles/index.php)
   - Select **Year: 2024** (or latest)
   - Select **Layer Type: ZIP Code Tabulation Areas**
   - Click **Download** and extract all files to the `data` folder

### Usage

#### Step 1: Fetch Isochrone Data

Run the first script and follow the prompts:

```bash
python fetch_isochrone.py
```

You'll be asked for:
- **API Key** - Your OpenRouteService API key
- **Address** - Where to calculate from (e.g., "123 Main St, Chicago, IL")
- **Time** - How many minutes to calculate (e.g., 30, 45, 60)

**Output:** Creates `isochrone.geojson`

#### Step 2: Process Isochrone

Run the second script to exclude areas and optimize for Google Maps:

```bash
python process_isochrone.py
```

You'll be asked for:
- **Shapefile path** - Location of ZCTA shapefile (default: `data/tl_2024_us_zcta520.shp`)
- **Simplification** - Tolerance for reducing vertices (default: 0.0005)

**Output:** Creates:
- `isochrone_processed.geojson` - Standard GeoJSON
- `isochrone_gmaps.json` - Google Maps format

## 📁 File Structure

```
drive-time-polygon-mapper/
├── fetch_isochrone.py          # Step 1: Fetch isochrone from API
├── process_isochrone.py        # Step 2: Process and export
├── requirements.txt            # Python dependencies
├── example_map.html            # Interactive map viewer
├── README.md                   # This file
├── data/
│   ├── exclude_zips.txt        # ZIP codes to exclude
│   └── tl_2024_us_zcta520.shp  # ZCTA shapefile (you download this)
└── [output files created by scripts]
```

## 🎨 Viewing Your Results

### Option 1: Example HTML Viewer

1. Open `example_map.html` in a text editor
2. Replace `YOUR_GOOGLE_MAPS_API_KEY` with your [Google Maps API key](https://developers.google.com/maps/documentation/javascript/get-api-key)
3. Open the HTML file in a web browser

### Option 2: Use in Your Own App

#### Google Maps JavaScript API

```javascript
// Load the polygon data
fetch('isochrone_gmaps.json')
  .then(r => r.json())
  .then(data => {
    const map = new google.maps.Map(document.getElementById('map'), {
      center: { lat: 41.6, lng: -87.9 },
      zoom: 10
    });

    // Draw each polygon
    data.polygons.forEach(poly => {
      new google.maps.Polygon({
        map: map,
        paths: poly.paths,
        strokeColor: '#FF0000',
        strokeWeight: 2,
        fillColor: '#FF0000',
        fillOpacity: 0.25
      });
    });
  });
```

#### Using GeoJSON Format

Most mapping libraries support GeoJSON directly:

```javascript
// Leaflet, Mapbox, etc.
map.data.addGeoJson('isochrone_processed.geojson');
```

## ⚙️ Configuration

### Excluding ZIP Codes

Edit `data/exclude_zips.txt` to customize which ZIP codes to exclude:

```
# Add ZIP codes to exclude (one per line or comma-separated)
60601, 60602, 60603
60604
60605 60606 60607
```

**Common use cases:**
- Exclude downtown/city center from suburban analysis
- Exclude high-cost areas
- Exclude competitor territories
- Exclude restricted zones

### Simplification Tolerance

Reduce file size and vertex count by adjusting simplification when prompted:
- `0` - No simplification (highest accuracy, largest file)
- `0.0001` - Minimal simplification (~10m)
- `0.0005` - Recommended (~50m)
- `0.001` - Aggressive (~100m)

## 🔧 Troubleshooting

### "Could not find ZCTA code field"
- Make sure you downloaded the ZCTA shapefile, not a different Census boundary
- Ensure all shapefile files (.shp, .shx, .dbf, .prj) are in the same folder

### "API Error: 401"
- Check that your OpenRouteService API key is correct
- Verify your key is active at [openrouteservice.org](https://openrouteservice.org/dev/#/home)

### "Could not geocode address"
- Try a more complete address with city and state
- Use a well-known landmark or intersection
- Check for typos

### "No matching ZIP polygons found"
- Verify ZIP codes in `exclude_zips.txt` are correct
- Check that the ZCTA shapefile year matches current ZIP codes
- Some ZIPs may not have geographic boundaries (P.O. boxes)

### Python/pip Not Found
- Windows: Make sure Python is added to PATH during installation
- Run: `python --version` to verify installation
- Use `python3` and `pip3` instead of `python` and `pip` on some systems

## 📊 API Limits

**OpenRouteService (Free Tier):**
- 40 requests per minute
- 2,000 requests per day
- Results are cached in `isochrone.geojson` so you can re-run processing without re-fetching

**Nominatim Geocoding:**
- 1 request per second
- Be respectful of the service

## 🤝 Contributing

Found a bug or have a feature request? Please open an issue!

## 📄 License

MIT License - Feel free to use this for personal or commercial projects.

## 🙏 Credits

- [OpenRouteService](https://openrouteservice.org/) - Isochrone API
- [OpenStreetMap](https://www.openstreetmap.org/) - Geocoding
- [US Census Bureau](https://www.census.gov/) - ZIP code boundaries
- Built with [GeoPandas](https://geopandas.org/) and [Shapely](https://shapely.readthedocs.io/)

## 📚 Additional Resources

- [OpenRouteService Documentation](https://openrouteservice.org/dev/#/api-docs)
- [Google Maps API Documentation](https://developers.google.com/maps/documentation/javascript)
- [GeoJSON Specification](https://geojson.org/)
- [TIGER/Line Shapefiles Guide](https://www.census.gov/programs-surveys/geography/technical-documentation/complete-technical-documentation/tiger-geo-line.html)

---

**Questions?** Check the [Troubleshooting](#-troubleshooting) section or open an issue.
