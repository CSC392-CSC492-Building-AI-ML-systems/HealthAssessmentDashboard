import io
import PyPDF2
from typing import List, Tuple, Dict, Any
from app.services.vectorDBServices.embedding_service import EmbeddingService

class FileProcessingService:
    def __init__(self):
        self.embedding_service = EmbeddingService()

    async def process_file(self, content: bytes, filename: str, drug_id: int) -> Tuple[List[Dict], List[List[float]]]:
        """Process PDF file content, extract text, chunk, and generate embeddings"""
        
        if not filename.lower().endswith('.pdf'):
            raise ValueError(f"Only PDF files are supported. Received: {filename}")
        
        # Extract all text from PDF
        text_content = await self._extract_text_from_pdf(content)
        
        # Chunk the text
        chunks = self._chunk_text(text_content, drug_id, filename)
        
        # Generate embeddings for chunks
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = await self.embedding_service.generate_embeddings_batch(chunk_texts)
        
        return chunks, embeddings

    async def _extract_text_from_pdf(self, content: bytes) -> str:
        """Extract all text from PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += f"\n[Page {page_num}]\n{page_text}\n"
                except Exception as e:
                    print(f"Error extracting text from page {page_num}: {e}")
                    continue
            
            if not text.strip():
                raise ValueError("No text could be extracted from the PDF")
            
            return text.strip()
            
        except Exception as e:
            raise ValueError(f"Error processing PDF: {str(e)}")

    def _chunk_text(self, text: str, drug_id: int, filename: str, 
                   chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
        """Split text into overlapping chunks"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            
            if chunk_text.strip():
                chunk_metadata = {
                    "drug_id": drug_id,
                    "filename": filename,
                    "chunk_index": len(chunks),
                    "text": chunk_text.strip(),
                    "word_count": len(chunk_words),
                    "char_count": len(chunk_text)
                }
                chunks.append(chunk_metadata)
        
        return chunks