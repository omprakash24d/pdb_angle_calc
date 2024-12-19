import os
from flask import Flask, render_template, request, jsonify, send_file
from utils.pdf_utils import convert_to_pdf  
from utils.pdb_utils import process_pdb_file  
from utils.csv_utils import save_results_to_csv  
from utils.file_utils import download_file  
from utils.upload_utils import upload_file  
from utils.ramachandran_plot import generate_ramachandran_plot
import logging

app = Flask(__name__)

UPLOAD_FOLDER = '/tmp/uploads'
RESULT_FOLDER = '/tmp/results'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file_route():
    file = request.files.get('file')
    
    if file is None:
        return jsonify({'error': 'No file selected'}), 400

    results = upload_file(file, UPLOAD_FOLDER, RESULT_FOLDER)
    
    if isinstance(results, dict) and 'error' in results:
        return jsonify(results), 400
    
    return jsonify(results)

@app.route('/download/<string:filetype>/<string:filename>')
def download_file_route(filetype, filename):
    return download_file(filetype, filename, RESULT_FOLDER)

@app.route('/generate_plot/<string:pdb_code>', methods=['GET'])
def generate_plot(pdb_code):
    try:
        download = request.args.get('download', default=False, type=bool)
        logging.debug(f"Request to generate Ramachandran plot for PDB code: {pdb_code}")
        return generate_ramachandran_plot(pdb_code, RESULT_FOLDER, download)
    except Exception as e:
        logging.error(f"Error generating Ramachandran plot: {str(e)}")
        return jsonify({'error': f"Error generating Ramachandran plot: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
