import boto3
from botocore.client import Config
from app.config import settings


def _client():
    return boto3.client(
        "s3",
        endpoint_url=settings.minio_endpoint,
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        config=Config(signature_version="s3v4"),
    )


def ensure_bucket():
    c = _client()
    existing = [b["Name"] for b in c.list_buckets().get("Buckets", [])]
    if settings.minio_bucket not in existing:
        c.create_bucket(Bucket=settings.minio_bucket)


def put_raw(key: str, data: bytes):
    ensure_bucket()
    _client().put_object(Bucket=settings.minio_bucket, Key=key, Body=data)
    return key
