from fpdf import FPDF

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
