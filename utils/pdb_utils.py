import Bio.PDB
import math

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
