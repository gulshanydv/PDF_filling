
# AI-Powered PDF Form Auto-Filler

This project automates the filling of structured PDF forms using Azure's LLMs. It ensures the **visual layout** of the final filled PDF remains identical to the original form.

---

## Project Goal

- Upload a **blank PDF form** and **dummy user data**.
- Auto-generate a **filled PDF** with the same layout.
- Use an LLM (Azure OpenAI) to understand and populate fields.

---

## 🔧 Project Setup

### 1. Clone the Repository

git clone https://github.com/gulshanydv/PDF_filling.git
cd PDF_filling

# Create virtual environment
python -m venv venv

# Activate it
# On Windows
venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Create .env File for Azure Credentials
# Create a .env file in the project root directory and add the following environment variables:

AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name  #gpt-4o-mini recommended
AZURE_OPENAI_API_VERSION=2023-03-15-preview

You can load these variables in Python using python-dotenv:

from dotenv import load_dotenv
load_dotenv()

# AI-Powered PDF Form Auto-Filler

This project automates the filling of structured PDF forms using Azure's LLMs. It ensures the **visual layout** of the final filled PDF remains identical to the original form.

## Project Goal

- Upload a **blank PDF form** and **dummy user data**.
- Auto-generate a **filled PDF** with the same layout.
- Use an LLM (Azure OpenAI) to understand and populate fields.

## Workflow Overview

1. **PDF to HTML Conversion**  
   - Use `PyMuPDF` to convert PDF to styled HTML while preserving layout.
   - Parse and transform elements for text extraction.

2. **LLM-based Data Filling**  
   - Use Azure OpenAI to fill HTML placeholders with appropriate data.
   - Inject data only in designated locations to preserve layout.

3. **HTML to PDF Rendering**  
   - Convert the filled HTML back to PDF using libraries like `WeasyPrint`, `wkhtmltopdf`, or `pdfkit`.

## Known Issues & Fixes

### Problem: Missing checkboxes, radio buttons, and table lines
- These project is not detecting radio buttons, and table lines.


