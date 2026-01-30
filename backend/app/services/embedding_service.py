"""Embedding service using Voyage AI."""
import asyncio
from typing import Optional

import httpx

from app.config import settings


class EmbeddingService:
    """Service for generating text embeddings using Voyage AI."""
    
    VOYAGE_API_URL = "https://api.voyageai.com/v1/embeddings"
    MODEL = "voyage-2"
    BATCH_SIZE = 128
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize embedding service.
        
        Args:
            api_key: Voyage AI API key (defaults to settings)
        """
        self.api_key = api_key or settings.VOYAGE_API_KEY
    
    async def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        embeddings = await self.embed_batch([text])
        return embeddings[0]
    
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.BATCH_SIZE):
            batch = texts[i:i + self.BATCH_SIZE]
            embeddings = await self._embed_with_retry(batch)
            all_embeddings.extend(embeddings)
        
        return all_embeddings
    
    async def _embed_with_retry(
        self,
        texts: list[str],
        max_retries: int = 3,
        base_delay: float = 1.0,
    ) -> list[list[float]]:
        """
        Make embedding API call with exponential backoff retry.
        
        Args:
            texts: Texts to embed
            max_retries: Maximum number of retries
            base_delay: Base delay between retries
            
        Returns:
            List of embedding vectors
        """
        async with httpx.AsyncClient() as client:
            for attempt in range(max_retries):
                try:
                    response = await client.post(
                        self.VOYAGE_API_URL,
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "input": texts,
                            "model": self.MODEL,
                        },
                        timeout=60.0,
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        # Sort by index to maintain order
                        sorted_data = sorted(data["data"], key=lambda x: x["index"])
                        return [item["embedding"] for item in sorted_data]
                    
                    elif response.status_code == 429:
                        # Rate limited, wait and retry
                        delay = base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue
                    
                    else:
                        response.raise_for_status()
                
                except httpx.TimeoutException:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue
                    raise
        
        raise Exception(f"Failed to embed after {max_retries} retries")


# Singleton instance
embedding_service = EmbeddingService()