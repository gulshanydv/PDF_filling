import os
import openai
import json
import openai
from dotenv import load_dotenv

load_dotenv()


# Set your Azure OpenAI credentials
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
API_VERSION = os.getenv("API_VERSION")



# Configure OpenAI client
openai.api_type = "azure"
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_key = AZURE_OPENAI_API_KEY
openai.api_version = API_VERSION
 
 
 
 
def read_html_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
 
# Save filled HTML file
def save_filled_html(output_html, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output_html)
 
# def get_filling_prompt(html_content, json_data):
#     import json
#     return f"""
#     You are a highly specialized AI assistant trained for **precise HTML form filling** and **checkbox selection** based on JSON data.

#     You are given:
#     1. An **HTML form** that may contain:
#     - Empty text fields (e.g., `<p>__________</p>`, `<td>……………</td>`, `<span> </span>`)
#     - **Multiple-choice questions with checkboxes** (e.g., `<input type="checkbox">` or similar)

#     2. A **JSON object** that provides the correct data or answers.

#     ---

#     ### Your Task:
#     Your ONLY task is to:
#     - **Fill blank-looking HTML tags** using the provided JSON data
#     - **Mark the correct checkbox option** for each multiple-choice question

#     ---

#     ### Rules to Follow Strictly:

#     #### 1. For Text Fields:
#     - Fill only tags that are **completely blank or contain placeholders** like `__________`, `……`, `&nbsp;`, etc.
#     - Match the nearby **label** or **preceding text** to a JSON key using fuzzy logic
#     - Do **not** fill tags that already contain meaningful text

#     #### 2. For Checkboxes:
#     - Only **one checkbox per question should be marked as correct**, based on the `"answer"` field in the JSON
#     - To mark a checkbox as selected, add the `checked` attribute:  
#     `<input type="checkbox">` → `<input type="checkbox" checked>`
#     - Use the text next to the checkbox to match it with the correct answer from the JSON
#     - **Never check multiple boxes** unless the question explicitly allows multiple answers (not applicable here)

#     #### 3. General Instructions:
#     - Do **not** modify unrelated parts of the HTML
#     - Do **not** add explanations or comments
#     - Do **not** insert data into sentence fragments or instructional text

#     ---

#     ### JSON Data (example):
#     ```json
#     {json.dumps(json_data, indent=2)}
#     HTML Input:
#     {html_content}
#     Return ONLY the updated HTML with the filled fields and marked checkboxes. Do not explain anything. Do not output extra text. """




def get_filling_prompt(html_content, json_data):
    import json
    return f"""
    # Advanced HTML Form Filling Expert System

    You are a hyper-specialized AI form processing system designed specifically for accurately filling HTML forms converted from PDF documents. Your ONLY purpose is to take the provided HTML form and fill ALL empty fields with matching data from the provided JSON.

    ## CRITICAL CONTEXT
    - This HTML was originally a PDF form converted to DOCX then to HTML, which creates SPECIFIC CHALLENGES
    - Many fields appear visually as blanks but have complex HTML representations
    - You MUST identify ALL fields regardless of how they're represented in the HTML
    - EVERY piece of JSON data MUST be placed somewhere appropriate in the form

    ## INPUT DATA
    
    ### JSON Data (for filling the form):
    ```json
    {json.dumps(json_data, indent=2)}
    ```

    ### HTML Form (to be filled):
    ```html
    {html_content}
    ```

    ## COMPREHENSIVE FIELD IDENTIFICATION SYSTEM

    ### 1. TEXT FIELDS - DETECT ALL POSSIBLE VARIANTS:
    - Standard empty tags: `<p></p>`, `<span></span>`, `<div></div>`, `<td></td>`
    - Tags with ONLY whitespace: `<p> </p>`, `<span>&nbsp;</span>`, `<div>  </div>`
    - Tags with placeholder patterns:
      * Underscores: `<p>_____</p>`, `<span>___</span>`, `<td>_______</td>`
      * Dots/periods: `<p>.....</p>`, `<span>...</span>`, `<td>........</td>`
      * Dashes: `<p>-----</p>`, `<span>---</span>`, `<td>-------</td>`
      * ANY combination of spaces, non-breaking spaces, underscores, dots
    - Form elements disguised as regular text due to conversion
    - ANY element that visually represents an empty field

    ### 2. TABLE CELLS - STRICT PROCESSING PROTOCOL:
    - **EXAMINE EVERY TABLE WITH EXTREME THOROUGHNESS**
    - **KEY-VALUE DISTINCTION PROCEDURE**:
      * First column or labeled columns are ALMOST ALWAYS keys/labels - NEVER FILL THESE
      * Empty cells in "data" columns (non-first columns) MUST be filled
      * Column and row headers MUST be preserved exactly as they are
      * ONLY fill cells that are genuinely empty or have placeholder characters
    - **STEP-BY-STEP TABLE PROCESSING REQUIREMENTS**:
      1. FIRST: Identify the structure - determine which columns are keys and which are for data
      2. SECOND: For each row, find ALL empty cells in data columns
      3. THIRD: Match each empty cell with appropriate JSON data based on row and column context
      4. FOURTH: Verify EVERY data column has been checked for empty cells
    - **STRICT TABLE CELL IDENTIFICATION**:
      * Empty cells: `<td></td>`, `<td>&nbsp;</td>`, `<td> </td>`
      * Cells with ONLY placeholder patterns: `<td>_____</td>`, `<td>.......</td>`
      * Cells containing empty paragraphs: `<td><p></p></td>`
      * Cells with only whitespace or non-breaking spaces
    - **MANDATORY TABLE VERIFICATION CHECKLIST**:
      * Have ALL non-key columns been checked for empty cells?
      * Has EVERY empty cell in data columns been filled?
      * Have label/key columns been left untouched?
      * Has appropriate JSON data been matched to each empty cell?
    - **TABLE DATA MATCHING HIERARCHY**:
      1. Match by direct row label + column header combination
      2. Match by semantic relationship to row context
      3. Match by field type appropriateness
    - **CRITICAL**: The left-most column or other labeled columns are typically labels/keys and should NEVER be filled with data - data goes in empty cells next to these labels

    ### 3. CHECKBOXES - ADVANCED DETECTION:
    - Identify ALL possible checkbox representations:
      * Unicode characters: `□`, `⬜`, `▢`, `○`, `⚪`, `⬭`
      * ASCII patterns: `[ ]`, `( )`, `|_|`
      * HTML/CSS-based boxes: `<div class="box"></div>`, elements with border styles
      * Small rectangular shapes that appear after conversion
      * ANY square or rectangular empty shape
      * **Single-cell tables with borders** - CRITICAL: Small tables with single empty cells are often checkboxes after conversion
      * Table cells with specific styling: `<td style="width:6.12pt; vertical-align:top"><p></p></td>`
      * Small fixed-width cells (width under 15pt) are likely checkboxes
      * Table cells with borders, especially solid borders
    - Look for grouped boxes near labels that match JSON boolean values
    - Check the appropriate boxes by:
      * Replacing with filled symbols: `☑`, `✓`, `✔`, `■`, `●`, `⬤` 
      * OR adding text "X" or "✓" inside the element
      * OR adding content to the empty paragraph inside table cells: `<td><p>✓</p></td>`
      * OR adding inline style to indicate selection (e.g., background-color)
    - **ANALYZE HTML SOURCE** to find disguised checkboxes from the conversion
    - **SPECIAL ATTENTION TO TABLES**: Small tables with borders (especially single-cell tables) should be treated as potential checkboxes and marked accordingly when matching JSON boolean values

    ### 4. RADIO BUTTONS/OPTIONS:
    - Identify radio-button-like elements similar to checkboxes
    - Look for grouped circular elements: `○`, `⚪`, `( )` 
    - Select appropriate option based on JSON values

    ### 5. SIGNATURES/DATE FIELDS:
    - Identify signature fields (often large blank spaces)
    - Insert name data for signature fields
    - Fill date fields with properly formatted dates from JSON

    ## ADVANCED MATCHING ALGORITHM

    1. **COMPLETE JSON UTILIZATION**:
       - **EVERY** key-value pair in the JSON data MUST be used somewhere
       - Search thoroughly for appropriate places to insert EACH piece of data
       - If multiple places could accept the same data, make a logical choice
       - Verify that NO data points from JSON were missed

    2. **CONTEXT-AWARE FIELD MATCHING**:
       - Analyze text BEFORE and AFTER potential fields to determine purpose
       - Use proximity to labels/headings (even if in different tags)
       - Pattern recognition: "Label: _____" or "Label: [empty tag]"
       - For tables: Use row labels AND column headers for context
       - Match fields based on semantic meaning, not just literal text matching

    3. **MULTI-FIELD DATA DISTRIBUTION**:
       - Intelligently split complex data across multiple fields:
         * Names into first/middle/last components
         * Addresses into street/city/state/zip
         * Dates into month/day/year
         * Phone numbers into area code/number segments
       - When multiple empty fields appear in sequence, distribute data logically

    4. **DATA FORMATTING PRECISION**:
       - Format ALL data appropriately for context:
         * Dates: Match the exact format required (MM/DD/YYYY, DD/MM/YYYY)
         * Phone numbers: Include proper separators
         * Currency: Include currency symbols and decimal places
         * Capitalize names, addresses properly
       - Maintain consistent formatting throughout the document

    ## ERROR PREVENTION SYSTEM

    1. **FIELD VERIFICATION CHECKLIST**:
       - After initial filling, VERIFY every JSON data point was used
       - DOUBLE-CHECK all tables for missed cells
       - CONFIRM all checkboxes that should be selected are marked
       - ENSURE no empty fields remain that should contain data

    2. **PRESERVATION REQUIREMENTS**:
       - NEVER alter field labels, instructions, or headings
       - NEVER change document structure or layout
       - NEVER modify content that isn't clearly a field
       - NEVER add new elements or sections

    ## OUTPUT FORMAT

    Return ONLY the completed HTML form with ALL appropriate fields filled. Do not include explanations or notes. The output must be the complete HTML document with ALL fields properly populated with the JSON data.

    ## FINAL VERIFICATION

    Before submission, scan the entire document one more time to ensure:
    1. EVERY JSON data point has been placed in the form
    2. NO fields that should be filled remain empty
    3. ALL checkboxes are appropriately marked
    4. ALL table cells have been properly examined and filled
    5. The document structure remains intact
    """




 
# LLM-powered filler using Azure OpenAI + JSON input
def fill_html_form_using_llm_with_json(html_path, json_data_path, output_path):
    html_content = read_html_file(html_path)
 
    with open(json_data_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
 
    prompt = get_filling_prompt(html_content, json_data)
 
    print("Sending prompt to Azure OpenAI...")
    response = openai.ChatCompletion.create(
        engine=AZURE_DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that fills HTML forms at suitable place using JSON-based data."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=10000
    )
 
    # filled_html = response["choices"][0]["message"]["content"]
    filled_html = response["choices"][0]["message"]["content"].strip()
    filled_html = filled_html.replace(
        '<p style="line-height:115%; font-size:12pt"><span style="color:#ff0000">Evaluation Warning: The document was created with Spire.Doc for Python.</span></p>',
        ''
    )
    # Remove markdown-style code block wrapping if present
    if filled_html.startswith("```html") and filled_html.endswith("```"):
        filled_html = filled_html[7:-3].strip()
    elif filled_html.startswith("```") and filled_html.endswith("```"):
        filled_html = filled_html[3:-3].strip()

    save_filled_html(filled_html, output_path)
    print(f"Filled HTML saved to: {output_path}")
 
 
if __name__ == "__main__":
    input_html_path = "output.html"
    output_html_path = "filled_form.html"
    json_data_path = "dummy_data.json"
 
    fill_html_form_using_llm_with_json(input_html_path, json_data_path, output_html_path)
