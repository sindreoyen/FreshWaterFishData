import csv
import constants

input_csv = constants.FishData.fish_extended_data_path
output_csv = constants.FishData.breed_data_path

# List of column indices to keep
columns_to_keep = [5, 6, 7, 8, 59]

# Read the input file and write only selected columns to the new file
# removing duplicates
with open(input_csv, 'r', newline='', encoding='utf-8') as infile, open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.reader(infile, delimiter=';')
    writer = csv.writer(outfile, delimiter=';')
    written_rows = set()
    
    # Iterate through each row and keep only the specified columns
    for row in reader:
        filtered_row = [row[i - 1] for i in columns_to_keep]
        # Check if the row is not already in the output file
        if tuple(filtered_row) not in written_rows:
            writer.writerow(filtered_row)
            written_rows.add(tuple(filtered_row))


print("New CSV file created with selected columns.")
