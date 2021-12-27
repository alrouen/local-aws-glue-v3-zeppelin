# Export Glue v3 from Aws Glue

with the glue job `aws-glue-export-job.py`, create a Glue job in your AWS environment with :

    - Glue version set to Glue v3
    - A IAM role capable to write to one of your S3 bucket

edit this job script to set TARGET_BUCKET to your target S3 bucket, on which will be stored the AWS Glue v3 backup

# Import the Glue v3 archive

    - From the S3 bucket, download the glue3.zip file
    - convert this zip file to tgz archive, and rename it 'glue3-opt-amazon.tgz', making sure the archive preserver the /opt/amazon folder structure
    - copy the tgz file into the docker/zeppelin or docker/jupyter folder of this cloned repo

# Zeppelin Notebook
## Build docker image

    cd docker/zeppelin
    docker build -t gluedev . 

## Run image

    docker run -it --rm --name gluedev -p 8080:8080 -p 7077:7077 -p 9001:9001 -v $PWD/logs:/logs -v $PWD/notebook:/notebook -e ZEPPELIN_LOG_DIR='/logs' -e ZEPPELIN_NOTEBOOK_DIR='/notebook' -v /path/to/your/.aws:/root/.aws:ro gluedev

The .aws volume is only required if you want your local job to get access to your AWS environment (ie. bucket S3).

## Zeppelin access

    http://localhost:9001

# Jupyter Notebook
## Build docker image

    cd docker/jupyter

    docker build -t gluedev .


## Run image

    docker run -it --name gluedev -p 4041:4040 -p 8889:8888 -e JUPYTER_ENABLE_LAB=yes -v ~/.aws:/home/jovyan/.aws:ro -v ~/YOUR_LOCAL_JUPYTER_FOLDER:/home/jovyan gluedev

- The .aws volume is only required if you want your local job to get access to your AWS environment (ie. bucket S3).

- The folder `~/YOUR_LOCAL_JUPYTER_FOLDER` is used for sharing the notebook files with your host machine.

## Jupyter access
Check output of the previous command to get the token. For instance:

`http://127.0.0.1:8888/?token=2f79af840450b332bea0d34e16f1189acab90449a5caec62`
    
# S3 access :

To enable AWS S3 access with your AWS credential just add this line in your notebook :

    spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.aws.credentials.provider", "com.amazonaws.auth.DefaultAWSCredentialsProviderChain")
    
(source: http://wrschneider.github.io/2019/02/02/spark-credentials-file.html)




