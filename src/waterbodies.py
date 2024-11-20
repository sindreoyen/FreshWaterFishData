import geopandas as gpd
import json
from collections import defaultdict
import constants

# Function to calculate the position based on geometry
def calculate_position(geometry):
    if geometry.geom_type == 'Polygon':
        return geometry.centroid
    elif geometry.geom_type == 'LineString':
        return geometry.interpolate(0.5, normalized=True)  # Midpoint for line
    elif geometry.geom_type == 'Point':
        return geometry
    elif geometry.geom_type == 'MultiPolygon':
        return geometry.centroid
    elif geometry.geom_type == 'MultiLineString':
        return geometry.interpolate(0.5, normalized=True)
    print(f"Unknown geometry type: {geometry.geom_type}")
    return None

# Read the river, lake, and rivernet data
print("Reading river data...")
river_gdf = gpd.read_file(constants.RiverLakeData.mainRiver_data_path)
print("Reading lake data...")
lake_gdf = gpd.read_file(constants.RiverLakeData.lake_data_path)

# Initialize a dictionary to store the results indexed by "nedborfeltVassdragNr" or "vassdragsnummer"
data = defaultdict(lambda: {'lake': [], 'river': []})

# Process river features
def add_data(gdf, category: str, removeColumns: list = []):
    # Calculate positions for each feature
    gdf['positionEuref89Utm33'] = gdf.geometry.apply(calculate_position)
    # convert from EUREF89 UTM zone 33 (epsg: 25833) to WGS84 (epsg: 4326)
    gdf = gdf.to_crs(epsg=4326)
    gdf['positionWgs84'] = gdf.geometry.apply(calculate_position)
    # Drop columns that are not needed
    #gdf = gdf.drop(columns=removeColumns)
    for _, row in gdf.iterrows():
        if row['objektType'] not in ['ElvBekk', 'Innsjø', 'InnsjøRegulert', 'Sideelv' 'Hovedelv i kystfelt', 'Hovedelv i vassOmr']:
            continue
        nedborfelt_vassdrag_nr = row['nedborfeltVassdragNr'] if ('nedborfeltVassdragNr' in row and row['nedborfeltVassdragNr'] is not None) else row['vassdragsnummer']
        position = row['positionWgs84']
        position_euref = row['positionEuref89Utm33']
        
        # Ensure position is serializable (convert Point to a list/tuple)
        position_serializable = (position.x, position.y)
        position_euref_serializable = (position_euref.x, position_euref.y)
        
        # Remove objektType from the row
        row = row.drop(removeColumns)

        if nedborfelt_vassdrag_nr:
            # Add position to the row dictionary and store it
            row_dict = row.dropna().to_dict()  # Convert the row to a dictionary
            row_dict['positionWgs84'] = position_serializable
            row_dict['positionEuref89Utm33'] = position_euref_serializable
            data[nedborfelt_vassdrag_nr][category].append(row_dict)

# Add data for rivers, lakes, and rivernets
print("Adding river data...")
add_data(river_gdf, 'river', 
         removeColumns=['geometry', 'objektType', 'nedborfeltVassdragNr', 
                        'nivaa', 'vassdragsomrade', 'dataUttaksdato', 'eksportType'])
print("Adding lake data...")
add_data(lake_gdf, 'lake', 
         removeColumns=['geometry', 'objektType', 'vassdragsnummer', 'vassdragsomradeNr',
                        'land1', 'arealNorge_km2', 'arealNedborfelt_km2', 'dataUttaksdato', 'eksportType'])

# Convert the result to JSON with proper character encoding
# Set indent=4 for pretty-printing, ensure_ascii=False to keep the original characters
# The reason for using no indentation is to reduce the file size
indent = False
output_json = json.dumps(data, indent=4 if indent else None, ensure_ascii=False)

# Save the result to a file
with open(constants.WaterBodyData.waterbody_json, 'w') as f:
    f.write(output_json)
