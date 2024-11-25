from PyPDF2 import PdfReader
import streamlit as st

class PDFProcessor:
    def __init__(self, pdf):
        self.pdf = pdf
        self.pdf_name = pdf.name.split(".")[0]
        self.text = ""

    def process(self):
        """Process the PDF and return the extracted text"""
        try:
            st.info('Extracting text from PDF, please wait...')
            self.text = self._read_pdf()
            return self.text
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return None

    def _read_pdf(self):
        """Extract text from PDF"""
        text = []
        reader = PdfReader(self.pdf)
        
        for page in reader.pages:
            text.append(page.extract_text())
        
        return "\n".join(text)

    def get_summary_stats(self):
        """Return summary statistics about the PDF"""
        if not self.text:
            self.text = self._read_pdf()
            
        return {
            "total_pages": len(PdfReader(self.pdf).pages),
            "total_chars": len(self.text),
            "total_words": len(self.text.split())
        }