"""
PDF generation module for Notion Report Generator
"""
import markdown
import weasyprint
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Optional
import re
from datetime import datetime


def generate_pdf_from_markdown(md_content: str, output_path: str, title: str = "Notion Report") -> str:
    """
    Convert Markdown content to a styled PDF.
    
    Args:
        md_content: Markdown content to convert
        output_path: Path where to save the PDF
        title: Title for the PDF document
        
    Returns:
        Path to the generated PDF file
    """
    # Convert Markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['toc', 'tables', 'fenced_code'])
    
    # Create styled HTML with CSS
    styled_html = create_styled_html(html_content, title)
    
    # Generate PDF
    pdf_path = Path(output_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert HTML to PDF with WeasyPrint
    try:
        html_doc = weasyprint.HTML(string=styled_html)
        html_doc.write_pdf(str(pdf_path))
    except Exception as e:
        print(f"Warning: PDF generation failed, retrying with simplified content: {e}")
        # Try with simplified HTML if complex styling fails
        simplified_html = create_simplified_html(html_content, title)
        html_doc = weasyprint.HTML(string=simplified_html)
        html_doc.write_pdf(str(pdf_path))
    
    return str(pdf_path)


def create_simplified_html(html_content: str, title: str) -> str:
    """
    Create a simplified HTML document for PDF generation when complex styling fails.
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <style>
            @page {{ size: A4; margin: 1in; }}
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            h1, h2, h3 {{ color: #333; margin-top: 1em; }}
            h1 {{ font-size: 2em; }}
            h2 {{ font-size: 1.5em; }}
            h3 {{ font-size: 1.2em; }}
            pre {{ background: #f4f4f4; padding: 10px; overflow-x: auto; }}
            code {{ background: #f0f0f0; padding: 2px 4px; }}
            p {{ margin-bottom: 1em; }}
            ul, ol {{ margin-bottom: 1em; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        {html_content}
    </body>
    </html>
    """


def create_styled_html(html_content: str, title: str) -> str:
    """
    Create a styled HTML document with CSS for PDF generation.
    
    Args:
        html_content: Raw HTML content from Markdown
        title: Document title
        
    Returns:
        Complete styled HTML document
    """
    # Parse HTML to add page breaks and styling
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Add page breaks before major sections
    add_page_breaks(soup)
    
    # Create the complete HTML document
    styled_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            {get_pdf_css()}
        </style>
    </head>
    <body>
        <div class="document">
            <header class="document-header">
                <h1 class="document-title">{title}</h1>
                <div class="document-meta">
                    <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
            </header>
            
            <div class="document-content">
                {str(soup)}
            </div>
            
            <footer class="document-footer">
                <div class="page-number">
                    <span class="page-number-text">Page <span class="page-number-current"></span></span>
                </div>
            </footer>
        </div>
    </body>
    </html>
    """
    
    return styled_html


def add_page_breaks(soup: BeautifulSoup):
    """
    Add page breaks before major sections for better PDF layout.
    
    Args:
        soup: BeautifulSoup object of the HTML content
    """
    # Add page breaks before main sections (h1, h2)
    for heading in soup.find_all(['h1', 'h2']):
        if heading.name == 'h1' and heading.get_text().strip() != soup.find('h1').get_text().strip():
            # Add page break before h1 (except the first one)
            heading['style'] = 'page-break-before: always;'
        elif heading.name == 'h2':
            # Add page break before h2 if it's a major section
            text = heading.get_text().strip().lower()
            if any(keyword in text for keyword in ['tasks', 'notes', 'project details', 'summary']):
                heading['style'] = 'page-break-before: always;'


def get_pdf_css() -> str:
    """
    Get CSS styles for PDF generation.
    
    Returns:
        CSS string for PDF styling
    """
    return """
    @page {
        size: A4;
        margin: 2cm 1.5cm 3cm 1.5cm;
        
        @top-center {
            content: "Notion Report Generator";
            font-size: 10px;
            color: #666;
        }
        
        @bottom-right {
            content: "Page " counter(page) " of " counter(pages);
            font-size: 10px;
            color: #666;
        }
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        color: #333;
        font-size: 11px;
    }
    
    .document {
        max-width: 100%;
    }
    
    .document-header {
        text-align: center;
        margin-bottom: 2cm;
        padding-bottom: 1cm;
        border-bottom: 2px solid #007bff;
    }
    
    .document-title {
        font-size: 24px;
        font-weight: bold;
        color: #007bff;
        margin: 0 0 0.5cm 0;
    }
    
    .document-meta {
        font-size: 10px;
        color: #666;
        margin: 0;
    }
    
    .document-content {
        margin-bottom: 2cm;
    }
    
    .document-footer {
        position: fixed;
        bottom: 1cm;
        right: 1.5cm;
        font-size: 10px;
        color: #666;
    }
    
    /* Headings */
    h1 {
        font-size: 18px;
        font-weight: bold;
        color: #007bff;
        margin: 1.5cm 0 0.5cm 0;
        padding-bottom: 0.3cm;
        border-bottom: 1px solid #e0e0e0;
    }
    
    h2 {
        font-size: 14px;
        font-weight: bold;
        color: #333;
        margin: 1cm 0 0.3cm 0;
        padding-left: 0.5cm;
        border-left: 3px solid #007bff;
    }
    
    h3 {
        font-size: 12px;
        font-weight: bold;
        color: #555;
        margin: 0.5cm 0 0.2cm 0;
    }
    
    h4, h5, h6 {
        font-size: 11px;
        font-weight: bold;
        color: #666;
        margin: 0.3cm 0 0.1cm 0;
    }
    
    /* Table of Contents */
    .toc {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 1cm;
        margin: 1cm 0;
    }
    
    .toc h2 {
        margin-top: 0;
        color: #007bff;
        border: none;
        padding: 0;
    }
    
    .toc ul {
        list-style: none;
        padding-left: 0;
    }
    
    .toc li {
        margin: 0.2cm 0;
        padding: 0.1cm 0;
    }
    
    .toc a {
        text-decoration: none;
        color: #333;
        font-size: 10px;
    }
    
    .toc a:hover {
        color: #007bff;
    }
    
    /* Tables */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 0.5cm 0;
        font-size: 10px;
    }
    
    th, td {
        border: 1px solid #ddd;
        padding: 0.3cm;
        text-align: left;
    }
    
    th {
        background-color: #f8f9fa;
        font-weight: bold;
        color: #333;
    }
    
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    
    /* Lists */
    ul, ol {
        margin: 0.3cm 0;
        padding-left: 1cm;
    }
    
    li {
        margin: 0.1cm 0;
    }
    
    /* Code blocks */
    pre {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 3px;
        padding: 0.5cm;
        margin: 0.5cm 0;
        font-family: 'Courier New', monospace;
        font-size: 9px;
        overflow-x: auto;
    }
    
    code {
        background-color: #f8f9fa;
        padding: 0.1cm 0.2cm;
        border-radius: 2px;
        font-family: 'Courier New', monospace;
        font-size: 9px;
    }
    
    /* Blockquotes */
    blockquote {
        border-left: 3px solid #007bff;
        margin: 0.5cm 0;
        padding-left: 1cm;
        color: #666;
        font-style: italic;
    }
    
    /* Horizontal rules */
    hr {
        border: none;
        border-top: 1px solid #e0e0e0;
        margin: 1cm 0;
    }
    
    /* Task properties */
    .task-properties {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 3px;
        padding: 0.3cm;
        margin: 0.2cm 0;
        font-size: 9px;
        color: #666;
    }
    
    .task-properties strong {
        color: #333;
    }
    
    /* Status indicators */
    .status-active { color: #28a745; font-weight: bold; }
    .status-in-progress { color: #ffc107; font-weight: bold; }
    .status-completed { color: #6c757d; font-weight: bold; }
    .status-planning { color: #17a2b8; font-weight: bold; }
    .status-on-hold { color: #fd7e14; font-weight: bold; }
    
    /* Page breaks */
    .page-break {
        page-break-before: always;
    }
    
    /* Avoid breaking these elements */
    h1, h2, h3, h4, h5, h6 {
        page-break-after: avoid;
    }
    
    table {
        page-break-inside: avoid;
    }
    
    pre {
        page-break-inside: avoid;
    }
    
    /* Print optimizations */
    @media print {
        body {
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
    }
    """


def extract_toc_from_html(html_content: str) -> str:
    """
    Extract table of contents from HTML content and format it for PDF.
    
    Args:
        html_content: HTML content to extract TOC from
        
    Returns:
        Formatted table of contents HTML
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    headings = soup.find_all(['h1', 'h2', 'h3'])
    
    if not headings:
        return ""
    
    toc_html = '<div class="toc"><h2>Table of Contents</h2><ul>'
    
    for heading in headings:
        # Create anchor link
        text = heading.get_text().strip()
        anchor = re.sub(r'[^\w\s-]', '', text.lower())
        anchor = re.sub(r'[-\s]+', '-', anchor).strip('-')
        
        # Create indentation based on heading level
        level = int(heading.name[1])
        indent = "&nbsp;" * (level - 1) * 4
        
        # Add to TOC
        toc_html += f'<li style="margin-left: {level - 1}em;"><a href="#{anchor}">{indent}{text}</a></li>'
    
    toc_html += '</ul></div>'
    return toc_html
