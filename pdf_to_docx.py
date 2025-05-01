from pdf2docx import Converter

pdf_file = 'DocumentiDuvri-1.pdf'
docx_file = 'output.docx'

# Use Converter for better layout handling
cv = Converter(pdf_file)
cv.convert(docx_file, start=0, end=1, layout=True) 
cv.close()


# from spire.pdf.common import *
# from spire.pdf import *

# # Create a PdfDocument object
# doc = PdfDocument()

# # Load a PDF document
# doc.LoadFromFile("tests.pdf")

# # Convert PDF to Word with streaming layout
# # doc.ConvertOptions.SetPdfToDocOptions(True, True)

# # Convert it to a docx file
# doc.SaveToFile("Output.docx", FileFormat.DOCX)

# # Dispose resources
# doc.Close()


# from spire.pdf.common import *
# from spire.pdf import *

# # Load the original PDF document
# original_doc = PdfDocument()
# original_doc.LoadFromFile("tests.pdf")

# # Create a new PDF document for the first page
# first_page_doc = PdfDocument()

# # Import the first page from the original document
# first_page_doc.InsertPage(original_doc, 0)

# # Save the single-page PDF to DOCX
# first_page_doc.SaveToFile("Output_First_Page.docx", FileFormat.DOCX)

# # Dispose resources
# original_doc.Close()
# first_page_doc.Close()
