import csv
import json
from datetime import datetime
import constants

def csv_to_json(file_path):
    summary = {}

    # Read the CSV file
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        
        for row in reader:
            # Extract relevant data
            valid_id = row['validScientificNameId']
            date_time = row['dateTimeCollected']
            municipality = row['municipality']
            county = row['county']
            lakes = row['lake']
            rivers = row['river']
            river_nets = row['riverNet']
            lake_centroid = row['lake_centroid']
            river_centroid = row['river_centroid']
            rivernet_centroid = row['riverNet_centroid']

            # Convert datetime to UNIX epoch with error handling
            try:
                timestamp = int(datetime.strptime(date_time, "%d.%m.%Y %H:%M:%S").timestamp())
            except (ValueError, TypeError):
                print(f"Skipping invalid date: {date_time} in row {row}")
                continue

            # Function to update data in summary
            def update_summary(category, name, position):
                if name not in summary.get(category, {}):
                    summary.setdefault(category, {})[name] = {
                        "fish_ids": {},
                        "connected_counties": set(),
                        "connected_municipalities": set(),
                        "position": position  # Store position
                    }
                
                entry = summary[category][name]
                
                if valid_id not in entry["fish_ids"]:
                    entry["fish_ids"][valid_id] = {
                        "count": 1,
                        "latest_timestamp": timestamp
                    }
                else:
                    # Update count and latest timestamp
                    entry["fish_ids"][valid_id]["count"] += 1
                    entry["fish_ids"][valid_id]["latest_timestamp"] = max(
                        entry["fish_ids"][valid_id]["latest_timestamp"], timestamp
                    )
                
                # Add county and municipality
                entry["connected_counties"].add(county)
                entry["connected_municipalities"].add(municipality)

            # Update lakes with position
            if lakes:
                update_summary("lakes", lakes, lake_centroid)

            # Update rivers with position
            if rivers:
                update_summary("rivers", rivers, river_centroid)

            # Handle river_nets with position
            if river_nets:
                # Check if the riverNet matches an existing river (case-insensitive)
                matching_river = next(
                    (name for name in summary.get("rivers", {}) if name.lower() == river_nets.lower()),
                    None
                )
                if matching_river:
                    # Merge riverNet into the existing river
                    update_summary("rivers", matching_river, river_centroid)
                else:
                    # Treat as a separate entry in river_nets
                    update_summary("river_nets", river_nets, rivernet_centroid)
    
    # Convert sets to lists and cleanup
    for category in summary:
        for name in summary[category]:
            summary[category][name]["connected_counties"] = list(summary[category][name]["connected_counties"])
            summary[category][name]["connected_municipalities"] = list(summary[category][name]["connected_municipalities"])
    
    return summary

# Generate summary
summary = csv_to_json(constants.FishData.fish_with_waterbody_data_path)

# Save to JSON
with open('summary.json', 'w', encoding='utf-8') as json_file:
    json.dump(summary, json_file, ensure_ascii=False, indent=4)

print("Summary saved to summary.json")
