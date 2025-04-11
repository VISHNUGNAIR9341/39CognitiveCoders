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

# ---- Field Extraction Function ----
def extract_invoice_fields(text):
    data = {}

    vendor = re.search(r"Vendor[:\s]*(.+)", text, re.IGNORECASE)
    address = re.search(r"Address[:\s]*(.+)", text, re.IGNORECASE)
    invoice = re.search(r"Invoice\s*#[:\s]*([A-Z0-9\-]+)", text, re.IGNORECASE)
    date = re.search(r"Date[:\s]*([0-9]{2}/[0-9]{2}/[0-9]{4})", text)

    total = re.search(
        r"(Total\s*Amount|Grand\s*Total|Amount\s*Payable|Total)[:\s₹$]*([\d,]+\.\d{2})",
        text, re.IGNORECASE
    )

    if vendor: data["Vendor"] = vendor.group(1).strip()
    if address: data["Address"] = address.group(1).strip()
    if invoice: data["Invoice Number"] = invoice.group(1).strip()
    if date: data["Date"] = date.group(1).strip()
    if total: data["Total Amount"] = total.group(2).strip()

    return data

# ---- OCR Processor ----
def process_file(file):
    extracted = []

    filename = file.filename.lower()
    if filename.endswith(".pdf"):
        pages = convert_from_bytes(file.read(), dpi=300, poppler_path=poppler_path)
        for i, page in enumerate(pages):
            text = pytesseract.image_to_string(page)
            fields = extract_invoice_fields(text)
            fields["Page"] = i + 1
            extracted.append(fields)
    else:
        img = Image.open(file)
        text = pytesseract.image_to_string(img)
        fields = extract_invoice_fields(text)
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
    results = process_file(file)

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

        # ✅ Automatically open Excel file (only locally)
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
