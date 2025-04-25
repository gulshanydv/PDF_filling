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
 
 
def get_filling_prompt(html_content, json_data):
    import json
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
        temperature=0.3,
        max_tokens=10000
    )
 
    # filled_html = response["choices"][0]["message"]["content"]
    filled_html = response["choices"][0]["message"]["content"].strip()

    # Remove markdown-style code block wrapping if present
    if filled_html.startswith("```html") and filled_html.endswith("```"):
        filled_html = filled_html[7:-3].strip()
    elif filled_html.startswith("```") and filled_html.endswith("```"):
        filled_html = filled_html[3:-3].strip()

    save_filled_html(filled_html, output_path)
    print(f"Filled HTML saved to: {output_path}")
 
 
if __name__ == "__main__":
    input_html_path = "html_output/page_1.html"
    output_html_path = "filled_form.html"
    json_data_path = "dummy_data.json"
 
    fill_html_form_using_llm_with_json(input_html_path, json_data_path, output_html_path)
