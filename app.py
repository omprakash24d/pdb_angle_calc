import os
from flask import Flask, render_template, request, jsonify, send_file
import Bio.PDB
import math
import pandas as pd
from fpdf import FPDF
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use 'Agg' for non-GUI backend
import matplotlib.pyplot as plt
import io
import seaborn as sns



app = Flask(__name__)

UPLOAD_FOLDER = '/tmp/uploads'
RESULT_FOLDER = '/tmp/results'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
def get_result_path(filename, extension):
    return os.path.join(RESULT_FOLDER, f"{filename}.{extension}")


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


@app.route('/generate_plot/<string:pdb_code>', methods=['GET'])
def generate_ramachandran_plot(pdb_code):
    try:
        # Read the CSV file containing Phi and Psi angles
        csv_file = os.path.join(RESULT_FOLDER, f"{pdb_code}_angles.csv")
        df = pd.read_csv(csv_file)
        
        # Filter out rows where Phi or Psi is missing
        valid_data = df.dropna(subset=['Phi (°)', 'Psi (°)'])
        
        # Convert Phi and Psi to radians for plotting
        phi = valid_data['Phi (°)'].apply(lambda x: np.deg2rad(x))
        psi = valid_data['Psi (°)'].apply(lambda x: np.deg2rad(x))

        # Create Ramachandran plot with enhanced styling
        sns.set(style="whitegrid", palette="muted")  # Seaborn styling for smooth design
        plt.figure(figsize=(12, 10))

        # Define regions: favored, allowed, and disallowed
        favored = [(-np.pi/2, -np.pi/4), (-np.pi/4, 0), (0, np.pi/4), (np.pi/4, np.pi/2)]
        allowed = [(-np.pi, -np.pi/2), (np.pi/2, np.pi)]
        disallowed = [(-np.pi, np.pi)]  # All angles that don't fit in allowed regions

        # Scatter plot with gradient coloring
        scatter = plt.scatter(phi, psi, c=phi + psi, cmap="twilight", s=50, alpha=0.8, edgecolors='w', linewidth=0.5, label="Residues")

        # Highlight favored regions with semi-transparent gradient fill
        for region in favored:
            plt.fill_betweenx(
                y=[-np.pi, np.pi],
                x1=region[0], x2=region[1],
                color='lightgreen', alpha=0.4, label="Favored Regions"
            )
            plt.plot([region[0], region[0]], [-np.pi, np.pi], color='darkgreen', lw=2, ls='--')  # Border for the region

        # Highlight allowed regions with semi-transparent blue fill
        for region in allowed:
            plt.fill_betweenx(
                y=[-np.pi, np.pi],
                x1=region[0], x2=region[1],
                color='skyblue', alpha=0.3, label="Allowed Regions"
            )
            plt.plot([region[0], region[0]], [-np.pi, np.pi], color='blue', lw=2, ls='--')  # Border for the region

        # Highlight disallowed regions with semi-transparent red fill
        for region in disallowed:
            plt.fill_betweenx(
                y=[-np.pi, np.pi],
                x1=region[0], x2=region[1],
                color='lightcoral', alpha=0.3, label="Disallowed Regions"
            )
            plt.plot([region[0], region[0]], [-np.pi, np.pi], color='red', lw=2, ls='--')  # Border for the region

        # Set axis limits, labels, and title with custom font styles
        plt.xlim(-np.pi, np.pi)
        plt.ylim(-np.pi, np.pi)
        plt.xlabel('Phi (Φ) Angle (radians)', fontsize=16, fontweight='bold', family='Arial')
        plt.ylabel('Psi (Ψ) Angle (radians)', fontsize=16, fontweight='bold', family='Arial')
        plt.title(f'Ramachandran Plot for {pdb_code}', fontsize=20, fontweight='bold', family='Arial')

        # Add a color bar to show the color map for the scatter points
        cbar = plt.colorbar(scatter)
        cbar.set_label('Sum of Phi and Psi', rotation=270, fontsize=14, labelpad=20)

        # Fine-tune the grid: alternating dotted and solid gridlines for visual aesthetics
        plt.grid(True, which='major', linestyle='-', alpha=0.5, color='black', linewidth=1)
        plt.grid(True, which='minor', linestyle=':', alpha=0.5, color='gray', linewidth=0.8)  # Dotted gridlines for precision

        # Set minor ticks for finer grid control
        plt.minorticks_on()
        
        # Add annotations to point out specific regions of interest
        plt.annotate('Favored Regions', xy=(-1.5, 0), xytext=(-2, 0.5),
                     color='darkgreen', fontsize=14, fontweight='bold',
                     arrowprops=dict(facecolor='green', arrowstyle="->"))
        plt.annotate('Allowed Regions', xy=(0.5, -1), xytext=(1, -2),
                     color='blue', fontsize=14, fontweight='bold',
                     arrowprops=dict(facecolor='blue', arrowstyle="->"))
        plt.annotate('Disallowed Regions', xy=(-2, -2), xytext=(-3, -3),
                     color='red', fontsize=14, fontweight='bold',
                     arrowprops=dict(facecolor='red', arrowstyle="->"))

        # Set custom tick parameters for better readability
        plt.xticks(np.arange(-np.pi, np.pi+np.pi/4, np.pi/4), fontsize=12)
        plt.yticks(np.arange(-np.pi, np.pi+np.pi/4, np.pi/4), fontsize=12)

        # Add region labels in text (with background highlight)
        plt.text(-1.7, 1.5, "Favored Regions", fontsize=14, color='green', bbox=dict(facecolor='white', alpha=0.5))
        plt.text(1.7, -1.5, "Allowed Regions", fontsize=14, color='blue', bbox=dict(facecolor='white', alpha=0.5))
        plt.text(-2.5, -2.5, "Disallowed Regions", fontsize=14, color='red', bbox=dict(facecolor='white', alpha=0.5))

        # Remove duplicate legends and show only distinct labels
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize=14)

        # Save plot to a BytesIO object with tight bounding box
        img_io = io.BytesIO()
        plt.savefig(img_io, format='png', bbox_inches='tight')
        img_io.seek(0)
        plt.close()

        # Return the image as a response
        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        return jsonify({'error': f"Error generating Ramachandran plot: {str(e)}"}), 500


def save_results_to_csv(results, pdb_code):
    """Saves the results to a CSV file."""
    result_csv = os.path.join(RESULT_FOLDER, f"{pdb_code}_angles.csv")
    df = pd.DataFrame(results)
    df.to_csv(result_csv, index=False)
    return result_csv

def convert_to_pdf(df, filepath):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Add first page
    pdf.add_page()

    # Add Header with page number (page number will be handled for each page)
    pdf.set_font('Arial', 'B', 12)  # Bold font for header
    pdf.cell(0, 10, 'PDB Data Report', 0, 1, 'C')

    # Add second heading (subheading below main title)
    pdf.set_font('Arial', 'I', 10)  # Italic font for subheading
    pdf.cell(0, 10, 'Generated Data for PDB Entries', 0, 1, 'C')
    pdf.ln(10)  # Add some space after the subheading

    # A4 page width (210mm), minus margins (15mm each)
    page_width = pdf.w - 2 * 15  # 180mm usable width for content
    n_cols = len(df.columns)

    # Calculate column widths to utilize the full page width
    total_data_width = sum([max(df[col].astype(str).apply(len).max(), len(col)) for col in df.columns])

    # Proportionally scale column widths to fit within the page width
    col_widths = []
    for col in df.columns:
        max_len = max(df[col].astype(str).apply(len).max(), len(col))
        proportional_width = (max_len / total_data_width) * page_width
        col_widths.append(proportional_width)

    # Add header row with bold and background color
    pdf.set_fill_color(200, 220, 255)  # Light blue background for header
    pdf.set_font('Arial', 'B', 10)  # Bold font for headers
    for i, col in enumerate(df.columns):
        pdf.cell(col_widths[i], 10, col, border=1, align='C', fill=True)
    pdf.ln()

    # Add data rows
    pdf.set_font('Arial', size=10)  # Regular font for data
    for _, row in df.iterrows():
        for i, val in enumerate(row):
            # If it's the first column, align left
            align = 'L' if i == 0 else 'C'
            pdf.cell(col_widths[i], 10, str(val), border=1, align=align)
        pdf.ln()

    # Add footer with custom text
    pdf.set_y(-15)  # Position 15mm from the bottom
    pdf.set_font('Arial', 'I', 8)  # Italic font for footer text
    pdf.cell(0, 10, 'Report generated at pdb.indhinditech.com', 0, 0, 'C')
    
    # Add page number
    pdf.set_font('Arial', 'I', 8)  # Page number font
    pdf.cell(0, 10, f"Page {pdf.page_no()}", 0, 0, 'R')

    # Output the PDF to the specified filepath
    pdf.output(filepath)
    return filepath


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file Selected'}), 400
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
