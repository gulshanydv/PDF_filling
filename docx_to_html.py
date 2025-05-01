from spire.doc import *
from spire.doc.common import *
     
# Create a Document instance
document = Document()

# Load a doc or docx document 
document.LoadFromFile("output.docx")

# Save to HTML
document.SaveToFile("output.html", FileFormat.Html)
document.Close()



