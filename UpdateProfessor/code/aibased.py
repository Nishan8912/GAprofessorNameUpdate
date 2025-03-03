import pdfplumber
import pytesseract
from PIL import Image
from tika import parser
from langchain.chains import AnalyzeDocumentChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

# Function to extract text from a PDF (machine-readable text)
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Function to extract text from scanned images using Tesseract OCR
def extract_text_from_image(pdf_path):
    # Convert PDF pages to images (we'll assume the first page)
    from pdf2image import convert_from_path
    images = convert_from_path(pdf_path)
    
    # Use OCR to extract text from the first page image
    text = pytesseract.image_to_string(images[0])
    return text

# Function to process the text using Langchain (summarize or extract specific data)
def process_text_with_langchain(text):
    # Use a simple prompt template and OpenAI model for summarization
    prompt = PromptTemplate(input_variables=["text"], template="Summarize the following content: {text}")
    llm = OpenAI(model="gpt-3.5-turbo")  # You can change this to any available model
    
    chain = AnalyzeDocumentChain(combine_docs_chain=llm)
    response = chain.run(input_document=text)
    return response

# Main function to process the PDF and extract data
def extract_data_from_pdf(pdf_path):
    # First try extracting text using PDFPlumber (for machine-readable PDFs)
    text = extract_text_from_pdf(pdf_path)
    
    # If no text is found, it might be an image-based PDF, so use Tesseract OCR
    if not text.strip():
        print("No machine-readable text found. Using OCR...")
        text = extract_text_from_image(pdf_path)
    
    # Process the extracted text using Langchain to summarize or extract specific data
    if text.strip():
        print("Processing text using Langchain...")
        processed_text = process_text_with_langchain(text)
        print("Processed Text: ", processed_text)
    else:
        print("No text found in the document.")
        
# Example Usage
pdf_path = "UpdateProfessor\data\Animal-and-Range-Sciences\allison, chris may 2020.pdf"
extract_data_from_pdf(pdf_path)
