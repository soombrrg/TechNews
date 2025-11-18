#!/bin/bash
set -e  # Output on error

# Setting alias
/usr/bin/mc alias set s3-minio http://s3:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD};
# Create bucket if not exists
/usr/bin/mc mb s3-minio/local-static 2>/dev/null || true;  # Skip error
/usr/bin/mc anonymous set public s3-minio/local-static;
echo "Minio ready with default bucket.";
