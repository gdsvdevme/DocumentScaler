// Funcionalidade de pré-visualização de PDF usando PDF.js
function initPdfPreview(pdfUrl) {
    // Obter o elemento container
    const container = document.getElementById('pdf-preview');
    container.innerHTML = '';
    
    // Carregar o visualizador PDF.js dinamicamente
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
    // Carregar o documento PDF
    const loadingTask = pdfjsLib.getDocument(pdfUrl);
    
    loadingTask.promise.then(function(pdf) {
        // Criar uma pré-visualização para as primeiras 5 páginas (ou menos se o documento tiver menos páginas)
        const numPages = Math.min(pdf.numPages, 5);
        
        // Adicionar indicador de contagem de páginas
        const pageCount = document.createElement('div');
        pageCount.className = 'text-center text-muted mb-2';
        pageCount.textContent = `O documento tem ${pdf.numPages} página(s)`;
        container.appendChild(pageCount);
        
        // Criar container de pré-visualização
        const previewPages = document.createElement('div');
        previewPages.className = 'preview-pages';
        container.appendChild(previewPages);
        
        // Carregar cada página
        for (let i = 1; i <= numPages; i++) {
            renderPage(pdf, i, previewPages);
        }
        
        // Adicionar nota se estiver mostrando apenas uma pré-visualização
        if (pdf.numPages > 5) {
            const previewNote = document.createElement('div');
            previewNote.className = 'text-center text-muted mt-3';
            previewNote.textContent = 'Mostrando as primeiras 5 páginas como pré-visualização. Baixe o arquivo para ver todas as páginas.';
            container.appendChild(previewNote);
        }
    }).catch(function(error) {
        console.error('Erro ao carregar PDF:', error);
        
        // Mostrar mensagem de erro
        const errorMsg = document.createElement('div');
        errorMsg.className = 'alert alert-danger';
        errorMsg.textContent = 'Erro ao carregar a pré-visualização do PDF. Por favor, tente novamente ou baixe o arquivo.';
        container.appendChild(errorMsg);
    });
}

function renderPage(pdf, pageNumber, container) {
    // Obter a página
    pdf.getPage(pageNumber).then(function(page) {
        // Criar um wrapper para esta página
        const pageWrapper = document.createElement('div');
        pageWrapper.className = 'pdf-page-wrapper mb-4';
        
        // Criar indicador de número de página
        const pageNum = document.createElement('div');
        pageNum.className = 'page-number badge bg-secondary';
        pageNum.textContent = `Página ${pageNumber}`;
        pageWrapper.appendChild(pageNum);
        
        // Criar canvas para a página
        const canvas = document.createElement('canvas');
        pageWrapper.appendChild(canvas);
        container.appendChild(pageWrapper);
        
        // Obter o contexto
        const context = canvas.getContext('2d');
        
        // Definir escala
        const viewport = page.getViewport({ scale: 0.8 });
        canvas.height = viewport.height;
        canvas.width = viewport.width;
        
        // Renderizar a página
        const renderContext = {
            canvasContext: context,
            viewport: viewport
        };
        
        page.render(renderContext);
    });
}
