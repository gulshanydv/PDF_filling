# from weasyprint import HTML
# HTML('html_output/page_1.html').write_pdf('output.pdf')
# print("PDF created successfully with WeasyPrint!")



from weasyprint import HTML, CSS

HTML('html_output/page_1.html').write_pdf(
    'output.pdf',
    stylesheets=[CSS(string='@page { size: 9in 18in !important; margin: 1cm; }')]

)
print("PDF created successfully with custom size!")
