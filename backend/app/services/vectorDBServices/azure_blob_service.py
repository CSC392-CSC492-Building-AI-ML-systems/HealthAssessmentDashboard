from typing import List
from azure.storage.blob.aio import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class AzureBlobService:
    def __init__(self):
        self.connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        self.container_name = settings.AZURE_CONTAINER_NAME
        self.vector_container_name = "vector-databases"  # Separate container for vector DBs
        self.client = BlobServiceClient.from_connection_string(self.connection_string)

    async def upload_blob(self, filename: str, data: bytes, content_type: str = None, container_name: str = None) -> str:
        """Upload a blob to Azure Storage"""
        try:
            container = container_name or self.container_name
            blob_client = self.client.get_blob_client(
                container=container, 
                blob=filename
            )
            
            await blob_client.upload_blob(
                data, 
                content_type=content_type,
                overwrite=True
            )
            
            return blob_client.url
            
        except Exception as e:
            logger.error(f"Error uploading blob {filename}: {str(e)}")
            raise

    async def download_blob(self, filename: str, container_name: str = None) -> bytes:
        """Download a blob from Azure Storage"""
        try:
            container = container_name or self.vector_container_name
            blob_client = self.client.get_blob_client(
                container=container, 
                blob=filename
            )
            
            download_stream = await blob_client.download_blob()
            return await download_stream.readall()
            
        except ResourceNotFoundError:
            logger.warning(f"Blob {filename} not found")
            raise
        except Exception as e:
            logger.error(f"Error downloading blob {filename}: {str(e)}")
            raise

    async def delete_blob(self, filename: str, container_name: str = None) -> bool:
        """Delete a blob from Azure Storage"""
        try:
            container = container_name or self.container_name
            blob_client = self.client.get_blob_client(
                container=container, 
                blob=filename
            )
            
            await blob_client.delete_blob()
            return True
            
        except ResourceNotFoundError:
            logger.warning(f"Blob {filename} not found for deletion")
            return False
        except Exception as e:
            logger.error(f"Error deleting blob {filename}: {str(e)}")
            raise

    async def blob_exists(self, filename: str, container_name: str = None) -> bool:
        """Check if a blob exists in Azure Storage"""
        try:
            container = container_name or self.container_name
            blob_client = self.client.get_blob_client(
                container=container, 
                blob=filename
            )
            
            properties = await blob_client.get_blob_properties()
            return True
            
        except ResourceNotFoundError:
            return False
        except Exception as e:
            logger.error(f"Error checking blob existence {filename}: {str(e)}")
            return False

    async def get_blob_url(self, filename: str, container_name: str = None) -> str:
        """Get the URL of a blob"""
        container = container_name or self.container_name
        blob_client = self.client.get_blob_client(
            container=container, 
            blob=filename
        )
        return blob_client.url

    async def list_blobs(self, prefix: str = "", container_name: str = None) -> List[str]:
        """List blobs with optional prefix filter"""
        try:
            container = container_name or self.container_name
            container_client = self.client.get_container_client(container)
            
            blob_names = []
            async for blob in container_client.list_blobs(name_starts_with=prefix):
                blob_names.append(blob.name)
            
            return blob_names
            
        except Exception as e:
            logger.error(f"Error listing blobs with prefix {prefix}: {str(e)}")
            return []