from pyspark.sql import SparkSession
from dotenv import load_dotenv
import os
import logging

# ------------------------------
# Setup Logging
# ------------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ------------------------------
# Load environment variables
# ------------------------------
load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# ------------------------------
# Create Spark session
# ------------------------------
spark = SparkSession.builder \
    .appName("CryptoPipeline") \
    .config("spark.jars", "/opt/spark/jars/postgresql-42.7.1.jar") \
    .getOrCreate()

# ------------------------------
# Read raw data from PostgreSQL
# ------------------------------
logging.info("Reading data from 'crypto_raw' table...")
df = spark.read \
    .format("jdbc") \
    .option("url", f"jdbc:postgresql://{POSTGRES_HOST}:5432/{POSTGRES_DB}") \
    .option("dbtable", "crypto_raw") \
    .option("user", POSTGRES_USER) \
    .option("password", POSTGRES_PASSWORD) \
    .option("driver", "org.postgresql.Driver") \
    .load()

# ------------------------------
# Filter relevant columns
# ------------------------------
logging.info("Filtering selected columns...")
df_filtered = df.select("id", "symbol", "name", "current_price", "market_cap")

# ------------------------------
# Write filtered data back to PostgreSQL
# ------------------------------
logging.info("Writing filtered data to 'crypto_filtered' table...")
df_filtered.write \
    .format("jdbc") \
    .option("url", f"jdbc:postgresql://{POSTGRES_HOST}:5432/{POSTGRES_DB}") \
    .option("dbtable", "crypto_filtered") \
    .option("user", POSTGRES_USER) \
    .option("password", POSTGRES_PASSWORD) \
    .option("driver", "org.postgresql.Driver") \
    .mode("overwrite") \
    .save()

logging.info("Transformation complete.")
