"""
Advanced PDF Processing with OCR
Extracts text from PDFs using multiple methods
"""
import os
import logging
from typing import Dict, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Multi-method PDF text extraction with OCR fallback
    """

    def __init__(self):
        self.confidence_score = 0.0
        self.extraction_method = None

    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text from PDF using best available method

        Args:
            pdf_path: Path to PDF file

        Returns:
            str: Extracted text
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        # Try methods in order of preference
        text = None

        # Method 1: pdfplumber (best for text PDFs)
        text = self._extract_with_pdfplumber(pdf_path)
        if text and len(text.strip()) > 100:
            self.extraction_method = 'pdfplumber'
            self.confidence_score = 95.0
            return text

        # Method 2: PyPDF2 (fallback for text)
        text = self._extract_with_pypdf2(pdf_path)
        if text and len(text.strip()) > 100:
            self.extraction_method = 'pypdf2'
            self.confidence_score = 85.0
            return text

        # Method 3: OCR with tesseract (for scanned documents)
        text = self._extract_with_ocr(pdf_path)
        if text:
            self.extraction_method = 'tesseract_ocr'
            self.confidence_score = 70.0
            return text

        # No text extracted
        self.extraction_method = 'none'
        self.confidence_score = 0.0
        return ""

    def _extract_with_pdfplumber(self, pdf_path: str) -> Optional[str]:
        """Extract text using pdfplumber"""
        try:
            import pdfplumber

            text_parts = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

            text = '\n\n'.join(text_parts)
            logger.info(f"pdfplumber extracted {len(text)} characters")
            return text if text.strip() else None

        except ImportError:
            logger.warning("pdfplumber not installed")
            return None
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {e}")
            return None

    def _extract_with_pypdf2(self, pdf_path: str) -> Optional[str]:
        """Extract text using PyPDF2"""
        try:
            import PyPDF2

            text_parts = []
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

            text = '\n\n'.join(text_parts)
            logger.info(f"PyPDF2 extracted {len(text)} characters")
            return text if text.strip() else None

        except ImportError:
            logger.warning("PyPDF2 not installed")
            return None
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {e}")
            return None

    def _extract_with_ocr(self, pdf_path: str) -> Optional[str]:
        """Extract text using OCR (for scanned documents)"""
        try:
            from pdf2image import convert_from_path
            import pytesseract
            from config import Config

            # Set tesseract path if configured
            if Config.TESSERACT_PATH and os.path.exists(Config.TESSERACT_PATH):
                pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_PATH

            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)

            text_parts = []
            for i, image in enumerate(images):
                logger.info(f"OCR processing page {i+1}/{len(images)}")

                # Run OCR
                page_text = pytesseract.image_to_string(
                    image,
                    lang=Config.OCR_LANGUAGE,
                    config='--psm 1'  # Automatic page segmentation with OSD
                )

                if page_text.strip():
                    text_parts.append(page_text)

            text = '\n\n'.join(text_parts)
            logger.info(f"OCR extracted {len(text)} characters from {len(images)} pages")
            return text if text.strip() else None

        except ImportError as e:
            logger.warning(f"OCR dependencies not installed: {e}")
            return None
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return None

    def get_confidence_score(self) -> float:
        """Get confidence score of extraction"""
        return self.confidence_score

    def get_extraction_method(self) -> Optional[str]:
        """Get method used for extraction"""
        return self.extraction_method

    def extract_metadata(self, pdf_path: str) -> Dict[str, any]:
        """
        Extract PDF metadata

        Args:
            pdf_path: Path to PDF

        Returns:
            dict: Metadata
        """
        try:
            import PyPDF2

            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                metadata = {
                    'num_pages': len(pdf_reader.pages),
                    'title': None,
                    'author': None,
                    'subject': None,
                    'creator': None,
                    'producer': None,
                    'creation_date': None
                }

                if pdf_reader.metadata:
                    info = pdf_reader.metadata
                    metadata['title'] = info.get('/Title', None)
                    metadata['author'] = info.get('/Author', None)
                    metadata['subject'] = info.get('/Subject', None)
                    metadata['creator'] = info.get('/Creator', None)
                    metadata['producer'] = info.get('/Producer', None)
                    metadata['creation_date'] = info.get('/CreationDate', None)

                return metadata

        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return {}

    def is_scanned_pdf(self, pdf_path: str) -> bool:
        """
        Determine if PDF is scanned (image-based) vs text-based

        Args:
            pdf_path: Path to PDF

        Returns:
            bool: True if scanned/image-based
        """
        # Try to extract text - if very little text, likely scanned
        text = self._extract_with_pypdf2(pdf_path)
        if not text or len(text.strip()) < 50:
            return True

        # Check ratio of text to pages
        metadata = self.extract_metadata(pdf_path)
        num_pages = metadata.get('num_pages', 1)

        # If less than 20 chars per page, likely scanned
        avg_chars_per_page = len(text) / max(num_pages, 1)
        return avg_chars_per_page < 20

    def clean_extracted_text(self, text: str) -> str:
        """
        Clean and normalize extracted text

        Args:
            text: Raw extracted text

        Returns:
            str: Cleaned text
        """
        if not text:
            return ""

        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r' +', ' ', text)

        # Remove page numbers (common patterns)
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        text = re.sub(r'\nPage \d+ of \d+\n', '\n', text, flags=re.IGNORECASE)

        # Fix common OCR errors
        text = text.replace('|', 'I')  # Common OCR error
        text = text.replace('`', "'")

        # Normalize line breaks
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')

        return text.strip()

    def extract_tables(self, pdf_path: str) -> List[List[List[str]]]:
        """
        Extract tables from PDF

        Args:
            pdf_path: Path to PDF

        Returns:
            list: List of tables (each table is list of rows)
        """
        try:
            import pdfplumber

            all_tables = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        all_tables.extend(tables)

            logger.info(f"Extracted {len(all_tables)} tables from PDF")
            return all_tables

        except ImportError:
            logger.warning("pdfplumber not installed - table extraction unavailable")
            return []
        except Exception as e:
            logger.error(f"Table extraction failed: {e}")
            return []
