import logging
import re

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.files.storage import default_storage

S3_URL_REGEX = r"https:\/\/(.*)s3(.*).amazonaws.com\/(.*)"
s3_url_regex = re.compile(S3_URL_REGEX, re.IGNORECASE)

logger = logging.getLogger(__name__)


def build_s3_url(bucket_name, key, region):
    """
    Build an S3 URL by passing the bucket name, key, and region.

    Args:
        bucket_name (str): The name of the S3 bucket.
        key (str): The key name of the object in the S3 bucket.
        region (str): The region of the S3 bucket.

    Returns:
        str: The constructed S3 URL.
    """
    s3_url = "https://{bucket_name}.s3.amazonaws.com/{key}"

    if region:
        s3_url = "https://{bucket_name}.s3-{region}.amazonaws.com/{key}"

    return s3_url.format(bucket_name=bucket_name, region=region, key=key)


def upload_file_obj_to_s3(file_obj, s3_key: str, s3_bucket: str = None, s3_region: str = None):
    """
    Upload a given file object to AWS S3.

    Args:
        file_obj: A file-like object.
        s3_key: The S3 key location.
        s3_bucket: S3 bucket name (optional).
        s3_region: S3 region name (optional).

    Returns:
        str: The S3 URL of the uploaded file.
    """

    s3_bucket = s3_bucket or settings.AWS_STORAGE_BUCKET_NAME
    s3_region = s3_region or settings.AWS_S3_REGION_NAME

    with default_storage.open(s3_key, "wb") as file:
        file.write(file_obj.read())
        file.close()

    s3_url = build_s3_url(s3_bucket, s3_key, region=s3_region)
    logger.info(
        "File uploaded to S3 successfully",
        extra={
            "action": "s3_file_upload",
            "s3_key": s3_key,
            "s3_bucket": s3_bucket,
            "s3_region": s3_region,
            "s3_url": s3_url,
        },
    )

    return s3_url


def split_s3_url(s3_url: str):
    """
    Split an S3 URL into its components.

    Args:
        s3_url (str): The S3 URL to split.

    Returns:
        tuple: A tuple containing the bucket name, key, and region extracted from the S3 URL.
    """
    s3_url_regex = re.compile(r"https:\/\/(.+?)\.s3(?:-(.+?))?.amazonaws.com\/(.+)")

    match = s3_url_regex.match(s3_url)
    if not match:
        return None, None, None

    groups = match.groups()
    if len(groups) != 3:
        return None, None, None

    bucket = groups[0].strip(".") if groups[0] else None
    key = groups[2].strip() if groups[2] else None
    region = groups[1].strip("-") if groups[1] else None

    return bucket, key, region


def _generate_presigned_url(bucket: str, key: str, expires_in: str, region: str = None):
    """
    Generate a presigned URL for accessing an S3 object.

    Args:
        bucket (str): The S3 bucket name.
        key (str): The key of the S3 object.
        expires_in (str): The expiration time for the presigned URL.
        region (str): The AWS region (optional).

    Returns:
        str: The generated presigned URL.

    Raises:
        ClientError: If an error occurs while generating the presigned URL.
    """
    params = {"Bucket": bucket, "Key": key}
    s3_client = boto3.client("s3", region_name=region, config=Config(signature_version="s3v4"))

    try:
        url = s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params=params,
            ExpiresIn=expires_in,
        )
        logger.info("Generated presigned URL: %s", url)
        return url
    except ClientError as e:
        logger.exception(
            "Failed to generate a presigned URL for bucket '%s' and key '%s'", bucket, key
        )
        raise e


def generate_presigned_url(s3_url: str, expires_in: int = 600):
    """
    Generate a publicly accessible presigned URL for a private S3 object.

    Args:
        s3_url (str): The S3 URL of the object.
        expires_in (int): The expiration time in seconds for the presigned URL. Default is 600.

    Returns:
        str: The generated presigned URL.
    """
    if expires_in is None:
        expires_in = settings.DEFAULT_SIGNED_S3_URL_EXPIRY_SECONDS
    s3_bucket, s3_key, s3_region = split_s3_url(s3_url)
    presigned_url = _generate_presigned_url(
        bucket=s3_bucket, key=s3_key, expires_in=expires_in, region=s3_region
    )
    logger.info(
        "Generated presigned url for S3 successfully",
        extra={
            "action": "s3_generate_presigned_url",
            "s3_key": s3_key,
            "s3_bucket": s3_bucket,
            "s3_region": s3_region,
            "s3_url": s3_url,
        },
    )
    return presigned_url
