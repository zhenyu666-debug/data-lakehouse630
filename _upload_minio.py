import sys
from minio import Minio

client = Minio(
    "minio:9000",
    access_key="admin",
    secret_key="password",
    secure=False
)

bucket = "warehouse"
if not client.bucket_exists(bucket):
    client.make_bucket(bucket)

file_path = "/data/UserBehavior.csv"
object_name = "UserBehavior.csv"

print(f"Uploading {file_path} to {bucket}/{object_name}...")
client.fput_object(bucket, object_name, file_path)
print("Upload complete!")
