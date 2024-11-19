import csv
import constants

input_csv = constants.FishData.fish_extended_data_path
output_csv = constants.FishData.reduced_fish_data_path

# List of column indices to keep
columns_to_keep = [5, 11, 14, 15, 23, 24]

# Read the input file and write only selected columns to the new file
with open(input_csv, 'r', newline='', encoding='utf-8') as infile, open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.reader(infile, delimiter=';')
    writer = csv.writer(outfile, delimiter=';')
    
    # Iterate through each row and keep only the specified columns
    for row in reader:
        filtered_row = [row[i - 1] for i in columns_to_keep]
        writer.writerow(filtered_row)

print("New CSV file created with selected columns.")
