"""The module contains the interface for work with S3 storage."""
import json
import logging
from pathlib import Path

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

from backend.reports_app.reports_generator import ReportType
from backend.reports_app.settings import S3Settings

load_dotenv()
logger = logging.getLogger(__name__)


class S3Client:
    """The interface for work with S3 storage."""

    def __init__(self) -> None:
        """Initialize self. See help(type(self)) for accurate signature."""
        self.s3config = S3Settings()
        self.bucket = self.s3config.s3_bucket
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=self.s3config.s3_access_key_id,
            aws_secret_access_key=self.s3config.s3_secret_access_key,
        )

    def get_s3path(self, remote_path: str) -> str:
        s3path = Path(self.bucket) / remote_path
        return f's3://{s3path}'

    def list_directory(self, *directories) -> list[str]:
        """List a directory."""
        prefix = str(Path('/').joinpath(*directories)).strip('/')
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix,
            )
        except ClientError as exc:
            logger.error('Error listing directory: %s', str(exc))
            return []
        return [
            resp_obj['Key']
            for resp_obj in response.get('Contents', [])
        ]

    def save_object(
        self,
        json_data: ReportType,
        remote_path: str,
    ) -> None:
        """Save an object to S3."""
        try:
            self.s3.put_object(
                Bucket=self.bucket,
                Key=remote_path,
                Body=json.dumps(json_data),
                ContentType='application/json',
            )
        except (NoCredentialsError, ClientError) as exc:
            logger.error('Error saving JSON: %s', str(exc))
        logger.info(
            'Data are saved into "%s"',
            self.get_s3path(remote_path=remote_path),
        )

    def load_object(self, remote_path: str) -> ReportType:
        """Load an object from S3."""
        try:
            response = self.s3.get_object(
                Bucket=self.bucket,
                Key=remote_path,
            )
        except self.s3.exceptions.NoSuchKey:
            logger.warning(
                '"%s" is not found',
                self.get_s3path(remote_path=remote_path),
            )
            return {}
        except (NoCredentialsError, ClientError) as exc:
            logger.error('Error loading JSON: %s', str(exc))
            return {}
        json_data = json.loads(response['Body'].read().decode('utf-8'))
        logger.info(
            'Data are loaded from "%s"',
            self.get_s3path(remote_path=remote_path),
        )
        return json_data

    def remove_object(self, remote_path: str) -> None:
        """Remove an object from S3."""
        try:
            self.s3.delete_object(
                Bucket=self.bucket,
                Key=remote_path,
            )
        except (NoCredentialsError, ClientError) as exc:
            logger.error('Error removing object: %s', str(exc))
        logger.info(
            'Data are removed from "%s"',
            self.get_s3path(remote_path=remote_path),
        )
