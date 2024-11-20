const form = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const resultsDiv = document.getElementById('results');
const resultsBody = document.getElementById('resultsBody');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');

// Show/Hide elements utility
function toggleVisibility(element, isVisible) {
    element.style.display = isVisible ? 'block' : 'none';
}

// Clear the results body
function clearResults() {
    resultsBody.innerHTML = '';
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();

    // Reset states
    toggleVisibility(resultsDiv, false);
    toggleVisibility(errorDiv, false);
    clearResults();
    toggleVisibility(loadingDiv, true);

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const data = await uploadFile(formData);
        toggleVisibility(loadingDiv, false);

        if (data.length > 0) {
            populateResults(data);
            toggleVisibility(resultsDiv, true);
        } else {
            throw new Error('No valid results found.');
        }
    } catch (error) {
        toggleVisibility(loadingDiv, false);
        errorDiv.textContent = error.message;
        toggleVisibility(errorDiv, true);
    }
}

// Upload file function
async function uploadFile(formData) {
    const response = await fetch('/upload', {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Something went wrong');
    }

    return response.json();
}

// Populate the results table
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

// Download file function
function download(filetype) {
    const filename = `${fileInput.files[0].name.split('.')[0]}_angles.csv`;
    window.location.href = `/download/${filetype}/${filename}`;
}

// Event listener
form.addEventListener('submit', handleFormSubmit);
