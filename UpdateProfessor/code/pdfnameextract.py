import re
import os
import pandas as pd
from collections import defaultdict

def extract_name_and_date_from_filename(filename):
    # Regular expression to extract the name and date from the filename
    match = re.match(r"(.+?)\s*(\w+\s+\d{4}|\w+\s+\d{1,2},\s*\d{4})", filename)
    if match:
        name = match.group(1).replace('_', ' ').replace('.', ' ').strip()
        date = match.group(2).strip()
        # Split the name and reverse the order
        name_parts = name.split(',')
        if len(name_parts) == 2:
            name = f"{name_parts[1].strip()} {name_parts[0].strip()}"
        return name, date
    return "Name not found", "Ending term not found"

def get_latest_pdf(files):
    latest_file = None
    latest_date = None
    date_pattern = re.compile(r"(\w+ \d{4})|(\w+ \d{1,2}, \d{4})")

    for file in files:
        match = date_pattern.search(file)
        if match:
            date_str = match.group(0)
            try:
                date = pd.to_datetime(date_str)
                if latest_date is None or date > latest_date:
                    latest_date = date
                    latest_file = file
            except ValueError:
                continue

    return latest_file

def process_pdfs_in_folder(folder_path):
    results = []
    grouped_files = defaultdict(list)

    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            name = re.split(r'[\s,_]', filename)[0]
            grouped_files[name].append(filename)

    for name, files in grouped_files.items():
        latest_file = get_latest_pdf(files)
        if latest_file:
            professor_name, ending_term = extract_name_and_date_from_filename(latest_file)
            results.append({
                "File": latest_file,
                "Professor Name": professor_name,
                "Ending Term": ending_term
            })

    return results

# Specify the folder path
folder_path = "UpdateProfessor/data/Biology"
results = process_pdfs_in_folder(folder_path)

# Create the resultCsv folder if it doesn't exist
result_folder = "UpdateProfessor/resultCsv"
os.makedirs(result_folder, exist_ok=True)

# Save results to a CSV file with the folder name as the file name inside the resultCsv folder
folder_name = os.path.basename(folder_path)
csv_file_name = os.path.join(result_folder, f"{folder_name}.csv")
df = pd.DataFrame(results)
df.to_csv(csv_file_name, index=False)

print(f"Results have been saved to {csv_file_name}")