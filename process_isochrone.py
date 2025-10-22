"""
Interactive Isochrone Processor
Removes excluded ZIP code areas and exports GeoJSON and Google Maps-ready formats.
"""
import json
import sys
import os
import geopandas as gpd
from shapely.ops import unary_union
from shapely.geometry import Polygon, MultiPolygon

def load_excluded_zips(filepath: str) -> set:
    """Load ZIP codes to exclude from file."""
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found. No ZIPs will be excluded.")
        return set()
    
    zips = set()
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith("#"):
                # Handle comma-separated values
                for zip_code in line.replace(",", " ").split():
                    zip_code = zip_code.strip().strip('"').strip("'")
                    if zip_code:
                        zips.add(zip_code)
    
    return zips

def ring_to_latlng_list(coords):
    """Convert ring coordinates to Google Maps lat/lng format."""
    latlng = [{"lat": lat, "lng": lon} for lon, lat in coords]
    if len(latlng) >= 2 and latlng[0] == latlng[-1]:
        latlng = latlng[:-1]
    return latlng

def geom_to_paths(geom):
    """Convert geometry to Google Maps paths format."""
    if isinstance(geom, Polygon):
        rings = []
        rings.append(ring_to_latlng_list(list(geom.exterior.coords)))
        for interior in geom.interiors:
            rings.append(ring_to_latlng_list(list(interior.coords)))
        return rings
    elif isinstance(geom, MultiPolygon):
        all_polys = []
        for p in geom.geoms:
            all_polys.append(geom_to_paths(p))
        return all_polys
    else:
        return []

def main():
    """Main execution function with interactive prompts."""
    print("=" * 60)
    print("ISOCHRONE GENERATOR - Step 2: Process Isochrone")
    print("=" * 60)
    print()
    
    # Check for input file
    isochrone_file = "isochrone.geojson"
    if not os.path.exists(isochrone_file):
        print(f"✗ ERROR: {isochrone_file} not found.")
        print("Please run fetch_isochrone.py first.")
        sys.exit(1)
    
    # Prompt for ZCTA shapefile
    print("Enter path to ZCTA shapefile:")
    print("Example: data/tl_2024_us_zcta520.shp")
    default_path = "data/tl_2024_us_zcta520.shp"
    shapefile_path = input(f"[{default_path}]: ").strip() or default_path
    
    if not os.path.exists(shapefile_path):
        print(f"✗ ERROR: Shapefile not found: {shapefile_path}")
        print("\nDownload from: https://www.census.gov/cgi-bin/geo/shapefiles/index.php")
        print("Select: ZIP Code Tabulation Areas (ZCTA)")
        sys.exit(1)
    
    # Load excluded ZIPs
    exclude_file = "data/exclude_zips.txt"
    print()
    print(f"Loading excluded ZIP codes from: {exclude_file}")
    excluded_zips = load_excluded_zips(exclude_file)
    if excluded_zips:
        print(f"✓ Found {len(excluded_zips)} ZIP codes to exclude")
    else:
        print("No ZIP codes to exclude (proceeding with full isochrone)")
    
    # Prompt for simplification
    print()
    print("Geometry simplification reduces file size for Google Maps.")
    print("Recommended: 0.0005 (~50m tolerance)")
    simplify_input = input("Enter simplification tolerance [0.0005]: ").strip() or "0.0005"
    try:
        simplify_tolerance = float(simplify_input)
    except ValueError:
        print("Invalid number, using default 0.0005")
        simplify_tolerance = 0.0005
    
    print()
    print("-" * 60)
    print("Processing...")
    print()
    
    try:
        # Load isochrone
        print("Loading isochrone data...")
        iso = gpd.read_file(isochrone_file)
        iso = iso.set_crs(epsg=4326, allow_override=True).to_crs(epsg=4326)
        
        # Process exclusion if there are ZIPs to exclude
        if excluded_zips:
            print("Loading ZCTA shapefile...")
            zcta = gpd.read_file(shapefile_path).to_crs(epsg=4326)
            
            # Detect ZIP field
            zip_field_candidates = [c for c in ["ZCTA5CE20","ZCTA5CE10","ZCTA5CE"] if c in zcta.columns]
            if not zip_field_candidates:
                raise RuntimeError("Could not find ZCTA code field (ZCTA5CE20/ZCTA5CE10/ZCTA5CE).")
            zip_field = zip_field_candidates[0]
            print(f"✓ Using ZIP field: {zip_field}")
            
            # Filter to excluded ZIPs
            zcta_excluded = zcta[zcta[zip_field].isin(excluded_zips)].copy()
            if zcta_excluded.empty:
                print("Warning: No matching ZIP polygons found in shapefile.")
            else:
                print(f"✓ Found {len(zcta_excluded)} ZIP code areas to exclude")
                
                # Spatial pre-clip for performance
                minx, miny, maxx, maxy = iso.total_bounds
                zcta_excluded = zcta_excluded.cx[minx:maxx, miny:maxy]
                
                # Subtract excluded areas
                print("Subtracting excluded ZIP areas from isochrone...")
                mask = unary_union(zcta_excluded.geometry)
                iso["geometry"] = iso.geometry.apply(lambda g: g.difference(mask))
                
                # Clean empties/split multiparts
                iso = iso[iso.geometry.notnull() & (~iso.is_empty)]
                iso = iso.explode(index_parts=False).reset_index(drop=True)
        
        # Simplify geometry
        if simplify_tolerance > 0:
            print(f"Simplifying geometry (tolerance: {simplify_tolerance})...")
            iso["geometry"] = iso.geometry.simplify(simplify_tolerance, preserve_topology=True)
            iso = iso[iso.geometry.notnull() & (~iso.is_empty)].reset_index(drop=True)
        
        # Export GeoJSON
        geojson_out = "isochrone_processed.geojson"
        print(f"Writing GeoJSON to {geojson_out}...")
        iso.to_file(geojson_out, driver="GeoJSON")
        
        # Export Google Maps format
        print("Converting to Google Maps format...")
        gmaps_payload = {"polygons": []}
        
        for g in iso.geometry:
            if isinstance(g, MultiPolygon):
                for p in g.geoms:
                    gmaps_payload["polygons"].append({"paths": geom_to_paths(p)})
            elif isinstance(g, Polygon):
                gmaps_payload["polygons"].append({"paths": geom_to_paths(g)})
        
        gmaps_out = "isochrone_gmaps.json"
        with open(gmaps_out, "w", encoding="utf-8") as f:
            json.dump(gmaps_payload, f, ensure_ascii=False)
        
        print()
        print("=" * 60)
        print("✓ SUCCESS!")
        print(f"Output files:")
        print(f"  - {geojson_out} (standard GeoJSON)")
        print(f"  - {gmaps_out} (Google Maps format)")
        print(f"Total polygons: {len(gmaps_payload['polygons'])}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
