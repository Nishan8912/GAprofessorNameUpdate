import PyPDF2

def read_pdf_fields(file_path):
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        fields = reader.get_fields()
    return fields

def extract_professor_name_and_ending_term(fields):
    # Extract the professor's name and ending term date from the form fields
    professor_name = fields.get('Name of nominee', {}).get('/V', 'Name not found')
    ending_term = fields.get('Ending term', {}).get('/V', 'Ending term not found')
    
    return professor_name, ending_term

fields = read_pdf_fields("data\Biology\Wright, Timothy November 2029.pdf")
professor_name, ending_term = extract_professor_name_and_ending_term(fields)

print(f"Professor Name: {professor_name}")
print(f"Ending Term: {ending_term}")