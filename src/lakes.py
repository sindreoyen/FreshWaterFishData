import constants
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from utils import normalize_key, calculate_midpoint

# Define the path to the original and new CSV files
fish_csv = constants.FishData.reduced_fish_data_path

# Load river data
print("Reading lake data...")
lake_gdf = gpd.read_file(constants.RiverLakeData.lake_data_path)
lake_gdf['centroid'] = lake_gdf.centroid

# Load fish data
print("Reading fish data...")
fish_data = pd.read_csv(fish_csv, delimiter=";")  # Adjust path and delimiter if necessary
# Convert coordinates to a geometry column in UTM zone 33 EUREF89 format
fish_data['geometry'] = fish_data.apply(lambda row: Point(row['east'], row['north']), axis=1)
fish_data = fish_data.drop(columns=['east', 'north']) # Drop original coordinate columns, as they are no longer needed
fish_gdf = gpd.GeoDataFrame(fish_data, geometry='geometry', crs=lake_gdf.crs)  # Ensure CRS matches lake data

# Spatial join: Check if fish points fall within lakes
print("Performing spatial join to check if fish points fall within lakes...")
fish_in_lakes = gpd.sjoin(fish_gdf, lake_gdf, predicate='within', how='left')

# Merge lake results
print("Merging lake results...")
fish_in_lakes['waterbody'] = fish_in_lakes.apply(
    lambda row: (normalize_key(str(row["vatnLnr"]),
                               row["vassdragsnummer"]))
    if pd.notna(row['index_right']) else None, 
    axis=1
)
fish_in_lakes['lake_name'] = fish_in_lakes.apply(
    lambda row: row['navn'] if pd.notna(row['index_right']) else None, 
    axis=1
)
fish_in_lakes['lake_centroid'] = fish_in_lakes.apply(
    lambda row: row['centroid'] if pd.notna(row['index_right']) else None, 
    axis=1
)

# Remove duplicates after spatial join
fish_in_lakes.drop(columns=['geometry'], inplace=True)

# Ensure indices align before assignment
fish_data["waterbody"] = fish_in_lakes["waterbody"]
fish_data["lake_name"] = fish_in_lakes["lake_name"]

# Remove rows that have no waterbody information
print("Filtering out rows with no lake information...")
fish_data = fish_data.dropna(subset=['waterbody'], how='all')

# Save results
print("Saving results to CSV...")
fish_data.to_csv(constants.FishData.fish_with_lake_data_path, index=False)
