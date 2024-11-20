import json
import csv
from collections import defaultdict
from datetime import datetime
import constants

# File paths
input_json_path = constants.WaterBodyData.waterbody_json
input_csv_path = constants.FishData.fish_with_lake_data_path
output_json_path = constants.AggregateData.aggregated_lake_data

def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def load_csv(file_path):
    """Load CSV data into a list of dictionaries."""
    with open(file_path, "r", encoding="utf-8") as file:
        return list(csv.DictReader(file))

def convert_to_unix_epoch(date_str, date_format="%d.%m.%Y %H:%M:%S"):
    """Convert a date string to UNIX epoch timestamp."""
    try:
        dt = datetime.strptime(date_str, date_format)
        return int(dt.timestamp())
    except ValueError:
        return None


def process_data(json_data, fish_data):
    """Process JSON and CSV data to create the rivers dataset."""
    lakes_data = {}

    fish_stats = defaultdict(lambda: defaultdict(lambda: {"count": 0, "last_caught": 0}))
    counties = defaultdict(set)
    municipalities = defaultdict(set)

    def handle(fish):
        waterbody = fish["waterbody"]
        species_id = fish["validScientificNameId"]
        date_caught = convert_to_unix_epoch(fish["dateTimeCollected"])
        county = fish["county"].strip() if fish["county"] else None
        municipality = fish["municipality"].strip() if fish["municipality"] else None

        # Update fish statistics
        fish_stats[waterbody][species_id]["species_id"] = species_id
        fish_stats[waterbody][species_id]["count"] += 1
        if date_caught and date_caught > fish_stats[waterbody][species_id]["last_caught"]:
            fish_stats[waterbody][species_id]["last_caught"] = date_caught

        # Track counties and municipalities
        if county:
            counties[waterbody].add(county)
        if municipality:
            municipalities[waterbody].add(municipality)

    for fish in fish_data: handle(fish)

    for region_id, region_data in json_data.items():
        lakes = region_data.get("lake", [])
        for lake in lakes:
            name = lake.get("navn", "unknown")
            key = str(lake.get("vatnLnr", "unknown")) + ".0"
            if key is None:
                print(f"Skipping lake with no key: {name}")
                continue

            # Retrieve fish statistics and locations
            lake_fish_stats = fish_stats.get(key, {})
            lake_counties = sorted(counties.get(key, []))
            lake_municipalities = sorted(municipalities.get(key, []))

            # Enrich river data
            lakes_data[key] = {
                "name": name,
                "area_km2": lake.get("arealInnsjo_km2", 0),
                "positionEuref89Utm33": lake.get("positionEuref89Utm33", []),
                "positionWgs84": lake.get("positionWgs84", []),
                "hoyde_moh": lake.get("hoyde_moh", None),
                "elvenavnHierarki": lake.get("elvenavnHierarki", None),
                "fish_species_count": len(lake_fish_stats),
                "fish_data": lake_fish_stats,
                "counties": lake_counties,
                "municipalities": lake_municipalities,
            }

    # Remove rivers with no fish data
    lakes_data = {key: value for key, value in lakes_data.items() if value["fish_species_count"] > 0}
    
    return lakes_data

def save_json(data, file_path):
    """Save data to a JSON file."""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def main():
    # Load data
    json_data = load_json(input_json_path)
    fish_data = load_csv(input_csv_path)

    # Process data
    lakes = list(process_data(json_data, fish_data).values())

    # Save processed data
    save_json(lakes, output_json_path)
    print(f"Processed data saved to {output_json_path}")

if __name__ == "__main__":
    main()
