import os
import pandas as pd
from flask import send_file
from utils.pdf_utils import convert_to_pdf  # Import the PDF conversion function

def download_file(filetype, filename, result_folder):
    """Handles the download of different file types (CSV, Excel, TXT, PDF)."""
    filepath = os.path.join(result_folder, filename)

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        return {'error': f"Error reading file: {str(e)}"}, 500

    if filetype == 'csv':
        return send_file(filepath, as_attachment=True)
    elif filetype == 'excel':
        excel_path = filepath.replace('.csv', '.xlsx')
        df.to_excel(excel_path, index=False)
        return send_file(excel_path, as_attachment=True)
    elif filetype == 'txt':
        txt_path = filepath.replace('.csv', '.txt')
        df.to_csv(txt_path, index=False, sep='\t')
        return send_file(txt_path, as_attachment=True)
    elif filetype == 'pdf':
        pdf_path = filepath.replace('.csv', '.pdf')
        convert_to_pdf(df, pdf_path)  # Call the function from pdf_utils.py
        return send_file(pdf_path, as_attachment=True)
    else:
        return {'error': 'Invalid file type requested'}, 400
