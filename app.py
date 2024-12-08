import os
import tempfile
from flask import Flask, render_template, request, jsonify, send_file
import Bio.PDB
import math
import pandas as pd
from fpdf import FPDF

app = Flask(__name__)

# Use Vercel's /tmp directory for file uploads
UPLOAD_FOLDER = '/tmp/uploads'
RESULT_FOLDER = '/tmp/results'

# Create the directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

def degrees(rad_angle):
    """Converts any angle in radians to degrees."""
    if rad_angle is None:
        return None
    angle = rad_angle * 180 / math.pi
    return (angle + 180) % 360 - 180  # Normalize angle to [-180, 180]

def process_pdb_file(filepath, pdb_code):
    """Processes a PDB file to extract angles and save results to a CSV."""
    results = []
    try:
        # Initialize PDB parser and CaPPBuilder only once to avoid unnecessary reinitialization
        parser = Bio.PDB.PDBParser()
        capp_builder = Bio.PDB.CaPPBuilder()

        structure = parser.get_structure(pdb_code, filepath)
        for model in structure:
            for chain in model:
                polypeptides = capp_builder.build_peptides(chain)
                for poly in polypeptides:
                    phi_psi = poly.get_phi_psi_list()
                    for residue, (phi, psi) in zip(poly, phi_psi):
                        # Check if phi and psi are available
                        if phi and psi:
                            result = {
                                "PDB Code": pdb_code,
                                "Chain ID": chain.id,
                                "Residue": residue.resname,
                                "Residue ID": residue.id[1],
                                "Phi (°)": degrees(phi),
                                "Psi (°)": degrees(psi),
                            }
                        else:
                            # If phi or psi is missing, mark residue as "Missing Residue"
                            result = {
                                "PDB Code": pdb_code,
                                "Chain ID": chain.id,
                                "Residue": "Missing Residue",  # Mark missing residues
                                "Residue ID": residue.id[1],
                                "Phi (°)": None,  # Missing value for Phi
                                "Psi (°)": None,  # Missing value for Psi
                            }
                        results.append(result)
    except Exception as e:
        raise ValueError(f"Error processing PDB file: {str(e)}")
    return results


def save_results_to_csv(results, pdb_code):
    """Saves the results to a CSV file."""
    result_csv = os.path.join(RESULT_FOLDER, f"{pdb_code}_angles.csv")
    df = pd.DataFrame(results)
    df.to_csv(result_csv, index=False)
    return result_csv

def convert_to_pdf(df, filepath):
    """Converts the data frame to a PDF file."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font('Arial', size=12)

    for i, row in df.iterrows():
        pdf.cell(0, 10, f"{row.to_dict()}", ln=True)
    pdf.output(filepath)
    return filepath

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    pdb_code = os.path.splitext(file.filename)[0]

    try:
        results = process_pdb_file(filepath, pdb_code)
        result_csv = save_results_to_csv(results, pdb_code)
    except ValueError as e:
        return jsonify({'error': str(e)}), 500

    return jsonify(results)

@app.route('/download/<string:filetype>/<string:filename>')
def download_file(filetype, filename):
    filepath = os.path.join(RESULT_FOLDER, filename)

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        return jsonify({'error': f"Error reading file: {str(e)}"}), 500

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
        pdf_path = convert_to_pdf(df, pdf_path)
        return send_file(pdf_path, as_attachment=True)
    else:
        return jsonify({'error': 'Invalid file type'}), 400
