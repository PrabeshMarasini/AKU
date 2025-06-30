import PyPDF2
import pdfplumber
import fitz
import os
import sys
from pathlib import Path

class PDFTextExtractor:
    def __init__(self):
        self.supported_methods = ['pypdf2', 'pdfplumber', 'pymupdf']
    
    def extract_with_pypdf2(self, pdf_path):
        """Extract text using PyPDF2 library"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            print(f"Error with PyPDF2: {e}")
            return None
    
    def extract_with_pdfplumber(self, pdf_path):
        """Extract text using pdfplumber library"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            return text.strip()
        except Exception as e:
            print(f"Error with pdfplumber: {e}")
            return None
    
    def extract_with_pymupdf(self, pdf_path):
        """Extract text using PyMuPDF library"""
        try:
            text = ""
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text() + "\n"
            
            doc.close()
            return text.strip()
        except Exception as e:
            print(f"Error with PyMuPDF: {e}")
            return None
    
    def extract_text(self, pdf_path, method='auto'):
        """
        Extract text from PDF using specified method or auto-detect best method
        
        Args:
            pdf_path (str): Path to the PDF file
            method (str): Method to use ('pypdf2', 'pdfplumber', 'pymupdf', or 'auto')
        
        Returns:
            str: Extracted text content
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Try different methods
        if method == 'auto':
            methods = [
                ('pdfplumber', self.extract_with_pdfplumber),
                ('pymupdf', self.extract_with_pymupdf),
                ('pypdf2', self.extract_with_pypdf2)
            ]
            
            for method_name, method_func in methods:
                print(f"Trying {method_name}...")
                text = method_func(pdf_path)
                if text and text.strip():
                    print(f"Successfully extracted text using {method_name}")
                    return text
            
            print("All methods failed to extract text")
            return ""
        
        elif method == 'pypdf2':
            return self.extract_with_pypdf2(pdf_path)
        elif method == 'pdfplumber':
            return self.extract_with_pdfplumber(pdf_path)
        elif method == 'pymupdf':
            return self.extract_with_pymupdf(pdf_path)
        else:
            raise ValueError(f"Unsupported method: {method}")
    
    def extract_from_directory(self, directory_path, output_dir=None):
        """
        Extract text from all PDF files in a directory
        
        Args:
            directory_path (str): Path to directory containing PDF files
            output_dir (str): Optional directory to save extracted text files
        
        Returns:
            dict: Dictionary with filename as key and extracted text as value
        """
        pdf_files = list(Path(directory_path).glob("*.pdf"))
        results = {}
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        for pdf_file in pdf_files:
            print(f"Processing: {pdf_file.name}")
            try:
                text = self.extract_text(str(pdf_file))
                results[pdf_file.name] = text
                
                if output_dir:
                    output_file = Path(output_dir) / f"{pdf_file.stem}.txt"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(text)
                    print(f"Saved to: {output_file}")
                
            except Exception as e:
                print(f"Failed to process {pdf_file.name}: {e}")
                results[pdf_file.name] = ""
        
        return results
    
    def get_pdf_info(self, pdf_path):
        """Get basic information about the PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                info = {
                    'num_pages': len(pdf_reader.pages),
                    'title': pdf_reader.metadata.get('/Title', 'N/A') if pdf_reader.metadata else 'N/A',
                    'author': pdf_reader.metadata.get('/Author', 'N/A') if pdf_reader.metadata else 'N/A',
                    'subject': pdf_reader.metadata.get('/Subject', 'N/A') if pdf_reader.metadata else 'N/A',
                    'creator': pdf_reader.metadata.get('/Creator', 'N/A') if pdf_reader.metadata else 'N/A',
                    'producer': pdf_reader.metadata.get('/Producer', 'N/A') if pdf_reader.metadata else 'N/A',
                }
                return info
        except Exception as e:
            print(f"Error getting PDF info: {e}")
            return None

def main():
    """Example usage of the PDFTextExtractor"""
    extractor = PDFTextExtractor()

    pdf_path = "example.pdf" 
    if os.path.exists(pdf_path):
        print("=== PDF Information ===")
        info = extractor.get_pdf_info(pdf_path)
        if info:
            for key, value in info.items():
                print(f"{key.title()}: {value}")
        
        print("\n=== Extracting Text ===")
        text = extractor.extract_text(pdf_path, method='auto')
        print(f"Extracted {len(text)} characters")
        print("\n=== First 500 characters ===")
        print(text[:100000])
        
        output_file = f"{Path(pdf_path).stem}_extracted.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"\nText saved to: {output_file}")

    directory_path = "./pdfs" 
    if os.path.exists(directory_path):
        print(f"\n=== Processing directory: {directory_path} ===")
        results = extractor.extract_from_directory(directory_path, output_dir="./extracted_texts")
        print(f"Processed {len(results)} files")

if __name__ == "__main__":
    main()