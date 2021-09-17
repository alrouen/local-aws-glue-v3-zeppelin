# This is Glue V3 sample job to use Delta.io
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

spark = SparkSession.builder \
        .config('spark.sql.extensions','io.delta.sql.DeltaSparkSessionExtension') \
        .config('spark.sql.catalog.spark_catalog','org.apache.spark.sql.delta.catalog.DeltaCatalog') \
        .getOrCreate()
        
sc = spark.sparkContext
# To include required dependencies for Delta.io :
#   - retrieve jars from an ivy cache (ie. after this: pyspark --packages io.delta:delta-core_2.12:1.0.0)
#   - upload them into a s3 bucket available from this job
#   - in job details / dependent jar paths add s3 url of each jar 
#   ie. For delta 2.12 v1.0.0 the list is the following (one line, comma seperated) : 
#   s3://mybucket/jars/io.delta-1.0.0/io.delta_delta-core_2.12-1.0.0.jar,
#   s3://mybucket/jars/io.delta-1.0.0/com.ibm.icu_icu4j-58.2.jar,
#   s3://mybucket/jars/io.delta-1.0.0/org.abego.treelayout_org.abego.treelayout.core-1.0.3.jar,
#   s3://mybucket/jars/io.delta-1.0.0/org.antlr_antlr-runtime-3.5.2.jar,
#   s3://mybucket/jars/io.delta-1.0.0/org.antlr_antlr4-4.7.jar,
#   s3://mybucket/jars/io.delta-1.0.0/org.antlr_antlr4-runtime-4.7.jar,
#   s3://mybucket/jars/io.delta-1.0.0/org.antlr_ST4-4.0.8.jar,
#   s3://mybucket/jars/io.delta-1.0.0/org.glassfish_javax.json-1.0.4.jar
# 
# Finally load the delta core module into this job :
sc.addPyFile("io.delta_delta-core_2.12-1.0.0.jar")

glueContext = GlueContext(sc)
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Import Delta 
from delta.tables import DeltaTable

bucket = "s3a://target-bucket/delta"

# Create a table
print("############# Creating a table ###############")
data = spark.range(0, 5)
data.write.format("delta").mode("overwrite").save(bucket)

# Read the table
print("############ Reading the table ###############")
df = spark.read.format("delta").load(bucket)
df.show()

# Upsert (merge) new data
print("########### Upsert new data #############")
newData = spark.range(0, 20)

deltaTable = DeltaTable.forPath(spark, bucket)

deltaTable.alias("oldData")\
    .merge(
    newData.alias("newData"),
    "oldData.id = newData.id")\
    .whenMatchedUpdate(set={"id": col("newData.id")})\
    .whenNotMatchedInsert(values={"id": col("newData.id")})\
    .execute()

deltaTable.toDF().show()

# Update table data
print("########## Overwrite the table ###########")
data = spark.range(5, 10)
data.write.format("delta").mode("overwrite").save(bucket)
deltaTable.toDF().show()

deltaTable = DeltaTable.forPath(spark, bucket)

# Update every even value by adding 100 to it
print("########### Update to the table(add 100 to every even value) ##############")
deltaTable.update(
    condition=expr("id % 2 == 0"),
    set={"id": expr("id + 100")})

deltaTable.toDF().show()

# Delete every even value
print("######### Delete every even value ##############")
deltaTable.delete(condition=expr("id % 2 == 0"))
deltaTable.toDF().show()

# Read old version of data using time travel
print("######## Read old data using time travel ############")
df = spark.read.format("delta").option("versionAsOf", 0).load(bucket)
df.show()

job.commit()
