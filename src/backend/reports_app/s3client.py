"""The module contains the interface for work with S3 storage."""
import json
from pathlib import Path

import fsspec
from dotenv import load_dotenv

from backend.reports_app.reports_generator import ReportType
from backend.reports_app.settings import S3Settings

load_dotenv()


class S3Client:
    """The interface for work with S3 storage."""

    def __init__(self) -> None:
        """Initialize self. See help(type(self)) for accurate signature."""
        self.s3config = S3Settings()
        self.bucket = Path(self.s3config.s3_bucket)
        self.filesystem = None
        self.reload()

    def reload(self) -> None:
        """Reload S3 filesystem."""
        self.filesystem = fsspec.filesystem(
            protocol='s3',
            key=self.s3config.s3_access_key_id,
            secret=self.s3config.s3_secret_access_key,
        )
        self.filesystem.clear_instance_cache()

    def get_s3path(
        self,
        remote_path: str,
        *,
        with_root: bool = False,
    ) -> str:
        s3path = self.bucket / remote_path
        if with_root:
            return f's3://{s3path}'
        return str(s3path)

    def list_directory(self, *directories) -> list[str]:
        """List a directory."""
        return self.filesystem.ls(str(self.bucket.joinpath(*directories)))

    def download_file(self, remote_path: str, local_path: str) -> None:
        """Download single file from a remote storage."""
        return self.filesystem.get_file(
            rpath=self.get_s3path(remote_path),
            lpath=local_path,
        )

    def upload_file(self, local_path: str, remote_path: str) -> None:
        """Upload single file to a remote storage."""
        return self.filesystem.put_file(
            lpath=local_path,
            rpath=self.get_s3path(remote_path),
        )

    def save_json(
        self,
        json_data: ReportType,
        remote_path: str,
    ) -> None:
        """Save JSON data to S3."""
        s3file = self.get_s3path(remote_path=remote_path)
        with self.filesystem.open(s3file, mode='w') as s3file:
            json.dump(json_data, s3file)

    def load_json(self, remote_path: str) -> ReportType:
        """Load JSON data from S3."""
        s3file = self.get_s3path(remote_path=remote_path)
        if not self.filesystem.exists(s3file):
            return {}
        with self.filesystem.open(s3file) as s3file:
            return json.load(s3file)
