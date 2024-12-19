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
const radioButtons = document.querySelectorAll('input[name="inputOption"]');
const formChecks = document.querySelectorAll('.form-check');

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
    const pdbId = pdbIdInput.value.trim(); // Get and trim input value
    const pdbIdPattern = /^[A-Za-z0-9]{4}$/; // Pattern for 4 alphanumeric characters

    // If the PDB ID does not match the pattern
    if (!pdbIdPattern.test(pdbId)) {
        // Show error message
        pdbIdErrorDiv.style.display = 'block';
        // Highlight the input field with a red border
        pdbIdInput.classList.add('invalid');
        return false;
    }

    // If the PDB ID is valid
    pdbIdErrorDiv.style.display = 'none';
    // Remove the invalid class (if any)
    pdbIdInput.classList.remove('invalid');
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

// Helper function to handle errors
function handleError(message) {
    toggleVisibility([loadingDiv], false);
    errorDiv.textContent = message;
    toggleVisibility([errorDiv], true);
}

// Helper function for input validation
function validateInputs(isFileSelected, isPdbIdSelected) {
    if (isFileSelected) {
        const file = fileInput.files[0];
        if (!validateFileType(file) || !validateFileSize(file)) {
            return 'Invalid file type or size.';
        }
    }
    if (isPdbIdSelected && !validatePdbId()) {
        return 'Invalid PDB ID.';
    }
    return null; // No error
}

// Helper function to append PDB file to form data
async function getPdbFile(pdbId) {
    try {
        const response = await fetch(`https://files.rcsb.org/download/${pdbId}.pdb`);
        if (!response.ok) {
            throw new Error('PDB file not found.');
        }
        const data = await response.text();
        const blob = new Blob([data], { type: "text/plain" });
        return { blob, filename: `${pdbId}.pdb` };
    } catch (error) {
        throw new Error(`Error fetching PDB file: ${error.message}`);
    }
}

// Helper function to create a spinner or loading message
function showLoadingMessage(message = 'Fetching PDB File...') {
    const spinnerDiv = document.getElementById('loadingMessage');
    spinnerDiv.textContent = message;
    toggleVisibility([loadingDiv, spinnerDiv], true);
}

// Main function to handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();

    const isPdbIdSelected = pdbIdInput.value.trim() !== '';
    const isFileSelected = fileInput.files.length > 0;

    // Validate the input fields
    if (isFileSelected && (!validateFileType(fileInput.files[0]) || !validateFileSize(fileInput.files[0]))) return;
    if (isPdbIdSelected && !validatePdbId()) return;

    toggleVisibility([resultsDiv, errorDiv], false);
    clearResults();
    
    // Show loading message while processing
    toggleVisibility([loadingMessage], true);

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

        // Perform the file upload
        const uploadResponse = await fetch(uploadUrl, { method: 'POST', body: formData });
        const uploadResponseBody = await uploadResponse.json();

        // Hide loading message after upload completion
        toggleVisibility([loadingMessage], false);

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
        // Hide loading message if there's an error
        toggleVisibility([loadingMessage], false);
        errorDiv.textContent = error.message;
        toggleVisibility([errorDiv], true);
    }
}


// File size validation function to check for large files
function validateFileSize(file) {
    const MAX_FILE_SIZE_MB = 50; // Max file size in MB
    const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024; // Convert MB to Bytes
    
    // Convert file size to MB for user-friendly display
    const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2); // Convert bytes to MB

    // Check if the file size exceeds the limit
    if (file.size > MAX_FILE_SIZE_BYTES) {
        // Provide specific feedback with the file size info
        handleError(`File size of ${fileSizeMB}MB exceeds the ${MAX_FILE_SIZE_MB}MB limit.`);
        return false;
    }

    return true;
}

// Generic error handling function with user-friendly messages
function handleError(message) {
    // Display the error message in the error div (you can update this as needed)
    const errorDiv = document.getElementById('errorDiv');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

// Disable submit button when file is too large
function disableSubmitButton() {
    const submitButton = document.getElementById('submitButton');
    submitButton.disabled = true;
    submitButton.style.opacity = 0.5; // Reduce opacity to show the button is disabled
}

// Enable submit button when file passes validation
function enableSubmitButton() {
    const submitButton = document.getElementById('submitButton');
    submitButton.disabled = false;
    submitButton.style.opacity = 1; // Restore opacity to show the button is enabled
}

// Handle multiple files
function validateFiles(files) {
    for (let i = 0; i < files.length; i++) {
        if (!validateFileSize(files[i])) {
            return false; // Return false on the first invalid file
        }
    }
    enableSubmitButton(); // Enable button if all files are valid
    return true;
}

// Example file input change event
document.getElementById('fileInput').addEventListener('change', function(event) {
    const files = event.target.files;
    if (files.length > 0) {
        if (!validateFiles(files)) {
            disableSubmitButton(); // Disable button if any file is invalid
        }
    }
});



// Populate results in the table after successful upload
function populateResults(data) {
    if (!Array.isArray(data) || data.length === 0) {
        console.error("No valid data available for population.");
        return;
    }

    // Clear any existing rows in the results table body
    const resultsBody = document.getElementById('resultsBody');
    resultsBody.innerHTML = '';

    // Map the data and create table rows
    const rows = data.map(item => {
        const { 'PDB Code': pdbCode = '', 'Chain ID': chainID = '', 'Residue': residue = '', 'Residue ID': residueID = '', 'Phi (\u00b0)': phi = '', 'Psi (\u00b0)': psi = '' } = item;

        // Create a table row element
        const tr = document.createElement('tr');
        
        // Apply conditional styling for invalid or missing data
        if (!pdbCode || !chainID || !residue || !residueID || !phi || !psi) {
            tr.style.backgroundColor = 'rgba(255, 0, 0, 0.1)'; // Highlight invalid rows
        }

        tr.innerHTML = `
            <td title="${sanitize(pdbCode)}">${sanitize(pdbCode)}</td>
            <td title="${sanitize(chainID)}">${sanitize(chainID)}</td>
            <td title="${sanitize(residue)}">${sanitize(residue)}</td>
            <td title="${sanitize(residueID)}">${sanitize(residueID)}</td>
            <td title="${sanitize(phi)}">${sanitize(phi)}</td>
            <td title="${sanitize(psi)}">${sanitize(psi)}</td>
        `;

        return tr;
    });

    // Append all rows at once
    resultsBody.append(...rows);
}

// Function to sanitize data (escape HTML characters to prevent XSS)
function sanitize(input) {
    const element = document.createElement('div');
    if (input) {
        element.innerText = input;  // Using innerText to escape any HTML content
        element.textContent = input; // Assign textContent as well
    }
    return element.innerHTML;
}


// Download function to handle file download
function download(filetype) {
    if (!filetype || !uploadedFilename) {
        handleError('Invalid download request. File type or filename is missing.');
        return;
    }

    // Validate the file type before proceeding with the download
    const validFileTypes = ['csv', 'pdb', 'txt']; // Customize as needed
    const fileExtension = uploadedFilename.split('.').pop().toLowerCase();
    
    if (!validFileTypes.includes(fileExtension)) {
        handleError(`Invalid file type requested. Supported types are: ${validFileTypes.join(', ')}`);
        return;
    }

    const downloadUrl = `/download/${filetype}/${encodeURIComponent(uploadedFilename)}`;

    // Show loading indicator or message to the user
    toggleDownloadLoading(true);

    // Timeout handler to ensure the download doesn't hang indefinitely
    const timeout = setTimeout(() => {
        handleError('Download timed out. Please try again.');
        toggleDownloadLoading(false);
    }, 10000); // Timeout after 10 seconds

    // Attempt the download
    fetch(downloadUrl, { method: 'GET' })
        .then(response => {
            clearTimeout(timeout); // Clear the timeout if the download starts

            if (response.ok) {
                // If the response is okay, start the download by redirecting
                window.location.href = downloadUrl;
                notifyDownloadSuccess(); // Notify the user about download success
            } else {
                // Handle specific server errors (e.g., file not found)
                throw new Error(`Failed to initiate download. Server returned: ${response.statusText}`);
            }
        })
        .catch(error => {
            // Catch any errors like network issues or invalid responses
            handleError(`Error during download: ${error.message}`);
        })
        .finally(() => {
            // Hide the loading indicator after the download attempt is complete
            toggleDownloadLoading(false);
        });
}

// Function to toggle the download loading state (e.g., a spinner or message)
function toggleDownloadLoading(isLoading) {
    const downloadBtn = document.getElementById('downloadPlotBtn');
    if (isLoading) {
        downloadBtn.innerHTML = 'Downloading... <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
        downloadBtn.disabled = true;  // Disable button to prevent further clicks
    } else {
        downloadBtn.innerHTML = 'Download Plot';
        downloadBtn.disabled = false;  // Re-enable button after download is complete
    }
}

// Function to show a success notification after the download begins
function notifyDownloadSuccess() {
    const successMessage = document.createElement('div');
    successMessage.classList.add('alert', 'alert-success');
    successMessage.innerText = 'Download has started successfully!';
    document.body.appendChild(successMessage);

    setTimeout(() => {
        successMessage.remove(); // Remove the success message after a few seconds
    }, 3000);
}

// Handle errors by displaying a message (or any custom error handling logic)
function handleError(errorMessage) {
    const errorDiv = document.getElementById('errorDiv');
    errorDiv.textContent = errorMessage;
    toggleVisibility([errorDiv], true);
}


// Debounce function to limit how frequently a function is called
function debounce(func, wait = 300) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// File validation combined into one function
function validateFile(file) {
    const isValidType = validateFileType(file);
    const isValidSize = validateFileSize(file);
    return isValidType && isValidSize;  // Return true if both are valid
}

// File input change event listener with debouncing
fileInput.addEventListener('change', debounce(() => {
    const file = fileInput.files[0];
    if (file && !validateFile(file)) {
        // Handle validation errors here (e.g., show error tooltip)
        fileInput.classList.add('is-invalid');
        showErrorTooltip(fileInput, 'Invalid file. Please upload a valid .pdb file with size < 50MB.');
    } else {
        fileInput.classList.remove('is-invalid');
        clearErrorTooltip(fileInput);
    }
}, 500));

// Form submit event listener
form.addEventListener('submit', handleFormSubmit);

// Radio button change event listener to toggle input method
radioButtons.forEach(radio => {
    radio.addEventListener('change', handleInputMethodChange);
});

// Initialize form visibility based on selected radio option
handleInputMethodChange();

// Adjust display style for mobile users (using matchMedia for better performance)
const mediaQuery = window.matchMedia('(max-width: 768px)');

// Lazy load additional form sections on mobile (adjust as needed)
function lazyLoadFormSections() {
    if (mediaQuery.matches) {
        // Add logic to dynamically load sections for mobile users (e.g., show hidden fields)
        const moreFormSections = document.querySelectorAll('.lazy-load');
        moreFormSections.forEach(section => section.classList.remove('d-none'));
    }
}

// Adjust form layout for mobile display
function adjustForMobileDisplay() {
    formChecks.forEach(check => {
        if (mediaQuery.matches) {
            check.classList.add('d-flex', 'flex-column');
        } else {
            check.classList.remove('d-flex', 'flex-column');
        }
    });
}

// Listen for media query change
mediaQuery.addEventListener('change', () => {
    adjustForMobileDisplay();
    lazyLoadFormSections();
});

// Call the function initially
adjustForMobileDisplay();
lazyLoadFormSections();

// Error handling utility function to display errors in tooltips
function showErrorTooltip(element, message) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip bs-tooltip-top';
    tooltip.setAttribute('role', 'tooltip');
    tooltip.innerHTML = `<div class="tooltip-arrow"></div><div class="tooltip-inner">${message}</div>`;
    element.parentNode.appendChild(tooltip);
    $(element).tooltip({ title: message, placement: 'top' }).tooltip('show');
}

// Clear error tooltips
function clearErrorTooltip(element) {
    $(element).tooltip('dispose'); // Dispose the tooltip
}

// Lazy load functionality for form sections or other content (Optional)
function lazyLoadContent() {
    // Example of lazy-loading content as you scroll
    const contentSections = document.querySelectorAll('.lazy-load');
    contentSections.forEach(section => {
        if (section.getBoundingClientRect().top <= window.innerHeight) {
            section.classList.remove('d-none');
        }
    });
}

// Listen for scroll events for lazy loading (optional)
window.addEventListener('scroll', debounce(lazyLoadContent, 300));
