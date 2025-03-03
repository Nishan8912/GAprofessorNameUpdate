import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re

# Specify the correct path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\nishan2\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

def extract_information(pdf_path):
    # Open the PDF file
    document = fitz.open(pdf_path)
    
    # Read the first two pages
    text = ""
    for page_num in range(2):
        page = document.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))
        text += pytesseract.image_to_string(img)

    # Print the extracted text for debugging
    print("Extracted Text:")
    print(text)
    print("End of Extracted Text\n")

    # Extract the required information
    lines = text.split('\n')
    name = None
    end_date = None

    for line in lines:
        if "Re: Approval of Dr." in line and "to" in line:
            print(f"Found line with name: {line}")
            match = re.search(r"Re: Approval of Dr\.\s*(.*?)\s*to", line)
            if match:
                name = match.group(1).strip()
        if "Dates:" in line:
            print(f"Found line with dates: {line}")
            dates = line.split(" to ")
            if len(dates) == 2:
                end_date = dates[1].strip()

    return name, end_date

# Example usage
pdf_path = "UpdateProfessor\data\Biology\Mabry, Karen Aug 2023.pdf"
name, end_date = extract_information(pdf_path)
print(f"Name: {name}")
print(f"End Date: {end_date}")