# Real-Time-Data-Streaming-and-Visualization-from-Reddit
A Spark Streaming application that will continuously read text data from Reddit, analyze the data for named entities, and send their counts to Apache Kafka. A pipeline using Elasticsearch and Kibana will read the data from Kafka and analyze it visually.

# Notes:
I have included detailed (manual) instructions at the end, you can follow those instructions opening each terminal to get everything running.

Alternatively, I created automatic instructions, i.e., two bash files (one that can run on MAC OS and one that can run on WSL (Windows Subsystem for Linux)). The bash file will simply ask for each directory (for kafka folder, logstash folder, elasticsearch folder, etc), and running this bash file will open everything for you.

After manually opening all terminals or running the bash file. You can open localhost:5601 on your web browser and view incoming data in the discover panel.
Note: The Terminals must stay open.

I have also included bar graphs of the data at 1min, 5min, 15min, 30min, 45min, and 60min intervals of the top 10 named entities for the r/Technology subreddit.

# Instructions (Automatic):

### Before running please:
1. Go to the “Additional_config_files” folder, and copy the “logstash-reddit.conf” file and paste it in your logstash install directory in your “config” folder
Note: This is a pipeline file that grabs from topic2 and sends to elasticsearch

2. Go to the “Additional_config_files” folder, and copy the “elasticsearch.yml” file and paste it in your elasticsearch install directory in your “config” folder
Note: It will ask you to replace the file which is fine, it just changes a setting to disable advanced security (allowing local connections, you may not need to do this step)

3. Make sure you have python 3 and the following installed:
    pip install praw
    
    pip install confluent-kafka
    
    pip install pyspark
    
    pip install nltk
    
    pip install kafka-python


### Directions to run the bash scripts:

1. Go to the directory where bash script is stored

    cd ~/path/to/directory


2. Make the script executable using the following command

    chmod +x run_all_mac.sh

    or

    chmod +x run_all_wsl.sh


3. Run the bash script

    ./run_all_mac.sh

    or

    ./run_all_wsl.sh



# Instructions (Manual):

----Terminal window 1 (start zookeper)----

### 1. Navigate to kafka folder installation

Example:
cd kafka_2.13-3.7.0


### 2. Start the ZooKeeper service

bin/zookeeper-server-start.sh config/zookeeper.properties


----Terminal window 2 (start broker)----

### 3. On another terminal window navigate to kafka folder installation

Example:
cd kafka_2.13-3.7.0

### 4. start the broker service on that other window

bin/kafka-server-start.sh config/server.properties


----Terminal window 3 (To create a topic)----

### 5. open another terminal and go to kafka folder installation

Example:
cd kafka_2.13-3.7.0


### 6. create topic1 and topic2 (replace topic-name with your topic name)

General Format:
bin/kafka-topics.sh --create --topic topic-name --bootstrap-server localhost:9092

Example:
bin/kafka-topics.sh --create --topic topic1 --bootstrap-server localhost:9092

Example:
bin/kafka-topics.sh --create --topic topic2 --bootstrap-server localhost:9092


---Terminal window 4 OR PyCharm----

### 7. run python script to write to read from reddit and write to topic1

python3 main.py


---Terminal window 5 (read from topic1 write to topic2) ----

### 8. run python script that has pyspark session that will readstream from topic1, put in dataframe, parse, and put in topic2

python3 SparkCluster.py


---Terminal window 6 (start logstash) ----

### 9.Add "logstash-reddit.conf" to your logstash folder.

Example:
logstash-8.13.1/config/logstash-reddit.conf

### 10. Now go to your logstash-8.13.1 directory

Example:
cd logstash-8.13.1


### 11. Start logstash with provided config file:

bin/logstash -f config/logstash-reddit.conf

---Terminal window 7 (start elasticsearch) ----

### 12. navigate to elasticsearch directory

Example:
cd elasticsearch-8.13.1

### 13. Start elasticsearch 
(Note: make sure xpack.ml.enabled = false in the elasticsearch.yml in config folder)
(Note: If on MAC OS, you may have to go to settings -> privacy & security -> allow the application to run "open anyways" due to unidentified developer)

bin/elasticsearch

---Terminal window 8 (start kibana) ----

### 14. navigate to kibana directory
cd kibana-8.13.1

bin/kibana

--- Visualize The Reddit Data on Kibana ----


### 15. Go to your web browser and put the following in the search bar

http://localhost:5601/app/home#/

### 16. Click on discover to see the incoming data


YOU ARE DONE!


----------------------------------------------
## Other Useful Kafka Commands:

#### READ FROM TOPIC:
bin/kafka-console-consumer.sh --topic topic1 --from-beginning --bootstrap-server localhost:9092

#### REMOVE TOPIC:
bin/kafka-topics.sh --delete --topic topic2 --bootstrap-server localhost:9092

#### LIST TOPICS:
./bin/kafka-topics.sh --list --bootstrap-server localhost:9092
