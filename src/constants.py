import os

class AggregateData:
    __path = os.path.join('./', 'aggregations')
    aggregated_lake_data = os.path.join(__path, 'aggregated_lake_data.json')
    aggregated_river_data = os.path.join(__path, 'aggregated_river_data.json')

class WaterBodyData:
    '''
    This class contains the paths to the waterbody data files.
    '''
    __waterbodies_data = os.path.join('./', 'extractedData', 'WaterBodies')
    waterbody_json = os.path.join(__waterbodies_data, 'aggregated_waterbodies.json')

    # Init
    def __init__(self):
        print(f"Waterbody data path: {self.waterbody_data_path}")

class RiverLakeData:
    '''
    This class contains the paths to the river and lake data files.
    '''
    __nve_data_folder = os.path.join('./', 'data', 'NVEKartData', 'NVEData')
    riverNet_data_path = os.path.join(__nve_data_folder, 'Elv_Elvenett.geojson')
    mainRiver_data_path = os.path.join(__nve_data_folder, 'Elv_Hovedelv.geojson')
    lake_data_path = os.path.join(__nve_data_folder, 'Innsjo_Innsjo.geojson')


    # Init
    def __init__(self):
        print(f"River data path: {self.river_data_path}")
        print(f"Lake data path: {self.lake_data_path}")

class FishData:
    '''
    This class contains the path to the fish data file.
    '''
    __fish_data_folder = os.path.join('./', 'data', 'ferskvann')
    fish_data_path = os.path.join(__fish_data_folder, 'fisk.csv')
    breed_data_path = os.path.join(__fish_data_folder, 'breed_data.csv')
    fish_extended_data_path = os.path.join(__fish_data_folder, 'fisk_extended.csv')
    reduced_fish_data_path = os.path.join(__fish_data_folder, 'reduced_fish_data.csv')

    fish_with_waterbody_data_path = os.path.join("./", "extractedData", 'WaterbodyData', 'fish_with_waterbody.csv')
    fish_with_lake_data_path = os.path.join("./", "extractedData", 'fish_with_lake.csv')
    fish_with_river_data_path = os.path.join("./", "extractedData", 'fish_with_river.csv')
    fish_with_riverNet_data_path = os.path.join("./", "extractedData", 'fish_with_riverNet.csv')

    # Init
    def __init__(self):
        print(f"Fish data path: {self.fish_data_path}")