# app/services/storage_service.py
from app.clients.supabase_api_client import supabase
from app.exceptions.decorators import handle_exceptions
from app.exceptions.base_exceptions import ExternalServiceError

class StorageService:

    @handle_exceptions
    async def upload_file(self, bucket: str, file_path: str, file_content: bytes, token: str):
        """
        Uploads a file to a Supabase storage bucket using the user's JWT for authorization.
        Raises ExternalServiceError on failure.
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            result = supabase.storage.from_(bucket).upload(file_path, file_content, headers=headers)
            if result.get("error"):
                raise ExternalServiceError(f"Upload failed: {result['error']['message']}")
            return result
        except Exception as e:
            raise ExternalServiceError(f"Supabase upload failed: {str(e)}")

    @handle_exceptions
    async def download_file(self, bucket: str, file_path: str, token: str) -> bytes:
        """
        Downloads a file from a Supabase storage bucket using the user's JWT for authorization.
        Raises ExternalServiceError if the file is not found or any other error occurs.
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            result = supabase.storage.from_(bucket).download(file_path, headers=headers)
            if result is None:
                raise ExternalServiceError(f"File not found in bucket '{bucket}': {file_path}")
            return result
        except Exception as e:
            raise ExternalServiceError(f"Supabase download failed: {str(e)}")
