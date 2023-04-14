import uvicorn
from fastapi import FastAPI, Request, File, UploadFile, Body
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import docx
import pytesseract
from PIL import Image
from typing import List

def setup():
    app = FastAPI()

    # TODO: How to know origin of aws app runner health check?
    origins = [
        "*", # for dev
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    return app

def pdftotext(file_name):
  text = []
  # Open the PDF file in read-binary mode
  with open(file_name, 'rb') as file:
    # Create a PDF object
    pdf = PyPDF2.PdfReader(file)

    # Get the number of pages in the PDF document
    num_pages = len(pdf.pages)

    # Iterate over every page
    for page in range(num_pages):
      # Extract the text from the page
      result = pdf.pages[page].extract_text()
      text.append(result)

  text = "\n".join(text)

  return text

def docxtotext(file_name):
  # Open the Word document
  document = docx.Document(file_name)

  # Extract the text from the document
  text = '\n'.join([paragraph.text for paragraph in document.paragraphs])

  return text

def readtextfile(file_name):
  # Open the Text document
  with open(file_name, 'r') as file:
    text = file.read()

  return text

def imagetotext(file_name):
  # Open the image using PIL
  image = Image.open(file_name)

  # Extract the text from the image
  text = pytesseract.image_to_string(image)

  return text

def preprocesstext(text):
  # Split the string into lines
  lines = text.splitlines()
  # Use a list comprehension to filter out empty lines
  lines = [line for line in lines if line.strip()]
  # Join the modified lines back into a single string
  text = '\n'.join(lines)

  return text

async def get_text_from_each_file(files):
  textlist = []

  # Iterate over provided files
  for file in files:
    # Get file name
    file_name = file.filename
    # Get extention of file name
    ext = file_name.split(".")[-1].lower()

    # Process document based on extention
    if ext == "pdf":
      text = pdftotext(file_name)
    elif ext == "docx":
      text = docxtotext(file_name)
    elif ext == "txt":
      text = readtextfile(file_name)
    elif ext in ["png", "jpg", "jpeg"]:
      text = imagetotext(file_name)
    else:
      text = ""

    # Preprocess text
    text = preprocesstext(text)

    # Append the text to final result
    textlist.append(text)

  return textlist

app = setup()

@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"hello": "world"}

# get_text_from_files extracts and returns text from all of the files you upload
# curl -X POST http://0.0.0.0:8080/upload -F "files=@/path/to/file1.pdf" -F "files=@/path/to/file2.pdf" -H "Content-Type: multipart/form-data"
@app.post("/upload")
async def upload_files(files: List[UploadFile]):
    try:
        texts = await get_text_from_each_file(files)
        return texts
    except Exception as e:
        return {"message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=False)