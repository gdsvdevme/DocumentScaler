import os
import logging
import tempfile
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4, A5
from reportlab.pdfgen import canvas
import subprocess
from pdf2image import convert_from_path
from docx2pdf import convert
import io

# Constants for page sizes (in points)
A4_WIDTH, A4_HEIGHT = A4  # 595.276, 841.89 points
A5_WIDTH, A5_HEIGHT = A5  # 419.528, 595.276 points

def convert_word_to_pdf(input_file, output_file):
    """
    Convert Word document to PDF
    """
    try:
        # Try using docx2pdf converter
        convert(input_file, output_file)
        return True
    except Exception as e:
        logging.error(f"Error converting Word to PDF with docx2pdf: {str(e)}")
        try:
            # Fallback: try using LibreOffice if available (uncomment if needed)
            # cmd = ['libreoffice', '--headless', '--convert-to', 'pdf', 
            #       '--outdir', os.path.dirname(output_file), input_file]
            # subprocess.run(cmd, check=True)
            # 
            # # Rename the output file to match the expected output_file path
            # original_name = os.path.splitext(os.path.basename(input_file))[0] + '.pdf'
            # original_path = os.path.join(os.path.dirname(output_file), original_name)
            # if os.path.exists(original_path):
            #     os.rename(original_path, output_file)
            #     return True
            
            # If both methods fail, return False
            return False
        except Exception as e2:
            logging.error(f"Error during fallback Word to PDF conversion: {str(e2)}")
            return False

def resize_pdf_to_a5(input_file, output_file, margins, orientation='portrait'):
    """
    Resize a PDF from any size to A5 format
    """
    try:
        # Determine target dimensions based on orientation
        if orientation == 'portrait':
            target_width, target_height = A5_WIDTH, A5_HEIGHT
        else:  # landscape
            target_width, target_height = A5_HEIGHT, A5_WIDTH
        
        # Apply margins (convert inches to points)
        margin_left = margins['left'] * 72
        margin_right = margins['right'] * 72
        margin_top = margins['top'] * 72
        margin_bottom = margins['bottom'] * 72
        
        # Adjusted dimensions
        content_width = target_width - margin_left - margin_right
        content_height = target_height - margin_top - margin_bottom
        
        # Create a new PDF with the target size
        reader = PdfReader(input_file)
        writer = PdfWriter()
        
        # Process each page
        for page_num in range(len(reader.pages)):
            # Create a new PDF page with A5 size
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=(target_width, target_height))
            
            # Get the original page
            original_page = reader.pages[page_num]
            
            # Extract the page as an image to maintain all content
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=True) as temp_pdf:
                # Create a temporary PDF with just this page
                temp_writer = PdfWriter()
                temp_writer.add_page(original_page)
                temp_writer.write(temp_pdf)
                temp_pdf.flush()
                
                # Convert page to image
                images = convert_from_path(temp_pdf.name, dpi=200)
                if images:
                    # Get first image from the page
                    img = images[0]
                    
                    # Calculate scaling to fit within the content area
                    img_width, img_height = img.size
                    scale_x = content_width / img_width
                    scale_y = content_height / img_height
                    
                    # Use the smaller scaling factor to ensure everything fits
                    scale = min(scale_x, scale_y)
                    
                    # Calculate scaled dimensions
                    scaled_width = img_width * scale
                    scaled_height = img_height * scale
                    
                    # Calculate position to center the content
                    x_pos = margin_left + (content_width - scaled_width) / 2
                    y_pos = margin_bottom + (content_height - scaled_height) / 2
                    
                    # Save image to a temporary file
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=True) as temp_img:
                        img.save(temp_img.name, format='PNG')
                        temp_img.flush()
                        
                        # Draw the image on the canvas
                        can.drawImage(temp_img.name, x_pos, y_pos, width=scaled_width, height=scaled_height)
            
            # Save the canvas
            can.save()
            
            # Move to the beginning of the buffer
            packet.seek(0)
            
            # Create a new PDF from the canvas
            new_pdf = PdfReader(packet)
            
            # Add the page to our output
            writer.add_page(new_pdf.pages[0])
        
        # Write the output file
        with open(output_file, 'wb') as f:
            writer.write(f)
        
        return True
    except Exception as e:
        logging.error(f"Error resizing PDF: {str(e)}")
        return False

def split_pdf_to_a5(input_file, output_file, margins, orientation='portrait'):
    """
    Split an A4 PDF into two A5 pages side by side
    """
    try:
        # Determine target dimensions based on orientation
        if orientation == 'portrait':
            target_width, target_height = A5_WIDTH, A5_HEIGHT
        else:  # landscape
            target_width, target_height = A5_HEIGHT, A5_WIDTH
        
        # Apply margins (convert inches to points)
        margin_left = margins['left'] * 72
        margin_right = margins['right'] * 72
        margin_top = margins['top'] * 72
        margin_bottom = margins['bottom'] * 72
        
        # Adjusted dimensions
        content_width = target_width - margin_left - margin_right
        content_height = target_height - margin_top - margin_bottom
        
        # Create a new PDF with the target size
        reader = PdfReader(input_file)
        writer = PdfWriter()
        
        # Process each page and split it into two
        for page_num in range(len(reader.pages)):
            original_page = reader.pages[page_num]
            page_width = float(original_page.mediabox.width)
            page_height = float(original_page.mediabox.height)
            
            # Extract the page as an image to maintain all content
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=True) as temp_pdf:
                # Create a temporary PDF with just this page
                temp_writer = PdfWriter()
                temp_writer.add_page(original_page)
                temp_writer.write(temp_pdf)
                temp_pdf.flush()
                
                # Convert page to image
                images = convert_from_path(temp_pdf.name, dpi=200)
                if not images:
                    continue
                
                # Get first image from the page
                img = images[0]
                img_width, img_height = img.size
                
                # Split the image into two halves
                if orientation == 'portrait':
                    # Split horizontally (left and right halves)
                    left_half = img.crop((0, 0, img_width // 2, img_height))
                    right_half = img.crop((img_width // 2, 0, img_width, img_height))
                else:
                    # Split vertically (top and bottom halves)
                    left_half = img.crop((0, 0, img_width, img_height // 2))
                    right_half = img.crop((0, img_height // 2, img_width, img_height))
                
                # Process first half (left or top)
                with tempfile.NamedTemporaryFile(suffix='.png', delete=True) as temp_img1:
                    left_half.save(temp_img1.name, format='PNG')
                    temp_img1.flush()
                    
                    # Create new A5 page for the first half
                    packet1 = io.BytesIO()
                    can1 = canvas.Canvas(packet1, pagesize=(target_width, target_height))
                    
                    # Calculate scaling to fit within the content area
                    half_width, half_height = left_half.size
                    scale_x = content_width / half_width
                    scale_y = content_height / half_height
                    scale = min(scale_x, scale_y)
                    
                    # Calculate scaled dimensions
                    scaled_width = half_width * scale
                    scaled_height = half_height * scale
                    
                    # Calculate position to center the content
                    x_pos = margin_left + (content_width - scaled_width) / 2
                    y_pos = margin_bottom + (content_height - scaled_height) / 2
                    
                    # Draw the first half
                    can1.drawImage(temp_img1.name, x_pos, y_pos, width=scaled_width, height=scaled_height)
                    can1.save()
                    
                    # Add the first half to the output
                    packet1.seek(0)
                    new_pdf1 = PdfReader(packet1)
                    writer.add_page(new_pdf1.pages[0])
                
                # Process second half (right or bottom)
                with tempfile.NamedTemporaryFile(suffix='.png', delete=True) as temp_img2:
                    right_half.save(temp_img2.name, format='PNG')
                    temp_img2.flush()
                    
                    # Create new A5 page for the second half
                    packet2 = io.BytesIO()
                    can2 = canvas.Canvas(packet2, pagesize=(target_width, target_height))
                    
                    # Calculate scaling to fit within the content area
                    half_width, half_height = right_half.size
                    scale_x = content_width / half_width
                    scale_y = content_height / half_height
                    scale = min(scale_x, scale_y)
                    
                    # Calculate scaled dimensions
                    scaled_width = half_width * scale
                    scaled_height = half_height * scale
                    
                    # Calculate position to center the content
                    x_pos = margin_left + (content_width - scaled_width) / 2
                    y_pos = margin_bottom + (content_height - scaled_height) / 2
                    
                    # Draw the second half
                    can2.drawImage(temp_img2.name, x_pos, y_pos, width=scaled_width, height=scaled_height)
                    can2.save()
                    
                    # Add the second half to the output
                    packet2.seek(0)
                    new_pdf2 = PdfReader(packet2)
                    writer.add_page(new_pdf2.pages[0])
        
        # Write the output file
        with open(output_file, 'wb') as f:
            writer.write(f)
        
        return True
    except Exception as e:
        logging.error(f"Error splitting PDF: {str(e)}")
        return False
