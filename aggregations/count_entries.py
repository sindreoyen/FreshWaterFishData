import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import constants
import json

lake_data_path = constants.AggregateData.aggregated_lake_data
river_data_path = constants.AggregateData.aggregated_river_data

# Count entries in the lake data
with open(lake_data_path, "r", encoding="utf-8") as file:
    lake_data = json.load(file)
    lake_count = sum(len(region_data) for region_data in lake_data)

# Count entries in the river data
with open(river_data_path, "r", encoding="utf-8") as file:
    river_data = json.load(file)
    river_count = sum(len(region_data) for region_data in river_data)

print(f"Total entries in lake data: {lake_count}")

print(f"Total entries in river data: {river_count}")