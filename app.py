import os
from flask import Flask, render_template, request, jsonify
from utils.pdf_utils import convert_to_pdf  
from utils.pdb_utils import process_pdb_file  
from utils.csv_utils import save_results_to_csv  
from utils.file_utils import download_file  
from utils.upload_utils import upload_file  
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use 'Agg' for non-GUI backend
import matplotlib.pyplot as plt
import io
import seaborn as sns
from datetime import datetime
import logging

# Import the generate_ramachandran_plot function from the new module
from utils.ramachandran_plot import generate_ramachandran_plot

app = Flask(__name__)

# Use Vercel's /tmp directory for file uploads
UPLOAD_FOLDER = '/tmp/uploads'
RESULT_FOLDER = '/tmp/results'

# Create the directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file_route():
    # Check if the 'file' field is present in the request
    file = request.files.get('file')
    
    if file is None:
        return jsonify({'error': 'No file selected'}), 400

    # Call the upload_file function to process the uploaded file
    results = upload_file(file, UPLOAD_FOLDER, RESULT_FOLDER)
    
    # If the function returns an error, respond accordingly
    if isinstance(results, dict) and 'error' in results:
        return jsonify(results), 400
    
    # If successful, return the results
    return jsonify(results)

@app.route('/download/<string:filetype>/<string:filename>')
def download_file_route(filetype, filename):
    return download_file(filetype, filename, RESULT_FOLDER)

@app.route('/generate_plot/<string:pdb_code>', methods=['GET'])
def generate_plot(pdb_code):
    try:
        return generate_ramachandran_plot(pdb_code, RESULT_FOLDER)
    except Exception as e:
        return jsonify({'error': f"Error generating Ramachandran plot: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
