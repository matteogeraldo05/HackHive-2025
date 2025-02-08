import os # for file management
from tkinter import filedialog, Text # GUI components
import fitz  # For pdf processing
from transformers import BlipProcessor # For pdf processor

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base") # Initializes and loads pre-trained processor

def upload_pdf(self): # Function to upload a pdf
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")]) # Let user choose a pdf from their computer
    if file_path: # Make sure file exists
        self.label.config(text="Processing PDF...")
        self.process_pdf(file_path)

def process_pdf(self, pdf_path): # Pass the chosen pdf file to fitz for pdf processing
    # Open the file and initialize some containers for the text and
    doc = fitz.open(pdf_path)
    combined_text = ""
    image_files = []

    # Iterates through the pages in the PDF
    for page_num, page in enumerate(doc):
        combined_text += page.get_text() + "\n" # Adds all the text on the current page to the text container
        for img_index, img in enumerate(page.get_images(full=True)): # Iterates through the images found in the page
            # Extract the image data and add it to the image container.
            base_image = doc.extract_image(img[0]) # Extract the image data from the pdf using the cross-reference number (img[0])
            image_bytes = base_image["image"] # Extracts the image data in bytes
            img_ext = base_image["ext"] # Sets extension of file
            img_path = f"page{page_num+1}_img{img_index+1}.{img_ext}" # Creates a path for the image so we can write the image data and save the image to the disc!
            with open(img_path, "wb") as f:
                f.write(image_bytes) # write the image data to the image path and save to the disc
            image_files.append(img_path) # add the image to the image file container.


    self.text_display.delete(1.0, "end") # clears the text area
    self.text_display.insert("end", f"Extracted Text:\n{combined_text}\n") # Displays the content of the page in the text area

    # Display each image caption
    for img_path in image_files: # iterate through all extracted images
        self.display_image(img_path) # Display the image

    for img_path in image_files: # remove the image after, as its no longer needed.
        os.remove(img_path)