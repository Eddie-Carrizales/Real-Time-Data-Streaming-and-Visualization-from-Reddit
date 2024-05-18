#!/bin/bash

# Function to prompt user for directory path
get_directory_path() {
    while true; do
        read -p "Enter $1 directory path: " dir_path
        if [ -z "$dir_path" ]; then
            echo "Error: No directory path provided. Please try again." >&2
        elif [ ! -d "$dir_path" ]; then
            echo "Error: Directory '$dir_path' does not exist. Please try again." >&2
        else
            echo "$dir_path"
            break
        fi
    done
}

# Function to run command in a new Terminal window
run_command() {
    # Open Terminal window and run the command
    osascript -e "tell application \"Terminal\" to do script \"$*\""
}

# Prompt user for directory paths
KAFKA_PATH=$(get_directory_path "Kafka")
if [ -n "$KAFKA_PATH" ]; then
    run_command "cd $KAFKA_PATH && ./bin/zookeeper-server-start.sh config/zookeeper.properties"
    run_command "cd $KAFKA_PATH && ./bin/kafka-server-start.sh config/server.properties"
    run_command "cd $KAFKA_PATH && ./bin/kafka-topics.sh --create --topic topic1 --bootstrap-server localhost:9092"
    run_command "cd $KAFKA_PATH && ./bin/kafka-topics.sh --create --topic topic2 --bootstrap-server localhost:9092"
fi

PYTHON_SCRIPT_DIR=$(get_directory_path "Python script")
if [ -n "$PYTHON_SCRIPT_DIR" ]; then
    run_command "cd $PYTHON_SCRIPT_DIR && python3 RedditReader.py"
    run_command "cd $PYTHON_SCRIPT_DIR && python3 SparkCluster.py"
fi

LOGSTASH_PATH=$(get_directory_path "Logstash")
if [ -n "$LOGSTASH_PATH" ]; then
    run_command "cd $LOGSTASH_PATH && ./bin/logstash -f config/logstash-reddit.conf"
fi

ELASTICSEARCH_PATH=$(get_directory_path "Elasticsearch")
if [ -n "$ELASTICSEARCH_PATH" ]; then
    run_command "cd $ELASTICSEARCH_PATH && ./bin/elasticsearch"
fi

KIBANA_PATH=$(get_directory_path "Kibana")
if [ -n "$KIBANA_PATH" ]; then
    run_command "cd $KIBANA_PATH && ./bin/kibana"
fi

# Message to go to "localhost:5601"
echo "Please go to http://localhost:5601 on your web browser to open Kibana and visualize the data."
