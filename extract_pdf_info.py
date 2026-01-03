"""
extract_pdf_info.py

Extract layout information from V2 Site-02.pdf
"""

try:
    import PyPDF2
    pdf_path = 'c:/Users/Admin/Desktop/V2 Site-02.pdf'
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        print(f"Total pages: {len(reader.pages)}")
        for i, page in enumerate(reader.pages):
            print(f"\n--- Page {i+1} ---")
            text = page.extract_text()
            print(text[:1000])
except Exception as e:
    print(f"PyPDF2 not available, trying alternative method: {e}")
    
try:
    from pdf2image import convert_from_path
    print("PDF is an image-based drawing - will need manual measurement")
except:
    print("PDF appears to be a CAD drawing - manual review recommended")
