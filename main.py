import os
import fitz  # PyMuPDF
import openai
import json
from dotenv import load_dotenv
import streamlit as st
from weasyprint import HTML as WeasyHTML, CSS
import tempfile

# Load environment variables
load_dotenv()

# Azure OpenAI setup
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_version = os.getenv("API_VERSION")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")

# Create prompt for the LLM
def get_filling_prompt(html_content, json_data):
    return f"""
    You are a highly specialized AI assistant trained for **precise HTML form filling**.

    You are given:
    1. An **HTML form** containing fields that appear to be blank (e.g., empty tags, placeholders like `__________`, `…………`, or many non-breaking spaces).
    2. A **JSON object** with realistic dummy data to insert into those blanks.

    ---

    ### Your Task:
    Your ONLY task is to **fill the visually blank-looking fields** using the provided dummy data. These fields are typically:

    - `<p>__________</p>`, `<span> </span>`, `<p></p>`, `<td>……………</td>`, or `<div>       </div>` (empty fields meant for input)
    - Fields that **follow a clear label** in a separate tag (like `Name:`, `Date of Birth:`), and are fully blank

    ---

    ### RULES TO STRICTLY FOLLOW:

    1. **NEVER** insert content into:
    - Tags that already contain visible words or real data
    - Tags that include instructions, even partially
    - Tags that begin or continue a sentence — DO NOT try to complete sentences

    2. **ONLY fill**:
    - Tags that are **completely empty or have placeholder patterns**
    - Tags that clearly appear **next to or underneath a label**, where the label is separate

    3. **Match fields intelligently**:
    - Use fuzzy matching between labels and JSON keys to determine which data goes where
    - If multiple similar blanks exist (e.g., multiple `<p>__________</p>` after multiple labels), match them one-by-one in order

    4. **If unsure whether to fill a tag — LEAVE IT BLANK.**

    ---

    ### JSON Data:
    ```json
    {json.dumps(json_data, indent=2)}

    ---
    
    ### HTML Input:
    -----
    {html_content}
    -----
    
    Return ONLY the updated HTML. Do not explain anything. Do not rephrase any content. Only modify blank tags.
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

    # Remove markdown-style code block wrapping if present
    if filled_html.startswith("```html") and filled_html.endswith("```"):
        filled_html = filled_html[7:-3].strip()
    elif filled_html.startswith("```html"):
        filled_html = filled_html[7:].strip()
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

            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            doc = fitz.open(pdf_path)
            filled_pages_html = []

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                html_body = page.get_text("html")

                # Wrap single-page HTML
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
                            background: #f9f9f9;
                            transform: scale(0.66);
                            transform-origin: 0 0;
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

                # Fill HTML page using LLM
                filled_html = fill_html_form_using_llm(full_html, json_data)
                filled_pages_html.append(filled_html)

            # Combine all filled pages into one HTML document
            combined_html = "\n".join(filled_pages_html)

            # Convert to final PDF
            output_pdf_path = os.path.join(tempfile.gettempdir(), "filled_output.pdf")
            WeasyHTML(string=combined_html).write_pdf(
                output_pdf_path,
                stylesheets=[CSS(string='@page { size: 157.5mm 222.75mm !important; margin: 1cm!important; }')]
            )

            with open(output_pdf_path, "rb") as f:
                st.success("PDF generated successfully!")
                st.download_button(
                    label="⬇Download Filled PDF",
                    data=f,
                    file_name="filled_form.pdf",
                    mime="application/pdf"
                )



