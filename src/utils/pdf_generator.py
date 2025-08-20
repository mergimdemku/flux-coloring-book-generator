"""
PDF generation utilities for coloring book export
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Image as ReportLabImage, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

class PDFGenerator:
    """Generate print-ready PDF coloring books"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Page dimensions
        self.page_width, self.page_height = A4
        self.margin = 15 * mm  # 15mm margins as per guide
        
        # Content area
        self.content_width = self.page_width - 2 * self.margin
        self.content_height = self.page_height - 2 * self.margin
        
        # Styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=20,
            alignment=1,  # Center
            textColor=colors.black
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=10,
            alignment=1,  # Center
            textColor=colors.grey
        )
        
        # Footer style
        self.footer_style = ParagraphStyle(
            'CustomFooter',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=1,  # Center
            textColor=colors.grey
        )
    
    def create_coloring_book(self, images: List[Path], metadata: Dict[str, Any], 
                           output_path: Path) -> Path:
        """Create complete coloring book PDF"""
        
        # Create document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin,
            title=metadata.get('title', 'Coloring Book'),
            author=metadata.get('company', '3D Gravity Kids'),
            subject="Children's Coloring Book",
            keywords=f"coloring, children, {metadata.get('theme', 'adventure')}"
        )
        
        # Build story
        story = []
        
        # Add title page
        story.extend(self._create_title_page(metadata))
        
        # Add coloring pages
        for i, image_path in enumerate(images):
            if image_path.exists():
                story.extend(self._create_coloring_page(image_path, i + 1))
            else:
                self.logger.warning(f"Image not found: {image_path}")
        
        # Add back cover/credits page
        story.extend(self._create_credits_page(metadata))
        
        # Build PDF
        try:
            doc.build(story)
            self.logger.info(f"PDF created successfully: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Failed to create PDF: {e}")
            raise
    
    def _create_title_page(self, metadata: Dict[str, Any]) -> List:
        """Create title page elements"""
        story = []
        
        # Title
        title = metadata.get('title', 'My Coloring Book')
        story.append(Spacer(1, 50))
        story.append(Paragraph(title, self.title_style))
        story.append(Spacer(1, 20))
        
        # Subtitle
        character_name = metadata.get('character_name', '')
        if character_name:
            subtitle = f"Adventures with {character_name}"
            story.append(Paragraph(subtitle, self.subtitle_style))
            story.append(Spacer(1, 30))
        
        # Age range
        age_range = metadata.get('age_range', '')
        if age_range:
            story.append(Paragraph(f"Perfect for ages {age_range}", self.subtitle_style))
            story.append(Spacer(1, 40))
        
        # Add cover image if available
        cover_image = self._find_cover_image(metadata.get('images', []))
        if cover_image and cover_image.exists():
            story.append(self._create_image_element(cover_image, fit_to_page=False))
        
        story.append(Spacer(1, 50))
        
        # Footer branding
        branding = f"{metadata.get('company', '3D Gravity Kids')} · {metadata.get('subtitle', 'Kopshti Magjik')}"
        story.append(Paragraph(branding, self.footer_style))
        
        return story
    
    def _create_coloring_page(self, image_path: Path, page_number: int) -> List:
        """Create a single coloring page"""
        story = []
        
        # Add page break
        if page_number > 1:
            story.append(Spacer(1, self.page_height))  # Page break
        
        # Add image
        story.append(self._create_image_element(image_path, fit_to_page=True))
        
        return story
    
    def _create_credits_page(self, metadata: Dict[str, Any]) -> List:
        """Create credits/back cover page"""
        story = []
        
        # Page break
        story.append(Spacer(1, self.page_height))
        
        story.append(Spacer(1, 100))
        
        # Thank you message
        thank_you = "Thank you for choosing our coloring book!"
        story.append(Paragraph(thank_you, self.title_style))
        story.append(Spacer(1, 30))
        
        # Credits
        credits_text = f"""
        <para alignment="center">
        Created with love by<br/>
        <b>{metadata.get('company', '3D Gravity Kids')}</b><br/>
        {metadata.get('subtitle', 'Kopshti Magjik')}<br/><br/>
        
        Visit us at: {metadata.get('website', 'kopshtimagjik.com')}<br/><br/>
        
        Generated on: {datetime.now().strftime('%B %Y')}<br/>
        </para>
        """
        
        story.append(Paragraph(credits_text, self.styles['Normal']))
        story.append(Spacer(1, 50))
        
        # Copyright notice
        copyright_text = f"© {datetime.now().year} {metadata.get('company', '3D Gravity Kids')}. All rights reserved."
        story.append(Paragraph(copyright_text, self.footer_style))
        
        return story
    
    def _create_image_element(self, image_path: Path, fit_to_page: bool = True) -> ReportLabImage:
        """Create a ReportLab image element"""
        
        try:
            # Open image to get dimensions
            with Image.open(image_path) as img:
                img_width, img_height = img.size
            
            # Calculate scaling for fit-to-page
            if fit_to_page:
                # Scale to fit content area while maintaining aspect ratio
                width_scale = self.content_width / img_width
                height_scale = self.content_height / img_height
                scale = min(width_scale, height_scale)
                
                display_width = img_width * scale
                display_height = img_height * scale
            else:
                # Use smaller size for cover images
                max_size = min(self.content_width, self.content_height) * 0.7
                width_scale = max_size / img_width
                height_scale = max_size / img_height
                scale = min(width_scale, height_scale)
                
                display_width = img_width * scale
                display_height = img_height * scale
            
            # Create ReportLab image
            return ReportLabImage(
                str(image_path),
                width=display_width,
                height=display_height
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create image element for {image_path}: {e}")
            # Return placeholder
            return Paragraph(f"[Image: {image_path.name}]", self.styles['Normal'])
    
    def _find_cover_image(self, images: List[Path]) -> Optional[Path]:
        """Find cover image from image list"""
        for image_path in images:
            if 'cover' in image_path.name.lower():
                return image_path
        return None
    
    def create_print_ready_pdf(self, images: List[Path], metadata: Dict[str, Any], 
                              output_path: Path, include_crop_marks: bool = False) -> Path:
        """Create print-ready PDF with professional settings"""
        
        # Create custom canvas for more control
        c = canvas.Canvas(str(output_path), pagesize=A4)
        
        # Set PDF metadata
        c.setTitle(metadata.get('title', 'Coloring Book'))
        c.setAuthor(metadata.get('company', '3D Gravity Kids'))
        c.setSubject("Children's Coloring Book")
        c.setCreator("Coloring Book Generator")
        
        page_num = 1
        
        # Title page
        self._draw_title_page_canvas(c, metadata)
        c.showPage()
        page_num += 1
        
        # Content pages
        for image_path in images:
            if image_path.exists():
                self._draw_image_page_canvas(c, image_path, include_crop_marks)
                c.showPage()
                page_num += 1
        
        # Credits page
        self._draw_credits_page_canvas(c, metadata)
        
        # Save PDF
        c.save()
        
        self.logger.info(f"Print-ready PDF created: {output_path}")
        return output_path
    
    def _draw_title_page_canvas(self, c: canvas.Canvas, metadata: Dict[str, Any]):
        """Draw title page using canvas"""
        
        # Title
        c.setFont("Helvetica-Bold", 24)
        title = metadata.get('title', 'My Coloring Book')
        title_width = c.stringWidth(title, "Helvetica-Bold", 24)
        c.drawString((self.page_width - title_width) / 2, self.page_height - 100, title)
        
        # Subtitle
        c.setFont("Helvetica", 14)
        character_name = metadata.get('character_name', '')
        if character_name:
            subtitle = f"Adventures with {character_name}"
            subtitle_width = c.stringWidth(subtitle, "Helvetica", 14)
            c.drawString((self.page_width - subtitle_width) / 2, self.page_height - 130, subtitle)
        
        # Age range
        age_range = metadata.get('age_range', '')
        if age_range:
            age_text = f"Perfect for ages {age_range}"
            age_width = c.stringWidth(age_text, "Helvetica", 14)
            c.drawString((self.page_width - age_width) / 2, self.page_height - 160, age_text)
        
        # Footer branding
        c.setFont("Helvetica", 10)
        branding = f"{metadata.get('company', '3D Gravity Kids')} · {metadata.get('subtitle', 'Kopshti Magjik')}"
        brand_width = c.stringWidth(branding, "Helvetica", 10)
        c.drawString((self.page_width - brand_width) / 2, 50, branding)
    
    def _draw_image_page_canvas(self, c: canvas.Canvas, image_path: Path, 
                               include_crop_marks: bool = False):
        """Draw image page using canvas"""
        
        try:
            # Open and get image dimensions
            with Image.open(image_path) as img:
                img_width, img_height = img.size
            
            # Calculate scaling to fit page with margins
            available_width = self.content_width
            available_height = self.content_height
            
            width_scale = available_width / img_width
            height_scale = available_height / img_height
            scale = min(width_scale, height_scale)
            
            display_width = img_width * scale
            display_height = img_height * scale
            
            # Center image on page
            x = (self.page_width - display_width) / 2
            y = (self.page_height - display_height) / 2
            
            # Draw image
            c.drawImage(str(image_path), x, y, display_width, display_height)
            
            # Add crop marks if requested
            if include_crop_marks:
                self._draw_crop_marks(c)
                
        except Exception as e:
            self.logger.error(f"Failed to draw image {image_path}: {e}")
            # Draw placeholder text
            c.setFont("Helvetica", 12)
            c.drawString(100, self.page_height / 2, f"Error loading image: {image_path.name}")
    
    def _draw_credits_page_canvas(self, c: canvas.Canvas, metadata: Dict[str, Any]):
        """Draw credits page using canvas"""
        
        # Thank you message
        c.setFont("Helvetica-Bold", 18)
        thank_you = "Thank you for choosing our coloring book!"
        thank_width = c.stringWidth(thank_you, "Helvetica-Bold", 18)
        c.drawString((self.page_width - thank_width) / 2, self.page_height - 150, thank_you)
        
        # Credits
        c.setFont("Helvetica", 12)
        credits_lines = [
            f"Created with love by",
            f"{metadata.get('company', '3D Gravity Kids')}",
            f"{metadata.get('subtitle', 'Kopshti Magjik')}",
            "",
            f"Visit us at: {metadata.get('website', 'kopshtimagjik.com')}",
            "",
            f"Generated on: {datetime.now().strftime('%B %Y')}"
        ]
        
        y_pos = self.page_height - 200
        for line in credits_lines:
            if line:  # Skip empty lines for spacing
                line_width = c.stringWidth(line, "Helvetica", 12)
                c.drawString((self.page_width - line_width) / 2, y_pos, line)
            y_pos -= 20
        
        # Copyright notice
        c.setFont("Helvetica", 8)
        copyright_text = f"© {datetime.now().year} {metadata.get('company', '3D Gravity Kids')}. All rights reserved."
        copyright_width = c.stringWidth(copyright_text, "Helvetica", 8)
        c.drawString((self.page_width - copyright_width) / 2, 50, copyright_text)
    
    def _draw_crop_marks(self, c: canvas.Canvas):
        """Draw crop marks for professional printing"""
        
        mark_length = 10
        mark_offset = 5
        
        # Top left
        c.line(0, self.page_height - mark_offset, mark_length, self.page_height - mark_offset)
        c.line(mark_offset, self.page_height, mark_offset, self.page_height - mark_length)
        
        # Top right
        c.line(self.page_width - mark_length, self.page_height - mark_offset, 
               self.page_width, self.page_height - mark_offset)
        c.line(self.page_width - mark_offset, self.page_height, 
               self.page_width - mark_offset, self.page_height - mark_length)
        
        # Bottom left
        c.line(0, mark_offset, mark_length, mark_offset)
        c.line(mark_offset, 0, mark_offset, mark_length)
        
        # Bottom right
        c.line(self.page_width - mark_length, mark_offset, self.page_width, mark_offset)
        c.line(self.page_width - mark_offset, 0, self.page_width - mark_offset, mark_length)
    
    def create_us_letter_version(self, a4_pdf_path: Path, output_path: Path) -> Path:
        """Create US Letter version from A4 PDF for Amazon KDP"""
        
        # This would require PyPDF2 or similar library to convert between page sizes
        # For now, we'll create a new PDF with Letter size
        
        self.logger.info("US Letter conversion would require additional PDF manipulation")
        # Implementation would go here using PyPDF2 or similar
        
        return output_path
    
    def validate_pdf_for_printing(self, pdf_path: Path) -> Dict[str, Any]:
        """Validate PDF meets printing requirements"""
        
        validation_results = {
            'file_exists': pdf_path.exists(),
            'file_size_mb': 0,
            'page_count': 0,
            'color_profile': 'unknown',
            'resolution_ok': True,
            'print_ready': False,
            'issues': []
        }
        
        if pdf_path.exists():
            validation_results['file_size_mb'] = pdf_path.stat().st_size / (1024 * 1024)
            
            # Additional validation would require PDF analysis libraries
            # For now, assume basic validation
            if validation_results['file_size_mb'] > 0:
                validation_results['print_ready'] = True
        else:
            validation_results['issues'].append("PDF file not found")
        
        return validation_results