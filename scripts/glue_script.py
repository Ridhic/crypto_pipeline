import sys
import json
import boto3
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

secret_name = "redshift/crypto-user"
region_name = "us-east-1"

session = boto3.session.Session()
client = session.client(service_name="secretsmanager", region_name=region_name)
get_secret_value_response = client.get_secret_value(SecretId=secret_name)
secret = json.loads(get_secret_value_response["SecretString"])

redshift_user = secret["username"]
redshift_password = secret["password"]
redshift_host = secret["host"]
redshift_port = secret["port"]
redshift_db = secret["database"]

s3_path = "s3://ridhic-crypto/raw/"
df = spark.read.json(s3_path)

df_filtered = df.select(
    "id", "symbol", "name", "current_price", "market_cap"
)

df_filtered.write \
    .format("jdbc") \
    .option("url", f"jdbc:redshift://{redshift_host}") \
    .option("user", redshift_user) \
    .option("password", redshift_password) \
    .option("dbtable", "crypto_filtered") \
    .option("driver", "com.amazon.redshift.jdbc.Driver") \
    .mode("overwrite") \
    .save()

job.commit()
