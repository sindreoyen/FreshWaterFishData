import os

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
    fish_with_waterbody_data_path = os.path.join("./", "extractedData", 'fish_with_waterbody.csv')

    # Init
    def __init__(self):
        print(f"Fish data path: {self.fish_data_path}")