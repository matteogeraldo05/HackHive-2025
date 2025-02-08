import fitz  # For pdf processing
from transformers import BlipProcessor # For pdf processor

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base") # Initializes and loads pre-trained processor

def process_pdf(self, pdf_path): # Pass the chosen pdf file to fitz for pdf processing
    # Open the file and initialize some containers for the text and
    doc = fitz.open(pdf_path)
    combined_text = ""

    # Iterates through the pages in the PDF
    for page_num, page in enumerate(doc):
        combined_text += page.get_text() + "\n" # Adds all the text on the current page to the text container

    return combined_text