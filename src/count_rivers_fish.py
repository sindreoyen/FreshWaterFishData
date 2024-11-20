import json
import csv
from collections import defaultdict
from datetime import datetime
import constants
from utils import normalize_key

# File paths
input_json_path = constants.WaterBodyData.waterbody_json
input_csv_path = constants.FishData.fish_with_river_data_path
rivernets_data_path = constants.FishData.fish_with_riverNet_data_path
output_json_path = constants.AggregateData.aggregated_river_data

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
    rivers = {}

    fish_stats = defaultdict(lambda: defaultdict(lambda: {"count": 0, "last_caught": 0}))
    river_counties = defaultdict(set)
    river_municipalities = defaultdict(set)

    fish_rivernets_data = load_csv(rivernets_data_path)
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
            river_counties[waterbody].add(county)
        if municipality:
            river_municipalities[waterbody].add(municipality)

    for fish in fish_data: handle(fish)
    for fish in fish_rivernets_data: handle(fish)

    for region_id, region_data in json_data.items():
        river_data = region_data.get("river", [])
        for river in river_data:
            river_name = river.get("elvenavn", "Unknown River")
            key = normalize_key(river_name, region_id)
            if key is None:
                continue

            # Retrieve fish statistics and locations
            river_fish_stats = fish_stats.get(key, {})
            counties = sorted(river_counties.get(key, []))
            municipalities = sorted(river_municipalities.get(key, []))

            # Enrich river data
            rivers[key] = {
                "name": river.get("elvenavn", "Unknown River"),
                "length_meters": river.get("elvelengde", 0),
                "position": river.get("position", []),
                "fish_species_count": len(river_fish_stats),
                "fish_data": river_fish_stats,
                "counties": counties,
                "municipalities": municipalities,
            }

    # Remove rivers with no fish data
    rivers = {key: value for key, value in rivers.items() if value["fish_species_count"] > 0}

    return rivers

def save_json(data, file_path):
    """Save data to a JSON file."""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def main():
    # Load data
    json_data = load_json(input_json_path)
    fish_data = load_csv(input_csv_path)

    # Process data
    rivers = process_data(json_data, fish_data)

    # Save processed data
    save_json(rivers, output_json_path)
    print(f"Processed data saved to {output_json_path}")

if __name__ == "__main__":
    main()
