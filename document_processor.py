import os
import logging
import tempfile
from PyPDF2 import PdfReader, PdfWriter, Transformation
from reportlab.lib.pagesizes import A4, A5
from reportlab.pdfgen import canvas
import subprocess
from pdf2image import convert_from_path
from docx2pdf import convert

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
        reader = PdfReader(input_file)
        writer = PdfWriter()
        
        # Calculate scaling factor and positioning
        for page in reader.pages:
            # Get the current page size
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            # Determine target dimensions based on orientation
            if orientation == 'portrait':
                target_width, target_height = A5_WIDTH, A5_HEIGHT
            else:  # landscape
                target_width, target_height = A5_HEIGHT, A5_WIDTH
            
            # Calculate scaling factors
            scale_x = target_width / page_width
            scale_y = target_height / page_height
            
            # Use the smaller scaling factor to ensure everything fits
            scale = min(scale_x, scale_y) * 0.95  # Add a small margin by scaling to 95%
            
            # Apply scaling transformation
            transformation = Transformation().scale(scale, scale)
            
            # Create a new page with A5 dimensions
            new_page = writer.add_blank_page(width=target_width, height=target_height)
            
            # Calculate centering offsets
            x_offset = (target_width - (page_width * scale)) / 2
            y_offset = (target_height - (page_height * scale)) / 2
            
            # Add margins
            x_offset += (margins['left'] * 72)  # Convert inches to points
            y_offset += (margins['bottom'] * 72)
            
            # Apply transformation
            new_page.merge_transformed_page(page, transformation, x_offset, y_offset)
        
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
        reader = PdfReader(input_file)
        writer = PdfWriter()
        
        for page in reader.pages:
            # Get the current page size
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            # Determine if we need portrait or landscape A5
            if orientation == 'portrait':
                target_width, target_height = A5_WIDTH, A5_HEIGHT
            else:  # landscape
                target_width, target_height = A5_HEIGHT, A5_WIDTH
            
            # Create first A5 page (left or top half)
            page1 = writer.add_blank_page(width=target_width, height=target_height)
            
            # Create transformation for first half
            # Scale the page to fit A5
            scale_x = target_width / (page_width * 0.5)
            scale_y = target_height / page_height
            scale = min(scale_x, scale_y) * 0.9  # 90% to add margin
            
            # Apply cropping and transformation for first half (left/top part)
            transform1 = Transformation().scale(scale * 2, scale)
            
            # Calculate centering offsets
            x_offset1 = (target_width - (page_width * scale)) / 2
            y_offset1 = (target_height - (page_height * scale)) / 2
            
            # Add margins
            x_offset1 += (margins['left'] * 72)  # Convert inches to points
            y_offset1 += (margins['bottom'] * 72)
            
            # Apply first transformation
            page1.merge_transformed_page(page, transform1, x_offset1, y_offset1)
            
            # Create second A5 page (right or bottom half)
            page2 = writer.add_blank_page(width=target_width, height=target_height)
            
            # Apply cropping and transformation for second half (right/bottom part)
            transform2 = Transformation().scale(scale * 2, scale).translate(-page_width/2, 0)
            
            # Apply second transformation
            page2.merge_transformed_page(page, transform2, x_offset1, y_offset1)
        
        # Write the output file
        with open(output_file, 'wb') as f:
            writer.write(f)
        
        return True
    except Exception as e:
        logging.error(f"Error splitting PDF: {str(e)}")
        return False
