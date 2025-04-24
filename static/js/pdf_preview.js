// PDF Preview functionality using PDF.js
function initPdfPreview(pdfUrl) {
    // Get the container element
    const container = document.getElementById('pdf-preview');
    container.innerHTML = '';
    
    // Load the PDF.js viewer dynamically
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.min.js';
    script.onload = function() {
        const pdfjsLib = window['pdfjs-dist/build/pdf'];
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';
        
        loadPdf(pdfUrl, pdfjsLib, container);
    };
    document.head.appendChild(script);
}

function loadPdf(pdfUrl, pdfjsLib, container) {
    // Load the PDF document
    const loadingTask = pdfjsLib.getDocument(pdfUrl);
    
    loadingTask.promise.then(function(pdf) {
        // Create a preview for the first 5 pages (or fewer if the document has fewer pages)
        const numPages = Math.min(pdf.numPages, 5);
        
        // Add page count indicator
        const pageCount = document.createElement('div');
        pageCount.className = 'text-center text-muted mb-2';
        pageCount.textContent = `Document has ${pdf.numPages} page(s)`;
        container.appendChild(pageCount);
        
        // Create preview container
        const previewPages = document.createElement('div');
        previewPages.className = 'preview-pages';
        container.appendChild(previewPages);
        
        // Load each page
        for (let i = 1; i <= numPages; i++) {
            renderPage(pdf, i, previewPages);
        }
        
        // Add note if showing only a preview
        if (pdf.numPages > 5) {
            const previewNote = document.createElement('div');
            previewNote.className = 'text-center text-muted mt-3';
            previewNote.textContent = 'Showing first 5 pages as preview. Download the file to see all pages.';
            container.appendChild(previewNote);
        }
    }).catch(function(error) {
        console.error('Error loading PDF:', error);
        
        // Show error message
        const errorMsg = document.createElement('div');
        errorMsg.className = 'alert alert-danger';
        errorMsg.textContent = 'Error loading PDF preview. Please try again or download the file.';
        container.appendChild(errorMsg);
    });
}

function renderPage(pdf, pageNumber, container) {
    // Get the page
    pdf.getPage(pageNumber).then(function(page) {
        // Create a wrapper for this page
        const pageWrapper = document.createElement('div');
        pageWrapper.className = 'pdf-page-wrapper mb-4';
        
        // Create page number indicator
        const pageNum = document.createElement('div');
        pageNum.className = 'page-number badge bg-secondary';
        pageNum.textContent = `Page ${pageNumber}`;
        pageWrapper.appendChild(pageNum);
        
        // Create canvas for the page
        const canvas = document.createElement('canvas');
        pageWrapper.appendChild(canvas);
        container.appendChild(pageWrapper);
        
        // Get the context
        const context = canvas.getContext('2d');
        
        // Set scale
        const viewport = page.getViewport({ scale: 0.8 });
        canvas.height = viewport.height;
        canvas.width = viewport.width;
        
        // Render the page
        const renderContext = {
            canvasContext: context,
            viewport: viewport
        };
        
        page.render(renderContext);
    });
}
