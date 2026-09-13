import os
from typing import Optional

class StorageProvider:
    def upload(self, local_path: str, dest_key: str) -> str:
        raise NotImplementedError
    def download(self, key: str, local_path: str) -> str:
        raise NotImplementedError
    def generate_signed_url(self, key: str, expires_seconds: int = 3600) -> str:
        raise NotImplementedError

class LocalStorageProvider(StorageProvider):
    def __init__(self, base_path: str = "uploads"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def upload(self, local_path: str, dest_key: str) -> str:
        # For local provider, we simply return the local path
        return local_path

    def download(self, key: str, local_path: str) -> str:
        return key

    def generate_signed_url(self, key: str, expires_seconds: int = 3600) -> str:
        # Not implemented for local
        return key
