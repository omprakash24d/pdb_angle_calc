const form = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const resultsDiv = document.getElementById('results');
const resultsBody = document.getElementById('resultsBody');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');

let uploadedFilename = '';  // To store the uploaded file's base name

function toggleVisibility(element, isVisible) {
    element.style.display = isVisible ? 'block' : 'none';
}

function clearResults() {
    resultsBody.innerHTML = '';
}

async function handleFormSubmit(e) {
    e.preventDefault();

    toggleVisibility(resultsDiv, false);
    toggleVisibility(errorDiv, false);
    clearResults();
    toggleVisibility(loadingDiv, true);

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch('/upload', { method: 'POST', body: formData });
        const responseBody = await response.json();

        toggleVisibility(loadingDiv, false);

        if (response.ok) {
            uploadedFilename = responseBody[0]['PDB Code'] + '_angles.csv';  // Set the filename for download
            populateResults(responseBody);
            toggleVisibility(resultsDiv, true);
        } else {
            throw new Error(responseBody.error || 'An error occurred.');
        }
    } catch (error) {
        toggleVisibility(loadingDiv, false);
        errorDiv.textContent = error.message;
        toggleVisibility(errorDiv, true);
    }
}

function populateResults(data) {
    data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row['PDB Code']}</td>
            <td>${row['Chain ID']}</td>
            <td>${row['Residue']}</td>
            <td>${row['Residue ID']}</td>
            <td>${row['Phi (°)']}</td>
            <td>${row['Psi (°)']}</td>
        `;
        resultsBody.appendChild(tr);
    });
}

// Download function to handle the file type and trigger download
function download(filetype) {
    const downloadUrl = `/download/${filetype}/${uploadedFilename}`;
    window.location.href = downloadUrl;  // Trigger the file download
}

form.addEventListener('submit', handleFormSubmit);
