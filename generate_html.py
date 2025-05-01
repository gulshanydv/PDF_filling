import fitz  # PyMuPDF
import os
 
def pdf_to_html_exact(pdf_path, output_dir="html_output"):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
 
    # Open PDF
    doc = fitz.open(pdf_path)
    print(f"Loaded {len(doc)} pages from {pdf_path}")
 
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        width, height = page.rect.width, page.rect.height
        html_body = page.get_text("html")
 
        # Set a margin for the page so that content isn't directly at the edges
        margin = 10  # Adjust this value as needed
 
        full_html = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Page {page_num + 1}</title>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background: #f9f9f9;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
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
        </html>
        """
        output_file = os.path.join(output_dir, f"page_{page_num + 1}.html")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_html)
 
        print(f"Page {page_num + 1} saved to {output_file}")
 
    print("All pages converted!")

 
if __name__ == "__main__":
    pdf_to_html_exact("A-1.pdf")
