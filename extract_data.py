import constants
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# Define the path to the original and new CSV files
fish_csv = constants.FishData.reduced_fish_data_path

# Load lake and river data
print("Reading lake data...")
lake_gdf = gpd.read_file(constants.RiverLakeData.lake_data_path)
# Add the centroid of each lake as a new column
lake_gdf['centroid'] = lake_gdf.centroid

print("Reading river data...")
river_gdf = gpd.read_file(constants.RiverLakeData.mainRiver_data_path)
# Add the centroid of each river as a new column
river_gdf['centroid'] = river_gdf.centroid

print("Reading riverNet data...")
riverNet_gdf = gpd.read_file(constants.RiverLakeData.riverNet_data_path)
# Add midpoint of each river as a new column
riverNet_gdf['centroid'] = riverNet_gdf.centroid

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

# Spatial join: Check if fish points are near rivers (buffer distance may vary)
print("Performing spatial join to check if fish points are near rivers...")
buffer_distance = 50  # Distance in meters; adjust as needed
river_gdf['geometry'] = river_gdf.geometry.buffer(distance=buffer_distance, cap_style="flat")  # Buffer river lines
riverNet_gdf['geometry'] = riverNet_gdf.geometry.buffer(distance=buffer_distance, cap_style="flat")  # Buffer river lines
fish_in_riverNets = gpd.sjoin(fish_gdf, riverNet_gdf, predicate='within', how='left')
fish_in_rivers = gpd.sjoin(fish_gdf, river_gdf, predicate='within', how='left')

# Merge lake results
print("Merging lake results...")
fish_in_lakes['lake'] = fish_in_lakes.apply(
    lambda row: (row["navn"] if row["navn"] is not None else row['elvenavnHierarki']) 
    if pd.notna(row['index_right']) else None, 
    axis=1
)
fish_in_lakes['lake_centroid'] = fish_in_lakes.apply(
    lambda row: row['centroid'] if pd.notna(row['index_right']) else None, 
    axis=1
)

# Merge river results
print("Merging river results...")
fish_in_rivers['river'] = fish_in_rivers.apply(
    lambda row: row['elvenavn'] if pd.notna(row['index_right']) else None, 
    axis=1
)
fish_in_rivers['river_centroid'] = fish_in_rivers.apply(
    lambda row: row['centroid'] if pd.notna(row['index_right']) else None, 
    axis=1
)

# Merge riverNet results
print("Merging riverNet results...")
fish_in_riverNets['riverNet'] = fish_in_riverNets.apply(
    lambda row: (row["elvenavn"] if row["elvenavn"] is not None else row['elvNavnHierarki']) 
    if pd.notna(row['index_right']) else None, 
    axis=1
)
fish_in_riverNets['riverNet_centroid'] = fish_in_riverNets.apply(
    lambda row: row['centroid'] if pd.notna(row['index_right']) else None, 
    axis=1
)

# Remove duplicate results by keeping the first occurrence
print("Removing duplicate river results...")
fish_in_rivers_unique = fish_in_rivers.loc[~fish_in_rivers.index.duplicated(keep='first')]
fish_in_riverNets_unique = fish_in_riverNets.loc[~fish_in_riverNets.index.duplicated(keep='first')]

# Combine results into the original fish data
print("Combining results into fish data...")
fish_data['lake'] = fish_in_lakes['lake']
fish_data['river'] = fish_in_rivers_unique['river']
fish_data['riverNet'] = fish_in_riverNets_unique['riverNet']
fish_data['lake_centroid'] = fish_in_lakes['lake_centroid']
fish_data['river_centroid'] = fish_in_rivers_unique['river_centroid']
fish_data['riverNet_centroid'] = fish_in_riverNets_unique['riverNet_centroid']

# Remove rows that have no waterbody information
print("Filtering out rows with no waterbody information...")
fish_data = fish_data.dropna(subset=['lake', 'river', 'riverNet'], how='all')

# Save results
print("Saving results to CSV...")
fish_data.to_csv(constants.FishData.fish_with_waterbody_data_path, index=False)

# Display final results
print("Final results:")
print(fish_data[['validScientificNameId', 'municipality', 'county', 'lake', 'river']])
