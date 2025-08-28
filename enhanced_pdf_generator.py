#!/usr/bin/env python3
"""
Enhanced PDF Generator for Kids Coloring Books
Creates professional PDFs with colored covers and B&W coloring pages
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedPDFGenerator:
    """Enhanced PDF generator for coloring books with professional covers"""
    
    def __init__(self, output_dir: str = "generated_books"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # PDF settings
        self.page_width, self.page_height = A4
        self.margin = 0.5 * inch
        
        # Font settings (try to find good fonts)
        self.fonts = self._detect_available_fonts()
        
        # Template settings
        self.cover_template_settings = {
            'title_font_size': 24,
            'author_font_size': 16,
            'age_range_font_size': 12,
            'cover_image_ratio': 0.7,  # Cover image takes 70% of page height
            'title_color': colors.darkblue,
            'subtitle_color': colors.darkgreen
        }
    
    def _detect_available_fonts(self) -> Dict[str, str]:
        """Detect available fonts on system"""
        
        # Default fonts that should be available
        fonts = {
            'title': 'Helvetica-Bold',
            'subtitle': 'Helvetica', 
            'body': 'Helvetica',
            'decorative': 'Helvetica-Bold'
        }
        
        # Try to find better kid-friendly fonts
        possible_fonts = [
            'Comic Sans MS', 'Trebuchet MS', 'Verdana', 'Arial Black', 
            'Impact', 'Lucida Grande', 'Georgia'
        ]
        
        try:
            from reportlab.pdfbase import pdfutils
            available_fonts = pdfutils.getAvailableFonts()
            
            for font in possible_fonts:
                if font in available_fonts:
                    fonts['title'] = font
                    break
                    
        except Exception as e:
            logger.warning(f"Could not detect system fonts: {e}")
        
        return fonts
    
    def create_cover_page(self, canvas_obj: canvas.Canvas, story_data: Dict[str, Any], 
                         cover_image: Optional[Image.Image] = None) -> None:
        """Create professional cover page with image and text"""
        
        logger.info("Creating cover page")
        
        # Page dimensions
        page_width = self.page_width
        page_height = self.page_height
        
        # Calculate layout dimensions
        image_height = page_height * self.cover_template_settings['cover_image_ratio']
        text_area_height = page_height - image_height - (2 * self.margin)
        
        # Add cover image if provided
        if cover_image:
            # Resize image to fit cover area
            img_ratio = cover_image.width / cover_image.height
            target_ratio = page_width / image_height
            
            if img_ratio > target_ratio:
                # Image is wider - fit to width
                new_width = page_width - (2 * self.margin)
                new_height = new_width / img_ratio
            else:
                # Image is taller - fit to height
                new_height = image_height - self.margin
                new_width = new_height * img_ratio
            
            # Center image
            x_offset = (page_width - new_width) / 2
            y_offset = page_height - self.margin - new_height
            
            # Convert PIL image to reportlab format
            img_buffer = io.BytesIO()
            cover_image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            img_reader = ImageReader(img_buffer)
            
            # Draw image
            canvas_obj.drawImage(img_reader, x_offset, y_offset, width=new_width, height=new_height)
            
            # Draw border around image
            canvas_obj.setStrokeColor(colors.black)
            canvas_obj.setLineWidth(2)
            canvas_obj.rect(x_offset-2, y_offset-2, new_width+4, new_height+4)
        
        # Add title text
        title = story_data.get('title', 'Coloring Book Adventure')
        
        # Title
        canvas_obj.setFont(self.fonts['title'], self.cover_template_settings['title_font_size'])
        canvas_obj.setFillColor(self.cover_template_settings['title_color'])
        
        # Calculate title position
        title_y = page_height - self.margin - 30
        if cover_image:
            title_y = y_offset - 40
        
        # NO TEXT AT ALL - USER EXPLICITLY REQUESTED ZERO TEXT
        # ALL TEXT DRAWING DISABLED
        # canvas_obj.drawString(title_x, title_y, title)  # DISABLED
        # canvas_obj.drawString(subtitle_x, title_y - 30, subtitle)  # DISABLED  
        # canvas_obj.drawString(age_x, title_y - 55, age_info)  # DISABLED
        pass  # Cover image only, no text overlay
        
        # Add decorative elements
        self._add_cover_decorations(canvas_obj, page_width, page_height)
        
        # Footer with generation info
        footer_text = f"Generated on {datetime.now().strftime('%B %Y')} • AI-Created Coloring Book"
        canvas_obj.setFont(self.fonts['body'], 8)
        canvas_obj.setFillColor(colors.gray)
        footer_width = canvas_obj.stringWidth(footer_text, self.fonts['body'], 8)
        footer_x = (page_width - footer_width) / 2
        canvas_obj.drawString(footer_x, self.margin, footer_text)
    
    def _add_cover_decorations(self, canvas_obj: canvas.Canvas, page_width: float, page_height: float) -> None:
        """Add decorative elements to cover"""
        
        # Draw corner decorations
        decoration_size = 20
        
        # Top corners
        canvas_obj.setFillColor(colors.lightblue)
        canvas_obj.setStrokeColor(colors.darkblue)
        canvas_obj.setLineWidth(1)
        
        # Top-left star
        self._draw_star(canvas_obj, self.margin + decoration_size, page_height - self.margin - decoration_size, decoration_size//2)
        
        # Top-right star  
        self._draw_star(canvas_obj, page_width - self.margin - decoration_size, page_height - self.margin - decoration_size, decoration_size//2)
        
        # Bottom corners
        canvas_obj.setFillColor(colors.lightgreen)
        canvas_obj.setStrokeColor(colors.darkgreen)
        
        # Bottom-left star
        self._draw_star(canvas_obj, self.margin + decoration_size, self.margin + decoration_size, decoration_size//2)
        
        # Bottom-right star
        self._draw_star(canvas_obj, page_width - self.margin - decoration_size, self.margin + decoration_size, decoration_size//2)
    
    def _draw_star(self, canvas_obj: canvas.Canvas, x: float, y: float, size: float) -> None:
        """Draw a simple star decoration"""
        
        # Simple 5-pointed star
        import math
        
        points = []
        for i in range(10):
            angle = (i * math.pi) / 5
            if i % 2 == 0:
                # Outer point
                px = x + size * math.cos(angle - math.pi/2)
                py = y + size * math.sin(angle - math.pi/2)
            else:
                # Inner point
                px = x + (size/2) * math.cos(angle - math.pi/2)
                py = y + (size/2) * math.sin(angle - math.pi/2)
            points.extend([px, py])
        
        # Draw filled star
        path = canvas_obj.beginPath()
        path.moveTo(points[0], points[1])
        for i in range(2, len(points), 2):
            path.lineTo(points[i], points[i+1])
        path.close()
        
        canvas_obj.drawPath(path, fill=1, stroke=1)
    
    def create_coloring_page(self, canvas_obj: canvas.Canvas, page_image: Image.Image, 
                           page_number: int, scene_description: str = "") -> None:
        """Add coloring page to PDF"""
        
        logger.info(f"Adding coloring page {page_number}")
        
        # Calculate image dimensions to fit page with margins
        available_width = self.page_width - (2 * self.margin)
        available_height = self.page_height - (2 * self.margin) - 40  # Leave space for page number
        
        # Calculate scaling to fit
        img_ratio = page_image.width / page_image.height
        page_ratio = available_width / available_height
        
        if img_ratio > page_ratio:
            # Image is wider - fit to width
            new_width = available_width
            new_height = new_width / img_ratio
        else:
            # Image is taller - fit to height
            new_height = available_height
            new_width = new_height * img_ratio
        
        # Center image on page
        x_offset = (self.page_width - new_width) / 2
        y_offset = (self.page_height - new_height) / 2 + 20  # Offset up for page number
        
        # Convert PIL image to reportlab format
        img_buffer = io.BytesIO()
        page_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_reader = ImageReader(img_buffer)
        
        # Draw image
        canvas_obj.drawImage(img_reader, x_offset, y_offset, width=new_width, height=new_height)
        
        # NO TEXT ON COLORING PAGES - User explicitly requested this
        # Pages should be completely clean with only the coloring image
    
    def generate_complete_book_pdf(self, story_data: Dict[str, Any], 
                                  cover_image: Optional[Image.Image],
                                  coloring_images: List[Image.Image],
                                  prompts_data: List[Dict[str, str]]) -> str:
        """Generate complete PDF with cover and coloring pages"""
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in story_data.get('title', 'ColoringBook') if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')[:30]
        
        filename = f"{safe_title}_{story_data['art_style']['name']}_{timestamp}.pdf"
        filepath = self.output_dir / filename
        
        logger.info(f"Generating PDF: {filename}")
        logger.info(f"Cover image: {'Yes' if cover_image else 'No'}")
        logger.info(f"Coloring pages: {len(coloring_images)}")
        
        # Create PDF
        pdf_canvas = canvas.Canvas(str(filepath), pagesize=A4)
        
        try:
            # Create cover page
            self.create_cover_page(pdf_canvas, story_data, cover_image)
            pdf_canvas.showPage()
            
            # Add coloring pages
            for i, (image, prompt_data) in enumerate(zip(coloring_images, prompts_data[1:])):  # Skip cover prompt
                scene_desc = prompt_data.get('scene_description', '')
                self.create_coloring_page(pdf_canvas, image, i + 1, scene_desc)
                pdf_canvas.showPage()
            
            # Save PDF
            pdf_canvas.save()
            
            logger.info(f"✅ PDF generated successfully: {filepath}")
            logger.info(f"📊 Total pages: {len(coloring_images) + 1} (1 cover + {len(coloring_images)} coloring)")
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            # Clean up incomplete file
            if filepath.exists():
                filepath.unlink()
            raise
    
    def create_book_info_page(self, canvas_obj: canvas.Canvas, story_data: Dict[str, Any]) -> None:
        """Create information page with story summary and instructions"""
        
        logger.info("Creating book info page")
        
        # Title
        canvas_obj.setFont(self.fonts['title'], 18)
        canvas_obj.setFillColor(colors.darkblue)
        canvas_obj.drawString(self.margin, self.page_height - self.margin - 30, "About This Coloring Book")
        
        # Story summary
        canvas_obj.setFont(self.fonts['body'], 12)
        canvas_obj.setFillColor(colors.black)
        
        y_position = self.page_height - self.margin - 70
        
        # Story info
        story_info = [
            f"Title: {story_data.get('title', 'Adventure Story')}",
            f"Art Style: {story_data.get('art_style', {}).get('name', 'Cartoon')}",
            f"Target Age: {story_data.get('target_age', '5-8')} years",
            f"Characters: {story_data.get('main_character', 'Hero')} and {story_data.get('companion', 'Friend')}",
            "",
            "Story Summary:",
            story_data.get('summary', 'A wonderful adventure awaits!')
        ]
        
        for line in story_info:
            canvas_obj.drawString(self.margin, y_position, line)
            y_position -= 20
        
        # Instructions
        y_position -= 20
        canvas_obj.setFont(self.fonts['subtitle'], 14)
        canvas_obj.setFillColor(colors.darkgreen)
        canvas_obj.drawString(self.margin, y_position, "Coloring Instructions:")
        
        y_position -= 30
        canvas_obj.setFont(self.fonts['body'], 11)
        canvas_obj.setFillColor(colors.black)
        
        instructions = [
            "• Use crayons, colored pencils, or markers",
            "• Stay within the lines for best results", 
            "• Be creative with colors - make it your own!",
            "• Take your time and have fun",
            "• Show your finished pages to family and friends"
        ]
        
        for instruction in instructions:
            canvas_obj.drawString(self.margin, y_position, instruction)
            y_position -= 18

def test_pdf_generator():
    """Test the PDF generator"""
    
    print("🧪 Testing Enhanced PDF Generator...")
    
    generator = EnhancedPDFGenerator()
    
    # Test story data
    test_story = {
        'id': 'test_story_pdf',
        'title': 'The Magical Garden Adventure',
        'summary': 'Join Alex and Buddy as they discover a magical garden full of talking flowers and helpful creatures.',
        'theme': 'friendship_adventure',
        'target_age': '5-8',
        'art_style': {
            'name': 'Disney',
            'coloring_style': 'Disney style black and white line art'
        },
        'main_character': 'Alex',
        'companion': 'Buddy the Dog',
        'page_count': 3
    }
    
    # Create test images
    test_cover = Image.new('RGB', (400, 600), color='lightblue')
    test_pages = [
        Image.new('RGB', (400, 600), color='white'),
        Image.new('RGB', (400, 600), color='white'),
        Image.new('RGB', (400, 600), color='white')
    ]
    
    # Test prompts
    test_prompts = [
        {'type': 'cover', 'scene_description': 'Cover image'},
        {'type': 'coloring_page', 'scene_description': 'Playing in garden'},
        {'type': 'coloring_page', 'scene_description': 'Meeting woodland creatures'},
        {'type': 'coloring_page', 'scene_description': 'Finding magical flowers'}
    ]
    
    try:
        pdf_path = generator.generate_complete_book_pdf(
            story_data=test_story,
            cover_image=test_cover,
            coloring_images=test_pages,
            prompts_data=test_prompts
        )
        
        print(f"✅ Test PDF generated successfully!")
        print(f"📁 Location: {pdf_path}")
        
        # Check file size
        file_size = Path(pdf_path).stat().st_size / (1024 * 1024)
        print(f"📊 File size: {file_size:.1f} MB")
        
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        
    print("\n🎉 PDF generator test completed!")

if __name__ == "__main__":
    test_pdf_generator()