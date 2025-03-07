import re
import os
import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta

# Function to correct common typos in month names
def correct_month_name(month_name):
    month_corrections = {
        "Novermber": "November",
        # Add other common typos if needed
    }
    return month_corrections.get(month_name, month_name)

# Function to convert term into the last day of the month or specific date
def convert_term_to_date(term):
    # Match month-year format like "Apr 2021", "Fall 2025", etc.
    month_year_pattern = r'([A-Za-z]+)\s?(\d{4})'
    full_date_pattern = r'([A-Za-z]+)\s(\d{1,2}),\s(\d{4})'
    season_to_date = {
        "Fall": "12/31",
        "Spring": "05/15",
        "Summer": "08/15"
    }
    
    # Check for Fall, Spring, Summer terms
    for season in season_to_date:
        if season.lower() in term.lower():
            year = re.search(r'\d{4}', term).group()
            return f"{season_to_date[season]}/{year}"
    
    # Check if it's a full date format like "August 1, 2022"
    match = re.match(full_date_pattern, term)
    if match:
        month_name = correct_month_name(match.group(1))
        day = match.group(2)
        year = match.group(3)
        return f"{datetime.strptime(f'{month_name} {day}, {year}', '%B %d, %Y').strftime('%m/%d/%Y')}"
    
    # Check if it's a month-year format like "Mar 2015"
    match = re.match(month_year_pattern, term)
    if match:
        month_name = correct_month_name(match.group(1))
        year = match.group(2)
        try:
            # Convert month name to month number
            month = datetime.strptime(month_name[:3], "%b").month
            # Get the last day of the month
            last_day = datetime(year=int(year), month=month, day=1).replace(day=28) + timedelta(days=4)
            last_day = last_day - timedelta(days=last_day.day)
            return last_day.strftime('%m/%d/%Y')
        except ValueError:
            return term
    
    return "Ending term not found"

def extract_name_from_filename(filename):
    # Extract the base name of the file without the directory path
    base_filename = os.path.basename(filename)
    # Regular expression to extract the name from the filename
    match = re.match(r"(.+?)\s*(\w+\s+\d{4}|\w+\s+\d{1,2},\s*\d{4})", base_filename)
    if match:
        name = match.group(1).replace('_', ' ').replace('.', ' ').strip()
        # Split the name and reverse the order
        name_parts = name.split(',')
        if len(name_parts) == 2:
            name = f"{name_parts[1].strip()} {name_parts[0].strip()}"
        return name
    return "Name not found"

def extract_date_from_filename(filename):
    # Extract the base name of the file without the directory path
    base_filename = os.path.basename(filename)
    # Regular expression to extract the date from the filename
    match = re.search(r"(\w+\s+\d{4}|\w+\s+\d{1,2},\s*\d{4})", base_filename)
    if match:
        return match.group(0).strip()
    return "Ending term not found"

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

    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".pdf"):
                name = re.split(r'[\s,_]', filename)[0]
                grouped_files[name].append(os.path.join(root, filename))

    for name, files in grouped_files.items():
        latest_file = get_latest_pdf(files)
        if latest_file:
            professor_name = extract_name_from_filename(latest_file)
            ending_term = extract_date_from_filename(latest_file)
            department_name = os.path.basename(os.path.dirname(latest_file))
            results.append({
                "Department": department_name,
                "Professor Name": professor_name,
                "Ending Term": convert_term_to_date(ending_term),
                "PDF File": os.path.basename(latest_file)
            })

    return results

# Specify the folder path
folder_path = "UpdateProfessor/data"
results = process_pdfs_in_folder(folder_path)

# Create the resultCsv folder if it doesn't exist
result_folder = "UpdateProfessor/resultCsv"
os.makedirs(result_folder, exist_ok=True)

# Save results to a single CSV file with department name, professor name, ending term, and PDF file name
csv_file_name = os.path.join(result_folder, "all_departments.csv")
df = pd.DataFrame(results)
df.to_csv(csv_file_name, index=False)

print(f"Results have been saved to {csv_file_name}")