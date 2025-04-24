document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const uploadForm = document.getElementById('upload-form');
    const processingForm = document.getElementById('processing-form');
    const fileInput = document.getElementById('document-input');
    const fileNameDisplay = document.getElementById('file-name');
    const processingOptions = document.getElementById('processing-options');
    const uploadProgress = document.getElementById('upload-progress');
    const processingProgress = document.getElementById('processing-progress');
    const previewContainer = document.getElementById('preview-container');
    const downloadBtn = document.getElementById('download-btn');
    const orientationSwitch = document.getElementById('orientation-switch');
    const orientationLabel = document.getElementById('orientation-label');
    
    // Store file info
    let currentFile = {
        path: null,
        name: null,
        id: null,
        type: null
    };
    
    let currentOutput = {
        path: null
    };
    
    // Upload form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const file = fileInput.files[0];
        if (!file) {
            showAlert('Please select a file', 'danger');
            return;
        }
        
        // Check file type
        const fileExt = file.name.split('.').pop().toLowerCase();
        if (!['pdf', 'doc', 'docx'].includes(fileExt)) {
            showAlert('Unsupported file type. Please upload PDF, DOC, or DOCX files.', 'danger');
            return;
        }
        
        // Show progress
        uploadProgress.classList.remove('d-none');
        
        // Create FormData
        const formData = new FormData();
        formData.append('document', file);
        
        // Send upload request
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            uploadProgress.classList.add('d-none');
            
            if (data.success) {
                // Store file info
                currentFile.path = data.file_path;
                currentFile.name = data.file_name;
                currentFile.id = data.file_id;
                currentFile.type = data.file_type;
                
                // Update UI
                fileNameDisplay.textContent = data.file_name;
                processingOptions.classList.remove('d-none');
                showAlert('File uploaded successfully!', 'success');
            } else {
                showAlert('Error: ' + data.error, 'danger');
            }
        })
        .catch(error => {
            uploadProgress.classList.add('d-none');
            showAlert('Error uploading file: ' + error.message, 'danger');
        });
    });
    
    // Processing form submission
    processingForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!currentFile.path) {
            showAlert('Please upload a file first', 'warning');
            return;
        }
        
        // Get form values
        const processingType = document.querySelector('input[name="processing-type"]:checked').value;
        const marginTop = document.getElementById('margin-top').value;
        const marginRight = document.getElementById('margin-right').value;
        const marginBottom = document.getElementById('margin-bottom').value;
        const marginLeft = document.getElementById('margin-left').value;
        const orientation = document.getElementById('orientation-switch').checked ? 'landscape' : 'portrait';
        
        // Show processing progress
        processingProgress.classList.remove('d-none');
        
        // Create request data
        const requestData = {
            file_path: currentFile.path,
            file_type: currentFile.type,
            processing_type: processingType,
            margin_top: marginTop,
            margin_right: marginRight,
            margin_bottom: marginBottom,
            margin_left: marginLeft,
            orientation: orientation
        };
        
        // Send processing request
        fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            processingProgress.classList.add('d-none');
            
            if (data.success) {
                // Store output path
                currentOutput.path = data.output_path;
                
                // Update preview
                previewContainer.classList.remove('d-none');
                initPdfPreview(data.preview_url);
                
                // Enable download button
                downloadBtn.classList.remove('d-none');
                downloadBtn.href = `/download/${data.preview_url.split('/').pop()}`;
                
                showAlert('Document processed successfully!', 'success');
            } else {
                showAlert('Error: ' + data.error, 'danger');
            }
        })
        .catch(error => {
            processingProgress.classList.add('d-none');
            showAlert('Error processing document: ' + error.message, 'danger');
        });
    });
    
    // Update orientation label when switch changes
    orientationSwitch.addEventListener('change', function() {
        orientationLabel.textContent = this.checked ? 'Landscape' : 'Portrait';
    });
    
    // Helper function to show alerts
    function showAlert(message, type) {
        const alertsContainer = document.getElementById('alerts');
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        alertsContainer.appendChild(alert);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    }
    
    // File input change event to update UI
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            const fileName = this.files[0].name;
            const fileLabel = document.querySelector('.custom-file-label');
            if (fileLabel) {
                fileLabel.textContent = fileName;
            }
        }
    });
});
