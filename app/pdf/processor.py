import PyPDF2
import pdfplumber
import re

class PDFProcessor:
    def extract_text(self, file_path: str, pages: str = "all"):
        """Extract text from PDF pages. Pages can be 'all', '1-3', '1,3,5', etc."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                # Parse page specification
                page_numbers = self._parse_pages(pages, total_pages)
                
                extracted_text = ""
                
                # Use pdfplumber for better text extraction
                with pdfplumber.open(file_path) as pdf:
                    for page_num in page_numbers:
                        if 0 <= page_num < total_pages:
                            page = pdf.pages[page_num]
                            text = page.extract_text()
                            if text:
                                extracted_text += f"\n--- Page {page_num + 1} ---\n{text}\n"
                
                return extracted_text.strip()
                
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    def _parse_pages(self, pages: str, total_pages: int):
        """Parse page specification into list of page numbers (0-indexed)"""
        if pages.lower() == "all":
            return list(range(total_pages))
        
        page_numbers = []
        
        # Handle ranges and individual pages
        parts = pages.split(',')
        for part in parts:
            part = part.strip()
            if '-' in part:
                # Range like "1-5"
                start, end = part.split('-')
                start = int(start.strip()) - 1  # Convert to 0-indexed
                end = int(end.strip()) - 1
                page_numbers.extend(range(start, end + 1))
            else:
                # Individual page like "3"
                page_numbers.append(int(part.strip()) - 1)  # Convert to 0-indexed
        
        # Remove duplicates and sort
        return sorted(list(set(page_numbers)))