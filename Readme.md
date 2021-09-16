# Export Glue v3 from Aws Glue

with the glue job 'aws-glue-export-job.py', create a Glue job in your AWS environment with :

    - Glue version set to Glue v3
    - A IAM role capable to write to one of your S3 bucket

edit this job script to set TARGET_BUCKET to your target S3 bucket, on which will be stored the AWS Glue v3 backup

# Import the Glue v3 archive

    - From the S3 bucket, download the glue3.zip file
    - convert this zip file to tgz archive, and rename it 'glue3-opt-amazon.tgz', making sure the archive preserver the /opt/amazon folder structure
    - copy the tgz file into the docker folder of this cloned repo

# Build docker image

    cd docker
    docker build -t gluedev . 

# Run image

    docker run -it --rm --name gluedev -p 8080:8080 -p 7077:7077 -p 9001:9001 -v $PWD/logs:/logs -v $PWD/notebook:/notebook -e ZEPPELIN_LOG_DIR='/logs' -e ZEPPELIN_NOTEBOOK_DIR='/notebook' -v /path/to/your/.aws:/root/.aws:ro gluedev

The .aws volume is only required if you want your local job to get access to your AWS environment (ie. bucket S3).

# Zeppelin access

    http://localhost:9001
    
# S3 access :

To enable AWS S3 access with your AWS credential just add this line in your notebook :

    spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.aws.credentials.provider", "com.amazonaws.auth.DefaultAWSCredentialsProviderChain")
    
(source: http://wrschneider.github.io/2019/02/02/spark-credentials-file.html)




