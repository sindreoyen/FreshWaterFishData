import constants
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from utils import normalize_key, calculate_midpoint

# Define the path to the original and new CSV files
fish_csv = constants.FishData.reduced_fish_data_path

# Load river data
print("Reading river data...")
river_gdf = gpd.read_file(constants.RiverLakeData.riverNet_data_path)
river_gdf['centroid'] = river_gdf.geometry.apply(calculate_midpoint) # river_gdf.centroid

# Load fish data
print("Reading fish data...")
fish_data = pd.read_csv(fish_csv, delimiter=";")  # Adjust path and delimiter if necessary
# Convert coordinates to a geometry column in UTM zone 33 EUREF89 format
fish_data['geometry'] = fish_data.apply(lambda row: Point(row['east'], row['north']), axis=1)
fish_data = fish_data.drop(columns=['east', 'north']) # Drop original coordinate columns, as they are no longer needed
fish_gdf = gpd.GeoDataFrame(fish_data, geometry='geometry', crs=river_gdf.crs)  # Ensure CRS matches lake data

# Perform spatial join: Check if fish points are near rivers
print("Performing spatial join to check if fish points are near rivers...")
buffer_distance = 50  # Distance in meters; adjust as needed
river_gdf['geometry'] = river_gdf.geometry.buffer(distance=buffer_distance, cap_style="flat")  # Buffer river lines
fish_in_rivers = gpd.sjoin(fish_gdf, river_gdf, predicate='within', how='left')

# Merge lake results
print("Merging lake results...")
fish_in_rivers['waterbody'] = fish_in_rivers.apply(
    lambda row: (normalize_key(row["elvenavn"] if row["elvenavn"] is not None else row["elvNavnHierarki"],
                                 row["vassdragsnummer"]))
    if pd.notna(row['index_right']) else None, 
    axis=1
)

fish_in_rivers['river_centroid'] = fish_in_rivers.apply(
    lambda row: row['centroid'] if pd.notna(row['index_right']) else None, 
    axis=1
)


# Remove duplicates after spatial join
#fish_in_rivers = fish_in_rivers.drop_duplicates(subset=['geometry', 'index_right']).reset_index(drop=True)
fish_in_rivers_unique = fish_in_rivers.loc[~fish_in_rivers.index.duplicated(keep='first')]
fish_in_rivers_unique.drop(columns=['geometry'], inplace=True)

# Ensure indices align before assignment
fish_data["waterbody"] = fish_in_rivers_unique["waterbody"]

# Remove rows that have no waterbody information
print("Filtering out rows with no river information...")
fish_data = fish_data.dropna(subset=['waterbody'], how='all')

# Save results
print("Saving results to CSV...")
fish_data.to_csv(constants.FishData.fish_with_riverNet_data_path, index=False)
