from flask import Flask, render_template, request
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import pandas as pd
import re
import os

# ---- Flask Setup ----
app = Flask(__name__)

# ---- Config ----
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
poppler_path = r"C:\Users\vishn\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"

# ---- Regex Map ----
regex_map = {
    "Vendor": r"Vendor[:\s]*(.+)",
    "Address": r"Address[:\s]*(.+)",
    "Invoice Number": r"Invoice\s*#[:\s]*([A-Z0-9\-]+)",
    "Date": r"Date[:\s]*([0-9]{2}/[0-9]{2}/[0-9]{4})",
    "Total Amount": r"(Total\s*Amount|Grand\s*Total|Amount\s*Payable|Total)[:\s₹$]*([\d,]+\.\d{2})",
    "GSTIN": r"GSTIN[:\s]*([0-9A-Z]{15})",
    "PAN": r"PAN[:\s]*([A-Z]{5}[0-9]{4}[A-Z])",
    "Email": r"Email[:\s]*([\w\.-]+@[\w\.-]+)",
    "Phone Number": r"(Phone|Contact)[:\s]*(\+?\d{10,13})",
    "Subtotal": r"Subtotal[:\s₹$]*([\d,]+\.\d{2})",
    "Tax": r"Tax[:\s₹$]*([\d,]+\.\d{2})",
    "Discount": r"Discount[:\s₹$]*([\d,]+\.\d{2})"
}


# ---- Field Extraction Function ----
def extract_invoice_fields(text, selected_fields):
    data = {}
    for field in selected_fields:
        pattern = regex_map.get(field)
        if pattern:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(len(match.groups()))
                data[field] = value.strip()
    return data

# ---- OCR Processor ----
def process_file(file, selected_fields):
    extracted = []
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        pages = convert_from_bytes(file.read(), dpi=300, poppler_path=poppler_path)
        for i, page in enumerate(pages):
            text = pytesseract.image_to_string(page)
            fields = extract_invoice_fields(text, selected_fields)
            fields["Page"] = i + 1
            extracted.append(fields)
    else:
        img = Image.open(file)
        text = pytesseract.image_to_string(img)
        fields = extract_invoice_fields(text, selected_fields)
        fields["Page"] = 1
        extracted.append(fields)

    return extracted

# ---- Routes ----
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_invoice():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    selected_fields = request.form.getlist("fields")

    if not selected_fields:
        return "No fields selected", 400

    results = process_file(file, selected_fields)

    df = pd.DataFrame(results)
    excel_path = "invoice_data.xlsx"
    sheet_name = f"Invoice_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"

    try:
        if os.path.exists(excel_path):
            with pd.ExcelWriter(excel_path, mode='a', engine='openpyxl', if_sheet_exists='new') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        try:
            os.startfile(excel_path)
        except Exception as e:
            print("Could not open Excel automatically:", e)

        return f"✅ Invoice uploaded and saved in sheet: <b>{sheet_name}</b>"

    except Exception as e:
        return f"❌ Error: {str(e)}"

# ---- Run App ----
if __name__ == '__main__':
    app.run(debug=True)
