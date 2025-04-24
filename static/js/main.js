document.addEventListener('DOMContentLoaded', function() {
    // Elementos DOM
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
    
    // Armazenar informações do arquivo
    let currentFile = {
        path: null,
        name: null,
        id: null,
        type: null
    };
    
    let currentOutput = {
        path: null
    };
    
    // Envio do formulário de upload
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const file = fileInput.files[0];
        if (!file) {
            showAlert('Por favor, selecione um arquivo', 'danger');
            return;
        }
        
        // Verificar tipo de arquivo
        const fileExt = file.name.split('.').pop().toLowerCase();
        if (!['pdf', 'doc', 'docx'].includes(fileExt)) {
            showAlert('Tipo de arquivo não suportado. Por favor, envie arquivos PDF, DOC ou DOCX.', 'danger');
            return;
        }
        
        // Mostrar progresso
        uploadProgress.classList.remove('d-none');
        
        // Criar FormData
        const formData = new FormData();
        formData.append('document', file);
        
        // Enviar requisição de upload
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            uploadProgress.classList.add('d-none');
            
            if (data.success) {
                // Armazenar informações do arquivo
                currentFile.path = data.file_path;
                currentFile.name = data.file_name;
                currentFile.id = data.file_id;
                currentFile.type = data.file_type;
                
                // Atualizar UI
                fileNameDisplay.textContent = data.file_name;
                processingOptions.classList.remove('d-none');
                showAlert('Arquivo enviado com sucesso!', 'success');
            } else {
                showAlert('Erro: ' + data.error, 'danger');
            }
        })
        .catch(error => {
            uploadProgress.classList.add('d-none');
            showAlert('Erro ao enviar arquivo: ' + error.message, 'danger');
        });
    });
    
    // Envio do formulário de processamento
    processingForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!currentFile.path) {
            showAlert('Por favor, envie um arquivo primeiro', 'warning');
            return;
        }
        
        // Obter valores do formulário
        const processingType = document.querySelector('input[name="processing-type"]:checked').value;
        const marginTop = document.getElementById('margin-top').value;
        const marginRight = document.getElementById('margin-right').value;
        const marginBottom = document.getElementById('margin-bottom').value;
        const marginLeft = document.getElementById('margin-left').value;
        const orientation = document.getElementById('orientation-switch').checked ? 'landscape' : 'portrait';
        
        // Mostrar progresso de processamento
        processingProgress.classList.remove('d-none');
        
        // Criar dados da requisição
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
        
        // Enviar requisição de processamento
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
                // Armazenar caminho do arquivo de saída
                currentOutput.path = data.output_path;
                
                // Atualizar pré-visualização
                previewContainer.classList.remove('d-none');
                initPdfPreview(data.preview_url);
                
                // Habilitar botão de download
                downloadBtn.classList.remove('d-none');
                downloadBtn.href = `/download/${data.preview_url.split('/').pop()}`;
                
                showAlert('Documento processado com sucesso!', 'success');
            } else {
                showAlert('Erro: ' + data.error, 'danger');
            }
        })
        .catch(error => {
            processingProgress.classList.add('d-none');
            showAlert('Erro ao processar documento: ' + error.message, 'danger');
        });
    });
    
    // Atualizar rótulo de orientação quando o switch mudar
    orientationSwitch.addEventListener('change', function() {
        orientationLabel.textContent = this.checked ? 'Paisagem' : 'Retrato';
    });
    
    // Função auxiliar para mostrar alertas
    function showAlert(message, type) {
        const alertsContainer = document.getElementById('alerts');
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
        `;
        alertsContainer.appendChild(alert);
        
        // Auto-dispensa após 5 segundos
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    }
    
    // Evento de mudança do input de arquivo para atualizar a UI
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
