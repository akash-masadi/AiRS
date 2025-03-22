import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import logging
from typing import Optional
import os

class S3Connector:
    """AWS S3 Connector for uploading files to S3"""

    def __init__(self):
        self._load_config()
        self.s3_client = self._create_s3_client()

    def _load_config(self) -> None:
        """Load AWS configuration from environment variables"""
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.s3_bucket_name = os.getenv("S3_BUCKET_NAME")

        if not all([self.aws_access_key_id, self.aws_secret_access_key, self.s3_bucket_name]):
            raise ValueError("Missing AWS configuration in environment variables")

    def _create_s3_client(self):
        """Create and return an S3 client"""
        return boto3.client(
            "s3",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.aws_region,
        )

    def upload_file_to_s3(self, file_path: str, s3_key: str) -> Optional[str]:
        """
        Upload a file to S3 and return the S3 URL.
        
        :param file_path: Path to the file to upload
        :param s3_key: Key (path) in S3 where the file will be stored
        :return: S3 URL of the uploaded file or None if upload fails
        """
        try:
            self.s3_client.upload_file(file_path, self.s3_bucket_name, s3_key)
            s3_url = f"https://{self.s3_bucket_name}.s3.{self.aws_region}.amazonaws.com/{s3_key}"
            return s3_url
        except (NoCredentialsError, PartialCredentialsError) as e:
            logging.error(f"Credentials error: {e}")
            return None
        except Exception as e:
            logging.error(f"Failed to upload file to S3: {e}")
            return None