import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
from flask import send_file

def generate_ramachandran_plot(pdb_code, result_folder):
    try:
        # Read the CSV file containing Phi and Psi angles
        csv_file = os.path.join(result_folder, f"{pdb_code}_angles.csv")
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
        raise ValueError(f"Error generating Ramachandran plot: {str(e)}")
