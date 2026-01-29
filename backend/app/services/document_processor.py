"""Document processor for extracting text and creating chunks."""
from pathlib import Path
from typing import Optional

from pypdf import PdfReader
from docx import Document as DocxDocument
import markdown


class DocumentProcessor:
    """Service for processing documents into chunks."""
    
    SUPPORTED_TYPES = {".pdf", ".docx", ".doc", ".md", ".txt"}
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize document processor.
        
        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap characters between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    @staticmethod
    def get_file_type(filename: str) -> str:
        """
        Get normalized file type from filename.
        
        Args:
            filename: File name
            
        Returns:
            File type (pdf, docx, txt, md)
            
        Raises:
            ValueError: If file type is not supported
        """
        suffix = Path(filename).suffix.lower()
        if suffix not in DocumentProcessor.SUPPORTED_TYPES:
            raise ValueError(f"Unsupported file type: {suffix}")
        
        # Normalize .doc to .docx
        if suffix == ".doc":
            suffix = ".docx"
        
        return suffix.lstrip(".")
    
    async def process(self, file_path: str, file_type: str) -> list[dict]:
        """
        Process a document into chunks.
        
        Args:
            file_path: Path to document file
            file_type: Type of file (pdf, docx, txt, md)
            
        Returns:
            List of chunk dictionaries with chunk_text, chunk_index, page_number
        """
        # Extract text
        if file_type == "pdf":
            text, page_texts = self._extract_pdf(file_path)
        elif file_type == "docx":
            text, page_texts = self._extract_docx(file_path)
        elif file_type == "md":
            text, page_texts = self._extract_markdown(file_path)
        elif file_type == "txt":
            text, page_texts = self._extract_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Create chunks
        if page_texts:
            # Create chunks per page for PDFs
            chunks = self._chunk_by_pages(page_texts)
        else:
            # Create chunks from full text
            chunks = self._chunk_text(text)
        
        return chunks
    
    def _extract_pdf(self, file_path: str) -> tuple[str, list[tuple[int, str]]]:
        """
        Extract text from PDF.
        
        Returns:
            Tuple of (full_text, list of (page_number, page_text))
        """
        reader = PdfReader(file_path)
        page_texts = []
        full_text = []
        
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text.strip():
                page_texts.append((page_num, text))
                full_text.append(text)
        
        return "\n\n".join(full_text), page_texts
    
    def _extract_docx(self, file_path: str) -> tuple[str, list]:
        """Extract text from DOCX."""
        doc = DocxDocument(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        text = "\n\n".join(paragraphs)
        return text, []
    
    def _extract_markdown(self, file_path: str) -> tuple[str, list]:
        """Extract text from Markdown."""
        with open(file_path, "r", encoding="utf-8") as f:
            md_text = f.read()
        # Convert to plain text
        html = markdown.markdown(md_text)
        # Simple HTML tag removal
        import re
        text = re.sub(r"<[^>]+>", "", html)
        return text, []
    
    def _extract_text(self, file_path: str) -> tuple[str, list]:
        """Extract text from plain text file."""
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        return text, []
    
    def _chunk_text(self, text: str) -> list[dict]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Full text to chunk
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            # Try to break at sentence or word boundary
            if end < len(text):
                # Look for sentence end
                last_period = chunk_text.rfind(". ")
                if last_period > self.chunk_size * 0.5:
                    end = start + last_period + 1
                    chunk_text = text[start:end]
                else:
                    # Look for word boundary
                    last_space = chunk_text.rfind(" ")
                    if last_space > self.chunk_size * 0.5:
                        end = start + last_space
                        chunk_text = text[start:end]
            
            if chunk_text.strip():
                chunks.append({
                    "chunk_text": chunk_text.strip(),
                    "chunk_index": chunk_index,
                    "page_number": None,
                })
                chunk_index += 1
            
            # Move start with overlap
            start = end - self.chunk_overlap if end < len(text) else end
        
        return chunks
    
    def _chunk_by_pages(self, page_texts: list[tuple[int, str]]) -> list[dict]:
        """
        Create chunks from page texts, respecting page boundaries.
        
        Args:
            page_texts: List of (page_number, text) tuples
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        chunk_index = 0
        
        for page_num, page_text in page_texts:
            # If page is small enough, use as single chunk
            if len(page_text) <= self.chunk_size:
                chunks.append({
                    "chunk_text": page_text.strip(),
                    "chunk_index": chunk_index,
                    "page_number": page_num,
                })
                chunk_index += 1
            else:
                # Split page into multiple chunks
                page_chunks = self._chunk_text(page_text)
                for pc in page_chunks:
                    pc["page_number"] = page_num
                    pc["chunk_index"] = chunk_index
                    chunk_index += 1
                chunks.extend(page_chunks)
        
        return chunks
