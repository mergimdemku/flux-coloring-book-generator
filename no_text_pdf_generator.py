#!/usr/bin/env python3
"""
NO TEXT PDF Generator - ZERO text anywhere
Creates PDFs with ONLY images, no text whatsoever
"""

import os
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch
import io
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NoTextPDFGenerator:
    """PDF generator with ZERO text - images only"""
    
    def __init__(self, output_dir: str = "no_text_books"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # PDF settings
        self.page_width, self.page_height = A4
        self.margin = 0.2 * inch  # Smaller margin for more image space
    
    def add_image_only_page(self, canvas_obj: canvas.Canvas, image: Image.Image) -> None:
        """Add a page with ONLY an image, no text at all"""
        
        # Calculate image dimensions to fill page (with small margin)
        available_width = self.page_width - (2 * self.margin)
        available_height = self.page_height - (2 * self.margin)
        
        # Calculate scaling to fit image in page
        img_ratio = image.width / image.height
        page_ratio = available_width / available_height
        
        if img_ratio > page_ratio:
            # Image is wider - fit to width
            new_width = available_width
            new_height = available_width / img_ratio
        else:
            # Image is taller - fit to height
            new_height = available_height
            new_width = available_height * img_ratio
        
        # Center the image on page
        x_offset = (self.page_width - new_width) / 2
        y_offset = (self.page_height - new_height) / 2
        
        # Convert PIL image to ReportLab format
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_reader = ImageReader(img_buffer)
        
        # Draw ONLY the image - NO TEXT ANYWHERE
        canvas_obj.drawImage(img_reader, x_offset, y_offset, width=new_width, height=new_height)
    
    def generate_clean_pdf(self, story_title: str, cover_image: Optional[Image.Image],
                          coloring_images: List[Image.Image]) -> str:
        """Generate PDF with ONLY images, zero text"""
        
        # Create filename based on title and timestamp
        safe_title = "".join(c for c in story_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"CLEAN_{safe_title}_{timestamp}.pdf"
        pdf_path = self.output_dir / filename
        
        logger.info(f"Generating CLEAN PDF: {filename}")
        logger.info(f"Cover image: {'Yes' if cover_image else 'No'}")
        logger.info(f"Coloring pages: {len(coloring_images)}")
        
        # Create PDF
        c = canvas.Canvas(str(pdf_path), pagesize=A4)
        
        # Add cover page (if provided)
        if cover_image:
            logger.info("Adding cover page (NO TEXT)")
            self.add_image_only_page(c, cover_image)
            c.showPage()
        
        # Add coloring pages
        for i, coloring_image in enumerate(coloring_images, 1):
            logger.info(f"Adding coloring page {i} (NO TEXT)")
            self.add_image_only_page(c, coloring_image)
            c.showPage()
        
        # Save PDF
        c.save()
        
        logger.info(f"✅ CLEAN PDF generated: {pdf_path}")
        logger.info(f"📊 Total pages: {len(coloring_images) + (1 if cover_image else 0)} (NO TEXT)")
        
        return str(pdf_path)

def test_no_text_pdf():
    """Test the no-text PDF generator with dummy images"""
    
    print("🧪 Testing NO TEXT PDF Generator")
    print("=" * 40)
    
    # Create dummy images
    from PIL import ImageDraw, ImageFont
    
    # Dummy colored cover
    cover = Image.new('RGB', (400, 600), color='lightblue')
    draw = ImageDraw.Draw(cover)
    
    # Draw some content on cover (but PDF won't add any text)
    draw.rectangle([50, 50, 350, 550], outline='darkblue', width=5)
    draw.ellipse([100, 200, 300, 400], fill='yellow', outline='orange', width=3)
    
    # Dummy B&W coloring page
    coloring = Image.new('RGB', (400, 600), color='white')
    draw = ImageDraw.Draw(coloring)
    
    # Draw simple coloring content
    draw.rectangle([50, 50, 350, 550], outline='black', width=3)
    draw.ellipse([100, 150, 300, 350], outline='black', width=3)
    draw.rectangle([150, 400, 250, 500], outline='black', width=3)
    
    # Generate clean PDF
    pdf_gen = NoTextPDFGenerator("test_clean_output")
    pdf_path = pdf_gen.generate_clean_pdf(
        story_title="Test Clean Story",
        cover_image=cover,
        coloring_images=[coloring]
    )
    
    print(f"✅ Clean PDF created: {pdf_path}")
    print("📋 This PDF should have ZERO text anywhere!")

if __name__ == "__main__":
    test_no_text_pdf()