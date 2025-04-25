import os
import fitz  # PyMuPDF
import openai
import json
from dotenv import load_dotenv
import streamlit as st
from weasyprint import HTML as WeasyHTML
import tempfile

# Load environment variables
load_dotenv()

# Azure OpenAI setup
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_version = os.getenv("API_VERSION")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")

# Convert PDF to HTML (first page only)
def pdf_to_html_exact(pdf_path):
    doc = fitz.open(pdf_path)
    html_pages = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        html_body = page.get_text("html")
        
        full_html = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Page {page_num + 1}</title>
            <style>
                @page {{
                    size: A4;
                    margin: 0;
                }}   
                    
                body {{
                    margin: 0;
                    padding: 0;
                    background: #fff;
                }}
                p {{
                    position: absolute;
                    margin: 0;
                    padding: 0;
                    white-space: pre;
                }}
                span {{
                    white-space: pre;
                }}
            </style>
        </head>
        <body>
            <div class="pdf-page">
                {html_body}
            </div>
        </body>
        </html>"""
        
        html_pages.append(full_html)
        
    return full_html

# Create prompt for the LLM
def get_filling_prompt(html_content, json_data):
    return f"""
    # HTML Form Filling Specialist

    You are a precision-focused assistant specialized in HTML form completion. Your task requires strict adherence to specific guidelines.

    ## INPUT MATERIALS:
    1. **HTML Form**: Contains visually empty fields (blank tags, placeholders like `__________`, `…………`, or multiple spaces)
    2. **JSON Data**: Contains structured information to be inserted into appropriate form fields

    ## CORE OBJECTIVE:
    Insert JSON data into visually empty HTML fields while preserving the exact structure and formatting of the original document.

    ## FIELD IDENTIFICATION CRITERIA:
    Only fill elements matching these patterns:
    - Empty tags: `<p></p>`, `<span></span>`, `<div></div>`
    - Placeholder patterns: `<p>__________</p>`, `<td>……………</td>`
    - Multiple non-breaking spaces: `<div>&nbsp;&nbsp;&nbsp;</div>`
    - Fields that follow standalone labels in separate tags

    ## CRITICAL RULES:
    1. **DO NOT MODIFY**:
       - Tags containing any visible text (except placeholder patterns)
       - Tags with instructions or guidance text
       - Tags that form part of a sentence or paragraph
       - Any element that doesn't clearly represent a form field

    2. **INTELLIGENT MATCHING**:
       - Use semantic matching between field labels and JSON keys
       - Match similar blank fields in sequence if multiple exist
       - Consider field context and proximity to labels
       - Field types should guide data format (dates, numbers, text)

    3. **PRESERVATION REQUIREMENTS**:
       - Maintain all HTML attributes exactly as provided
       - Preserve all CSS classes and styling
       - Keep all non-field content unchanged
       - Maintain document structure and hierarchy

    4. **UNCERTAINTY PROTOCOL**:
       - When uncertain about a field, leave it unchanged
       - Prioritize accuracy over completeness
       - Do not guess or invent connections

    ## DATA:
    ```json
    {json.dumps(json_data, indent=2)}
    ```

    ## HTML FORM:
    ```html
    {html_content}
    ```

    Return only the modified HTML with appropriate fields filled. Make no explanations or comments. Your response must be pure HTML that can be directly used.
    """
    
    
    
def fill_html_form_using_llm(html_content, json_data): 
    prompt = get_filling_prompt(html_content, json_data) 
    response = openai.ChatCompletion.create( 
                engine=AZURE_DEPLOYMENT_NAME, 
                messages=[ {"role": "system", "content": "You are a helpful assistant that fills HTML forms using JSON-based data."}, 
                          {"role": "user", "content": prompt} ], 
                temperature=0.3, 
                max_tokens=10000 )
    filled_html = response["choices"][0]["message"]["content"].strip()

    # Remove markdown-style wrapping
    if filled_html.startswith("```html") and filled_html.endswith("```"):
        filled_html = filled_html[7:-3].strip()
    elif filled_html.startswith("```") and filled_html.endswith("```"):
        filled_html = filled_html[3:-3].strip()

    return filled_html


st.title("PDF Form Auto-Filler (Powered by Azure OpenAI)")

uploaded_pdf = st.file_uploader("Upload PDF form", type=["pdf"]) 
uploaded_json = st.file_uploader("Upload JSON data", type=["json"])

if uploaded_pdf and uploaded_json: 
    if st.button("Generate Filled PDF"): 
        with st.spinner("Processing... Please wait..."):

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                temp_pdf.write(uploaded_pdf.read())
                pdf_path = temp_pdf.name

            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_json:
                temp_json.write(uploaded_json.read())
                json_path = temp_json.name

            raw_html = pdf_to_html_exact(pdf_path)

            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            # Fill HTML using LLM
            filled_html = fill_html_form_using_llm(raw_html, json_data)

            # Convert HTML to final PDF
            output_pdf_path = os.path.join(tempfile.gettempdir(), "filled_output.pdf")
            WeasyHTML(string=filled_html).write_pdf(output_pdf_path)

            # Serve the result
            with open(output_pdf_path, "rb") as f:
                st.success("PDF generated successfully!")
                st.download_button(
                    label="⬇Download Filled PDF",
                    data=f,
                    file_name="filled_form.pdf",
                    mime="application/pdf"
                )




