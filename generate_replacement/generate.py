import os
import pandas as pd
import fileinput 
import shutil

basepath = os.path.dirname(__file__)
dir_name = os.path.join(basepath, "temp")
source_file = os.path.join(basepath, "source.xlsx")
output_file = os.path.join(basepath, "..", "replacements.csv")

# Ensure temp folder exists
if not os.path.exists(dir_name):
    os.makedirs(dir_name)

# Create CSV files
all_sheets = pd.read_excel(source_file, sheet_name=None)
sheets = all_sheets.keys()

for sheet_name in sheets:
  sheet = pd.read_excel(source_file, sheet_name=sheet_name)
  sheet.to_csv(dir_name + ("/%s.csv" % sheet_name), index=False)

# Concatenate
csv_files = os.listdir(dir_name)
csv_files = list(map(lambda e: os.path.join(dir_name, e), csv_files))
with open(output_file, 'w') as outfile:
  for line in fileinput.input(files=csv_files):
    outfile.write(line)

# Delete temp folder
shutil.rmtree(dir_name)

