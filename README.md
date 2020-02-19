# ai-kafka-elasticsearch

## About
This repo is a demo of using Kafka and elasticsearch, the overall process is:
1. Write User Events to Kafka
2. Consume the Events and send that to elasticsearch.
3. Monitor the Events from Kibana

Test Version:
- Kafka: 2.12-2.4.0
- Elastic Stack: 7.6.0

## Start Kafka

Start zookeeper in docker
```
docker run --rm -d --name zookeeper \
-p 2181:2181 \
digitalwonderland/zookeeper
```

Start kafka in docker with a topic 'user_log'
```
docker run --rm -d --name kafka \
--link zookeeper -p 9092:9092 \
-e KAFKA_ADVERTISED_HOST_NAME=192.168.56.107 \
-e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 \
-e KAFKA_ADVERTISED_PORT=9092 \
-e KAFKA_BROKER_ID=1 \
-e KAFKA_CREATE_TOPICS="user_log" \
wurstmeister/kafka:2.12-2.4.0
```


## Start elasticsearch + Kibana

Start elasticsearch in docker
```
docker run --rm -d --name elasticsearch \
-p 9200:9200 -p 9300:9300 \
-e "discovery.type=single-node" \
docker.elastic.co/elasticsearch/elasticsearch:7.6.0
```

Start kibana in docker
```
docker run --rm -d --name kibana \
--link elasticsearch:elasticsearch -p 5601:5601 \
docker.elastic.co/kibana/kibana:7.6.0
```
## Data file

The data file comes from Alibaba Tianchi, which contains over 10 millions of records. 

Download from: to be updated.

Example records:
```
user_id,item_id,behavior_type,user_geohash,item_category,time
98047837,232431562,1,,4245,2014-12-06 02
97726136,383583590,1,,5894,2014-12-09 20
98607707,64749712,1,,2883,2014-12-18 11
98662432,320593836,1,96nn52n,6562,2014-12-06 10
98145908,290208520,1,,13926,2014-12-16 21
```

## Sender

Use pandas to process the csv data file (the data file is over 500 MB), then use confluent_kafka client api (better performance than kafka-python) to send each records to a Kafka Topic


## Consumer

There are many ways to consume the messages and send that to elasticsearch. Here, I have listed 3 options:

- Option 1: logstash

Create a logstash.conf (Under ~/pipeline/)
```
input {
        kafka {
                bootstrap_servers => "192.168.56.107:9092"
                topics => ["user_log"]
                group_id => "test-group"
                codec => "json"
                consumer_threads => 1
                decorate_events => true
        }

}

output {
        elasticsearch {
                hosts => ["192.168.56.107:9200"]
                index => "user_log"
                workers => 1
        }
}
```

Run logstash in docker
```
docker run --rm -d --name=logstash \
-v ~/pipeline/:/usr/share/logstash/pipeline/ \
--link elasticsearch:elasticsearch \
docker.elastic.co/logstash/logstash:7.6.0
```


- Option 2: Filebeat

Filebeat is more lightweight than logstash. 

Prepare a filebeat.yml (under ~/filebeat/)

```
filebeat.inputs:
- type: kafka
  hosts:
    - 192.168.56.107:9092
  topics: ["user_log"]
  group_id: "filebeat"

output.elasticsearch:
  hosts: ["192.168.56.107:9200"]

setup.kibana.host: "http://192.168.56.107:5601"
setup.kibana.dashboards.enabled: false
```

Run
```
docker run --rm -d --name=filebeat \
-v ~/filebeat/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro \
docker.elastic.co/beats/filebeat:7.6.0
```


- Option 3: Custom program.

To be updated.
