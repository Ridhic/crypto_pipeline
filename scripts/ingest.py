import requests
import boto3
import json
import psycopg2
import os
import logging
from datetime import datetime

# ------------------------------
# Setup Logging
# ------------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ------------------------------
# Load ENV vars
# ------------------------------
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASS = os.getenv("POSTGRES_PASSWORD")

# ------------------------------
# Fetch tdata from CoinGecko
# ------------------------------
url = "https://api.coingecko.com/api/v3/coins/markets"
params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 10, "page": 1}
response = requests.get(url, params=params)
coins = response.json()

# ------------------------------
# Store raw data to S3
# ------------------------------
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
s3_key = f"raw/crypto_{timestamp}.json"
s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=json.dumps(coins))

logging.info(f"Raw data uploaded to S3 at {s3_key}")

# ------------------------------
# Insert data into PostgreSQL
# ------------------------------
conn = psycopg2.connect(
    host=POSTGRES_HOST,
    database=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASS
)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS crypto_raw (
    id TEXT,
    symbol TEXT,
    name TEXT,
    current_price FLOAT,
    market_cap BIGINT,
    timestamp TIMESTAMP
)
""")

for coin in coins:
    cursor.execute(
        "INSERT INTO crypto_raw (id, symbol, name, current_price, market_cap, timestamp) VALUES (%s, %s, %s, %s, %s, %s)",
        (coin['id'], coin['symbol'], coin['name'], coin['current_price'], coin['market_cap'], datetime.utcnow())
    )

conn.commit()
cursor.close()
conn.close()

logging.info("Data inserted into PostgreSQL")
