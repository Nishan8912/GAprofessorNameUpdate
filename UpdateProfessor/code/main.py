import PyPDF2
import re
import os
import pandas as pd

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
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text

def extract_professor_name_and_ending_term_from_text(text):
    # Regular expression to find the professor's name
    name_match = re.search(r"Name of nominee\s*:\s*(.*)", text)
    # Regular expression to find the ending term date
    ending_term_match = re.search(r"Ending term\s*:\s*(\w+ \d{4})", text)
    
    professor_name = name_match.group(1).strip() if name_match else "Name not found"
    ending_term = ending_term_match.group(1).strip() if ending_term_match else "Ending term not found"
    
    return professor_name, ending_term

def process_pdfs_in_folder(folder_path):
    results = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            fields = read_pdf_fields(file_path)
            if fields:
                professor_name, ending_term = extract_professor_name_and_ending_term(fields)
            else:
                text = read_pdf_text(file_path)
                professor_name, ending_term = extract_professor_name_and_ending_term_from_text(text)
            results.append({
                "File": filename,
                "Professor Name": professor_name,
                "Ending Term": ending_term
            })
    return results

# Specify the folder path
folder_path = "UpdateProfessor\data\Biology"
results = process_pdfs_in_folder(folder_path)

# Create the resultCsv folder if it doesn't exist
result_folder = "UpdateProfessor\resultCsv"
os.makedirs(result_folder, exist_ok=True)

# Save results to a CSV file with the folder name as the file name inside the resultCsv folder
folder_name = os.path.basename(folder_path)
csv_file_name = os.path.join(result_folder, f"{folder_name}.csv")
df = pd.DataFrame(results)
df.to_csv(csv_file_name, index=False)

print(f"Results have been saved to {csv_file_name}")