// Elements
const form = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const pdbIdInput = document.getElementById('pdbIdInput');
const resultsDiv = document.getElementById('results');
const resultsBody = document.getElementById('resultsBody');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');
const fileErrorDiv = document.getElementById('fileError');
const pdbIdErrorDiv = document.getElementById('pdbIdError');

let uploadedFilename = ''; // Stores the uploaded file's base name

// Helper to toggle visibility
function toggleVisibility(elements, isVisible) {
    elements.forEach(element => {
        element.style.display = isVisible ? 'block' : 'none';
    });
}

// Clears previous results
function clearResults() {
    resultsBody.innerHTML = '';
}

// Validate file type (only .pdb)
function validateFileType(file) {
    if (file && !file.name.toLowerCase().endsWith('.pdb')) {
        fileErrorDiv.style.display = 'block';
        fileInput.value = ''; // Clear the file input
        return false;
    }
    fileErrorDiv.style.display = 'none';
    return true;
}

// Validate file size (10MB max)
function validateFileSize(file) {
    const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB max size
    if (file && file.size > MAX_FILE_SIZE) {
        errorDiv.textContent = 'File size exceeds the maximum allowed size of 10MB.';
        toggleVisibility([errorDiv], true);
        fileInput.value = ''; // Clear the file input
        return false;
    }
    return true;
}

// Validate PDB ID format (4 alphanumeric characters)
function validatePdbId() {
    const pdbId = pdbIdInput.value.trim();
    const pdbIdPattern = /^[A-Za-z0-9]{4}$/;
    if (!pdbIdPattern.test(pdbId)) {
        pdbIdErrorDiv.style.display = 'block';
        return false;
    }
    pdbIdErrorDiv.style.display = 'none';
    return true;
}

// Handle input method change (toggle visibility of inputs)
function handleInputMethodChange() {
    const isPdbIdSelected = document.getElementById('pdbIdOption').checked;
    const isFileSelected = document.getElementById('fileOption').checked;

    // Clear error messages when switching methods
    toggleVisibility([pdbIdErrorDiv, fileErrorDiv, errorDiv], false);

    if (isPdbIdSelected) {
        fileInput.value = ''; // Clear file input
        toggleVisibility([document.getElementById('fileInputDiv')], false);
        toggleVisibility([document.getElementById('pdbIdInputDiv')], true);
    } else if (isFileSelected) {
        pdbIdInput.value = ''; // Clear PDB ID input
        toggleVisibility([document.getElementById('fileInputDiv')], true);
        toggleVisibility([document.getElementById('pdbIdInputDiv')], false);
    }
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();

    const isPdbIdSelected = pdbIdInput.value.trim() !== '';
    const isFileSelected = fileInput.files.length > 0;

    // Validate the input fields
    if (isFileSelected && (!validateFileType(fileInput.files[0]) || !validateFileSize(fileInput.files[0]))) return;
    if (isPdbIdSelected && !validatePdbId()) return;

    toggleVisibility([resultsDiv, errorDiv], false);
    clearResults();
    toggleVisibility([loadingDiv], true);

    const formData = new FormData();
    let uploadUrl;

    try {
        if (isPdbIdSelected) {
            const pdbId = pdbIdInput.value.trim();
            const response = await fetch(`https://files.rcsb.org/download/${pdbId}.pdb`);

            if (!response.ok) {
                throw new Error('PDB file not found.');
            }

            const data = await response.text();
            const blob = new Blob([data], { type: "text/plain" });
            formData.append('file', blob, `${pdbId}.pdb`);
            uploadUrl = '/upload';
        } else {
            const file = fileInput.files[0];
            formData.append('file', file);
            uploadUrl = '/upload';
        }

        const uploadResponse = await fetch(uploadUrl, { method: 'POST', body: formData });
        const uploadResponseBody = await uploadResponse.json();

        toggleVisibility([loadingDiv], false);

        if (uploadResponse.ok) {
            uploadedFilename = `${uploadResponseBody[0]['PDB Code']}_angles.csv`;

            // Dynamically set the plot URL based on the uploaded pdb code
            const pdbCode = uploadResponseBody[0]['PDB Code'];
            const plotUrl = `/generate_plot/${pdbCode}`;

            // Set the image source
            const plotImg = document.getElementById('ramachandranPlot');
            plotImg.src = plotUrl;

            // Show the Ramachandran plot section
            document.getElementById('ramachandran_plot_section').style.display = 'block';

            // Enable the download button and set its link
            const downloadBtn = document.getElementById('downloadPlotBtn');
            downloadBtn.href = plotUrl;
            downloadBtn.style.display = 'inline-block'; // Show the download button

            populateResults(uploadResponseBody);
            toggleVisibility([resultsDiv], true);
        } else {
            throw new Error(uploadResponseBody.error || 'An error occurred while processing the file.');
        }
    } catch (error) {
        toggleVisibility([loadingDiv], false);
        errorDiv.textContent = error.message;
        toggleVisibility([errorDiv], true);
    }
}

// Populate results in the table after successful upload
function populateResults(data) {
    const rows = data.map(({ 'PDB Code': pdbCode, 'Chain ID': chainID, 'Residue': residue, 'Residue ID': residueID, 'Phi (\u00b0)': phi, 'Psi (\u00b0)': psi }) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${pdbCode}</td>
            <td>${chainID}</td>
            <td>${residue}</td>
            <td>${residueID}</td>
            <td>${phi}</td>
            <td>${psi}</td>
        `;
        return tr;
    });
    resultsBody.append(...rows);
}

// Download function to handle file download
function download(filetype) {
    const downloadUrl = `/download/${filetype}/${uploadedFilename}`;
    window.location.href = downloadUrl;
}

// Event listener for file input change to trigger validation
fileInput.addEventListener('change', () => {
    validateFileType(fileInput.files[0]);
    validateFileSize(fileInput.files[0]);
});

// Listen for form submit to trigger file upload handling
form.addEventListener('submit', handleFormSubmit);

// Listen for changes in radio buttons to toggle the input method
document.querySelectorAll('input[name="inputOption"]').forEach((radio) => {
    radio.addEventListener('change', handleInputMethodChange);
});

// Initialize form visibility based on selected radio option
handleInputMethodChange();

// Adjust display style for mobile users (if needed)
if (window.innerWidth <= 768) {
    document.querySelectorAll('.form-check').forEach((check) => {
        check.classList.add('d-flex', 'flex-column');
    });
}