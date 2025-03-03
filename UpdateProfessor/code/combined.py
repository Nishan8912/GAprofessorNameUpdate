import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
import PyPDF2
import os
import pandas as pd
from collections import defaultdict

# Specify the correct path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\nishan2\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

def extract_name_from_filename(filename):
    # Regular expression to extract the name from the filename
    match = re.match(r"(.+?)\s*(\w+\s+\d{4}|\w+\s+\d{1,2},\s*\d{4})", filename)
    if match:
        name = match.group(1).replace('_', ' ').replace('.', ' ').strip()
        # Split the name and reverse the order
        name_parts = name.split(',')
        if len(name_parts) == 2:
            name = f"{name_parts[1].strip()} {name_parts[0].strip()}"
        return name
    return "Name not found"

def extract_date_from_filename(filename):
    # Regular expression to extract the date from the filename
    match = re.search(r"(\w+\s+\d{4}|\w+\s+\d{1,2},\s*\d{4})", filename)
    if match:
        return match.group(0).strip()
    return "Ending term not found"

def read_pdf_fields(file_path):
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        fields = reader.get_fields()
    return fields

def extract_professor_name_and_ending_term(fields):
    if fields is None:
        return "Fields not found", "Fields not found"
    
    # Extract the professor's name and ending term date from the form fields
    professor_name = fields.get('Name of applicant', {}).get('/V', 'Name not found')
    ending_term = fields.get('Ending term', {}).get('/V', 'Ending term not found')
    return professor_name, ending_term

def read_pdf_text(file_path):
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = reader.pages[0].extract_text() if reader.pages else ""
    return text

def extract_ending_term_from_text(text):
    # Regular expression to find the ending term date
    ending_term_match = re.search(r"(\w+\s+\d{4})\s*(to|through)\s*(\w+\s+\d{4})", text)
    if ending_term_match:
        return ending_term_match.group(3).strip()
    return "Ending term not found"

def extract_information_from_ocr(pdf_path):
    # Open the PDF file
    document = fitz.open(pdf_path)
    
    # Read the first page
    text = ""
    page = document.load_page(0)
    pix = page.get_pixmap()
    img = Image.open(io.BytesIO(pix.tobytes()))
    text += pytesseract.image_to_string(img)

    # Extract the required information
    lines = text.split('\n')
    end_date = "Ending term not found"

    for line in lines:
        if re.search(r"Dates?:", line):
            dates = re.split(r" to | through ", line)
            if len(dates) == 2:
                end_date = dates[1].strip()

    return end_date

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
            file_path = os.path.join(folder_path, latest_file)
            professor_name = extract_name_from_filename(latest_file)
            ending_term = extract_date_from_filename(latest_file)
            fields = read_pdf_fields(file_path)
            if fields:
                professor_name, ending_term = extract_professor_name_and_ending_term(fields)
            else:
                text = read_pdf_text(file_path)
                if text.strip():
                    extracted_ending_term = extract_ending_term_from_text(text)
                    if extracted_ending_term != "Ending term not found":
                        ending_term = extracted_ending_term
                else:
                    extracted_ending_term = extract_information_from_ocr(file_path)
                    if extracted_ending_term != "Ending term not found":
                        ending_term = extracted_ending_term
            results.append({
                "File": latest_file,
                "Professor Name": professor_name,
                "Ending Term": ending_term
            })

    return results

# Specify the folder path
folder_path = "UpdateProfessor\data\Animal-and-Range-Sciences"
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