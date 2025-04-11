🧾 Invoice OCR Web App
A simple and professional web app that lets you extract key invoice data (like Invoice Number, Date, Vendor, and Total Amount) from uploaded PDFs or image files using OCR and save it directly to an Excel sheet.

✨ Features
Upload invoices in PDF, JPG, PNG formats

Extract fields using Tesseract OCR + Regex:

Invoice Number

Date

Vendor

Total Amount (₹, Rs., Grand Total, etc.)

Instantly display extracted data on the website

Save extracted data to Excel (new sheet per upload)

Clean, responsive web interface (HTML/CSS/JavaScript)

🚀 How It Works
Upload a PDF or image file

OCR reads text using Tesseract

Regex patterns identify key fields

Results are shown on screen

Data is saved to extracted_data.xlsx

🛠 Tech Stack
Python (Flask)

HTML, CSS, JavaScript

Tesseract OCR

pdf2image, Pillow

pandas, openpyxl

📦 Setup Instructions
Clone the repo:

bash
Copy
Edit
git clone https://github.com/your-username/invoice-ocr-webapp.git
cd invoice-ocr-webapp
Install dependencies:

bash
Copy
Edit
pip install flask pytesseract pdf2image pillow openpyxl pandas
Configure paths in app.py:

Tesseract executable path (Windows):

python
Copy
Edit
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
Poppler path (for PDF conversion):

python
Copy
Edit
poppler_path = r"C:\path\to\poppler\bin"
Run the app:

bash
Copy
Edit
python app.py
Open your browser:

cpp
Copy
Edit
http://127.0.0.1:5000
🧪 Sample Use Cases
Invoice scanning & data collection

Bookkeeping automation

Invoice-to-database import tools

Academic or portfolio OCR projects
