import os
import uuid
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename
import document_processor as dp

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-dev")

# Configure upload folder
UPLOAD_FOLDER = '/tmp/uploads'
PROCESSED_FOLDER = '/tmp/processed'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

# Create required directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'document' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    
    file = request.files['document']
    
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Generate a unique filename to avoid collisions
        unique_filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # Get file extension
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        
        # Return the file info for the next steps
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'file_path': file_path,
            'file_name': file.filename,
            'file_id': unique_filename,
            'file_type': file_extension
        })
    
    flash('File type not supported. Please upload PDF, DOC, or DOCX files.', 'danger')
    return redirect(url_for('index'))

@app.route('/process-text', methods=['POST'])
def process_text():
    try:
        # Get parameters from request
        text_content = request.json.get('text')
        title = request.json.get('title', '')
        text_style = request.json.get('text_style', 'normal')
        font_size = int(request.json.get('font_size', 12))
        processing_type = request.json.get('processing_type', 'resize')  # Ignored for text, but kept for API consistency
        margins = {
            'top': float(request.json.get('margin_top', 0.5)),
            'right': float(request.json.get('margin_right', 0.5)),
            'bottom': float(request.json.get('margin_bottom', 0.5)),
            'left': float(request.json.get('margin_left', 0.5))
        }
        orientation = request.json.get('orientation', 'portrait')
        
        # Validate inputs
        if not text_content:
            return jsonify({'success': False, 'error': 'Texto não fornecido'})
        
        # Generate output filename
        output_filename = os.path.join(PROCESSED_FOLDER, 
                                      f"{uuid.uuid4()}_text_document.pdf")
        
        # Create PDF from text
        success = dp.create_pdf_from_text(
            text_content, 
            output_filename, 
            title=title,
            font_size=font_size,
            text_style=text_style,
            margins=margins,
            orientation=orientation
        )
        
        if success:
            # Return preview URL
            return jsonify({
                'success': True,
                'output_path': output_filename,
                'preview_url': url_for('get_preview', filename=os.path.basename(output_filename))
            })
        else:
            return jsonify({'success': False, 'error': 'Falha ao processar o texto'})
            
    except Exception as e:
        logging.error(f"Error processing text: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/process', methods=['POST'])
def process_document():
    try:
        # Get parameters from request
        file_path = request.json.get('file_path')
        file_type = request.json.get('file_type')
        processing_type = request.json.get('processing_type', 'resize')  # 'resize' or 'split'
        margins = {
            'top': float(request.json.get('margin_top', 0.5)),
            'right': float(request.json.get('margin_right', 0.5)),
            'bottom': float(request.json.get('margin_bottom', 0.5)),
            'left': float(request.json.get('margin_left', 0.5))
        }
        orientation = request.json.get('orientation', 'portrait')
        
        # Validate inputs
        if not file_path or not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'Arquivo não encontrado'})
        
        # Generate output filename
        output_filename = os.path.join(PROCESSED_FOLDER, 
                                      f"{uuid.uuid4()}_processed.pdf")
        
        # Process the document based on file type and processing type
        if file_type == 'pdf':
            if processing_type == 'resize':
                success = dp.resize_pdf_to_a5(file_path, output_filename, margins, orientation)
            else:  # split
                success = dp.split_pdf_to_a5(file_path, output_filename, margins, orientation)
        elif file_type in ['doc', 'docx']:
            # Convert word to PDF first
            temp_pdf = os.path.join(PROCESSED_FOLDER, f"{uuid.uuid4()}_converted.pdf")
            conversion_success = dp.convert_word_to_pdf(file_path, temp_pdf)
            
            if not conversion_success:
                return jsonify({'success': False, 'error': 'Falha ao converter documento Word para PDF'})
            
            # Then process the PDF
            if processing_type == 'resize':
                success = dp.resize_pdf_to_a5(temp_pdf, output_filename, margins, orientation)
            else:  # split
                success = dp.split_pdf_to_a5(temp_pdf, output_filename, margins, orientation)
            
            # Clean up temp file
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)
        
        if success:
            # Return preview URL
            return jsonify({
                'success': True,
                'output_path': output_filename,
                'preview_url': url_for('get_preview', filename=os.path.basename(output_filename))
            })
        else:
            return jsonify({'success': False, 'error': 'Falha ao processar o documento'})
            
    except Exception as e:
        logging.error(f"Error processing document: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/preview/<filename>')
def get_preview(filename):
    return send_file(os.path.join(PROCESSED_FOLDER, filename), mimetype='application/pdf')

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(PROCESSED_FOLDER, filename),
                     mimetype='application/pdf',
                     as_attachment=True,
                     download_name='documento_formatado_a5.pdf')
