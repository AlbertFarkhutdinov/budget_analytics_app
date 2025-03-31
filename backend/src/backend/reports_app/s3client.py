"""
Module providing an interface for interacting with S3 storage.

This module defines a client class for handling S3 operations such as listing,
saving, loading, and deleting objects.

"""
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
    """Interface for interacting with S3 storage."""

    def __init__(self) -> None:
        """Initialize the S3 client with configuration settings."""
        self.s3config = S3Settings()
        self.bucket = self.s3config.s3_bucket
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=self.s3config.s3_access_key_id,
            aws_secret_access_key=self.s3config.s3_secret_access_key,
        )

    def get_s3path(self, remote_path: str) -> str:
        """
        Construct a S3 path.

        Parameters
        ----------
        remote_path : str
            The relative path of the object in S3.

        Returns
        -------
        str
            The full S3 URI.

        """
        s3path = Path(self.bucket) / remote_path
        return f's3://{s3path}'

    def list_directory(self, *directories) -> list[str]:
        """
        List the contents of a directory in S3.

        Parameters
        ----------
        *directories : str
            The directory path components.

        Returns
        -------
        list of str
            A list of object keys in the specified directory.

        """
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
        """
        Save a JSON object to S3.

        Parameters
        ----------
        json_data : ReportType
            The data to store in S3.
        remote_path : str
            The target S3 path.

        """
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
        """
        Load a JSON object from S3.

        Parameters
        ----------
        remote_path : str
            The S3 path to retrieve.

        Returns
        -------
        ReportType
            The retrieved JSON data.

        """
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
        """
        Remove an object from S3.

        Parameters
        ----------
        remote_path : str
            The S3 path to delete.

        """
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
