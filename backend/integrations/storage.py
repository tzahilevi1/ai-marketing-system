import io
import boto3
from botocore.exceptions import ClientError
from config import settings


class StorageClient:
    def __init__(self) -> None:
        if settings.aws_access_key_id:
            self.s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region,
            )
            self.bucket = settings.aws_s3_bucket
        else:
            self.s3 = None
            self.bucket = None

    def upload(self, key: str, data: bytes, content_type: str = "image/webp") -> str:
        if not self.s3:
            return f"https://cdn.example.com/{key}"
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return f"https://{self.bucket}.s3.{settings.aws_region}.amazonaws.com/{key}"

    def presigned_url(self, key: str, expires: int = 3600) -> str:
        if not self.s3:
            return f"https://cdn.example.com/{key}"
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires,
        )


storage = StorageClient()
