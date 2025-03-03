import fitz  # PyMuPDF

def read_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

pdf_text = read_pdf("Fuqua, Donovan November 2029.pdf")
print(pdf_text)
