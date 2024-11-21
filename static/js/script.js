const form = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const resultsDiv = document.getElementById('results');
const resultsBody = document.getElementById('resultsBody');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');
const fileErrorDiv = document.getElementById('fileError');  // Error div for file validation

let uploadedFilename = '';  // To store the uploaded file's base name

function toggleVisibility(elements, isVisible) {
    elements.forEach(element => {
        element.style.display = isVisible ? 'block' : 'none';
    });
}

function clearResults() {
    resultsBody.innerHTML = '';
}

function validateFileType() {
    const file = fileInput.files[0];
    if (file && !file.name.toLowerCase().endsWith('.pdb')) {
        fileErrorDiv.style.display = 'block';  // Show error if file type is not .pdb
        fileInput.value = '';  // Clear file input
        return false;
    }
    fileErrorDiv.style.display = 'none';  // Hide error if valid file
    return true;
}

function validateFileSize() {
    const file = fileInput.files[0];
    const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB max size
    if (file && file.size > MAX_FILE_SIZE) {
        errorDiv.textContent = 'File size exceeds the maximum allowed size of 10MB.';
        toggleVisibility([errorDiv], true);
        fileInput.value = '';  // Clear file input
        return false;
    }
    return true;
}

async function handleFormSubmit(e) {
    e.preventDefault();

    // Validate file before proceeding
    if (!validateFileType() || !validateFileSize()) return;

    toggleVisibility([resultsDiv, errorDiv], false);
    clearResults();
    toggleVisibility([loadingDiv], true);

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch('/upload', { method: 'POST', body: formData });
        const responseBody = await response.json();

        toggleVisibility([loadingDiv], false);

        if (response.ok) {
            uploadedFilename = `${responseBody[0]['PDB Code']}_angles.csv`;  // Set filename for download
            populateResults(responseBody);
            toggleVisibility([resultsDiv], true);
        } else {
            throw new Error(responseBody.error || 'An error occurred while processing the file.');
        }
    } catch (error) {
        toggleVisibility([loadingDiv], false);
        errorDiv.textContent = error.message;
        toggleVisibility([errorDiv], true);
    }
}

function populateResults(data) {
    const rows = data.map(({ 'PDB Code': pdbCode, 'Chain ID': chainID, 'Residue': residue, 'Residue ID': residueID, 'Phi (°)': phi, 'Psi (°)': psi }) => {
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
    window.location.href = downloadUrl;  // Trigger the file download
}

fileInput.addEventListener('change', () => {
    validateFileType(); 
    validateFileSize();
});  // Event listener for file input change

form.addEventListener('submit', handleFormSubmit);
