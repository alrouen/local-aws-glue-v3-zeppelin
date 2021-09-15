import sys
import zipfile
from zipfile import ZipFile
import os
from os.path import basename
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

import boto3
from botocore.exceptions import ClientError

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
logger = glueContext.get_logger()
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Parameters
TARGET_BUCKET='your-bucket-name-with-rw-acces'

# Send file to S3
def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logger.error(e)
        return False
    return True

def zipfolder(zipFileName, target_dir):            
    zipobj = zipfile.ZipFile(zipFileName, 'w', compression=zipfile.ZIP_DEFLATED)
    rootlen = len(target_dir) + 1
    for base, dirs, files in os.walk(target_dir):
        for file in files:
            fn = os.path.join(base, file)
            zipobj.write(fn, fn[rootlen:])

def env():
    logger.info('Env:')
    e = ""
    for k, v in sorted(os.environ.items()):
        e = e + f'\n{k} : {v}'
    logger.info(e)

def content():
    logger.info('Content:')
    out = ""
    for root, dirs, files in os.walk("/opt/amazon"):
        path = root.split(os.sep)
        out = out + f'\n{(len(path) - 1) * "---"} {os.path.basename(root)}'
        for file in files:
            out = out + f'\n{len(path) * "---"} {file}'
    logger.info(out)


content()
env()
zipfolder('/tmp/glue3.zip', '/opt/amazon')
upload_file('/tmp/glue3.zip', TARGET_BUCKET)

job.commit()
