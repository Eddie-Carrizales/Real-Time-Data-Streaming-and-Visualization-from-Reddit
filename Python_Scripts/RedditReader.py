import praw
from confluent_kafka import Producer
import json
import time

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id="A7OphWx0H-oLzNN_YIAOhQ",
    client_secret="soKAstRzQKKLT7KsLKXxcTwk6XKuug",
    user_agent="A Reddit reader script that will read and stream information to Kafka topic."
)

# Initialize Kafka Producer
kafka_producer = Producer({'bootstrap.servers': 'localhost:9092'})

# Define the Kafka topic to which data will be published
kafka_topic = 'topic1'


def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')


# Function to publish data to Kafka
def publish_to_kafka(data):
    # Convert data to JSON format
    message = json.dumps(data)
    # Publish message to Kafka topic
    kafka_producer.produce(kafka_topic, message.encode('utf-8'), callback=delivery_report)
    kafka_producer.poll(0)


# Function to fetch Reddit comments and publish to Kafka
def fetch_and_publish():
    subreddit = reddit.subreddit("wallstreetbets")

    # Fetch new comments using comment stream
    for comment in subreddit.stream.comments():
        comment_data = {
            'type': 'comment',
            'post_id': comment.link_id,
            'comment_id': comment.id,
            'author': str(comment.author),
            'body': comment.body,
            'score': comment.score,
            'created_utc': comment.created_utc
        }
        publish_to_kafka(comment_data)


# Main function to start fetching and publishing data
if __name__ == '__main__':
    while True:
        print("Writing comments to Kafka")
        fetch_and_publish()

        # Sleep for 5 minutes
        # time.sleep(300)

        # Sleep for 1 minutes
        time.sleep(60)
