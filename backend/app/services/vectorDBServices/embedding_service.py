import openai
from typing import List
from app.core.config import settings

class EmbeddingService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            response = await openai.Embedding.acreate(
                model="text-embedding-ada-002",
                input=text
            )
            return response['data'][0]['embedding']
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 1536

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = []
        
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                response = await openai.Embedding.acreate(
                    model="text-embedding-ada-002",
                    input=batch
                )
                
                batch_embeddings = [item['embedding'] for item in response['data']]
                embeddings.extend(batch_embeddings)
                
            except Exception as e:
                print(f"Error generating embeddings for batch {i//batch_size}: {e}")
                embeddings.extend([[0.0] * 1536] * len(batch))
        
        return embeddings