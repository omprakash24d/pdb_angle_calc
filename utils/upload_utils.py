import os
from utils.pdb_utils import process_pdb_file  # Import the function from pdb_utils.py
from utils.csv_utils import save_results_to_csv  # Import the function from csv_utils.py

def upload_file(file, upload_folder, result_folder):
    """Handles the file upload and processing of PDB files."""
    if file is None:
        return {'error': 'No file selected'}, 400
    if file.filename == '':
        return {'error': 'No selected file'}, 400

    filepath = os.path.join(upload_folder, file.filename)
    try:
        file.save(filepath)  # Save the uploaded file
        pdb_code = os.path.splitext(file.filename)[0]

        # Process the PDB file and save the results as CSV
        results = process_pdb_file(filepath, pdb_code)  
        result_csv = save_results_to_csv(results, pdb_code, result_folder)
        
    except Exception as e:
        return {'error': f"An error occurred: {str(e)}"}, 500

    return results
