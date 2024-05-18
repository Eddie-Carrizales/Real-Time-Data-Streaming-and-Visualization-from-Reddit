import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import nltk
from nltk.tokenize import word_tokenize
from nltk import ne_chunk
import re
import json

from kafka import KafkaProducer

# Initialize NLTK
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

# Create a SparkSession
spark = SparkSession.builder \
    .appName("RedditDataConsumer") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:" + str(pyspark.__version__)) \
    .getOrCreate()

# Define Kafka parameters
kafka_bootstrap_servers = "localhost:9092"
kafka_topic_input = "topic1"
kafka_topic_output = "topic2"

# Define the JSON schema to parse incoming messages
jsonSchema = StructType([
    StructField("type", StringType(), True),
    StructField("post_id", StringType(), True),
    StructField("comment_id", StringType(), True),
    StructField("author", StringType(), True),
    StructField("body", StringType(), True),
    StructField("score", IntegerType(), True),
    StructField("created_utc", DoubleType(), True)
])

# Read data from Kafka topic with specified schema, starting from the earliest offset
stream_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", kafka_topic_input) \
    .option("startingOffsets", "earliest") \
    .load()

# Parse JSON data and select relevant columns
parsed_df = stream_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json("value", jsonSchema).alias("data")) \
    .select("data.*")


# Define a function to process comment body, remove numbers, escape sequences, and punctuations,
# tokenize, and then extract named entities
def extract_nltk_named_entities(text):
    # Convert to string if not already
    text = str(text)

    # Remove numbers, escape sequences, and punctuations
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = re.sub(r'\n', ' ', text)  # Replace escape sequences with space
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuations

    # Tokenize the text
    tokens = word_tokenize(text)

    # Perform part-of-speech tagging
    tagged = nltk.pos_tag(tokens)

    # Extract named entities using NLTK's ne_chunk
    named_entities = ne_chunk(tagged)
    named_entities = [entity for entity in named_entities if isinstance(entity, nltk.tree.Tree)]
    named_entities = [" ".join([token for token, pos in entity.leaves()]) for entity in named_entities]

    return named_entities


# Register the function as a UDF
extract_nltk_named_entities_udf = udf(extract_nltk_named_entities, ArrayType(StringType()))

# Apply the UDF to the comment bodies
entity_df = parsed_df.withColumn("entities", explode(extract_nltk_named_entities_udf(col("body")))) \
    .groupBy("entities") \
    .agg(count("*").alias("count")) \
    .orderBy(col("count").desc())  # Order by count in descending order

# Define a query to write the streaming data to console
query = entity_df \
    .writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

# Prepare data for sending to Kafka topic2
def prepare_kafka_message(row):
    return json.dumps({"entity": row["entities"], "count": row["count"]})

# Send data to Kafka topic2
def send_to_kafka(stream_df, batch_id):
    producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers)
    for row in stream_df.toLocalIterator():
        kafka_message = prepare_kafka_message(row)
        producer.send(kafka_topic_output, value=kafka_message.encode('utf-8'))
        print(f"Sent message to Kafka topic2: {kafka_message}")
    producer.flush()
    producer.close()

# Write data to Kafka topic2
entity_df.writeStream.outputMode("complete").foreachBatch(send_to_kafka).start().awaitTermination()


# Await termination of the query
query.awaitTermination()
